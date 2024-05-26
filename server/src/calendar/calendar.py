import os
PARENT_DIR = os.path.dirname(os.path.realpath(__file__))

import re
import json
import datetime

from .todo_api import TodoAPI
from .executor import Executor,parse_datetime,str_datetime,parse_date,str_date

prompt_template = open(PARENT_DIR+"/prompt_template.txt").read()


class Calendar:
    def __init__(self,llm_api):
        self.llm_api = llm_api
        self.executor = Executor()

    def get_augmented_prompt(self,query,system_prompt,contexts):
        # Augment the prompt template with correct dates, times and list of contexts
        prompt = (prompt_template.replace("{instruction}",query)
                  .replace("{context_list}",", ".join(contexts))
                  .replace("2024-04-01 00:00:00",datetime.datetime.now().strftime('%B %d, %Y at %H:%M')))
        matches = re.findall(r'\b(\d{4}-\d{1,2}-\d{1,2}(\s+\d{1,2}:\d{1,2}(:\d{1,2})?)?)\b', prompt)
        for m in sorted(matches,key=lambda x:len(x[0]),reverse=True):
            date_time,has_time = self._recalibrate_datetime(m[0])
            prompt = prompt.replace(m[0],date_time if has_time else str_date(parse_date(date_time)))
        prompt = (prompt.replace("{friday}",str_date(parse_date("Friday")))
                  .replace("{in_one_hour}", str_datetime(datetime.datetime.now()+datetime.timedelta(hours=1))))
        return prompt
    async def process(self,query,system_prompt,commit=True):
        contexts = list({t.context.name:None for t in TodoAPI().get_all() if t.context}.keys())
        augmented_prompt = self.get_augmented_prompt(query,system_prompt,contexts=contexts)
        # Prompt the LLM
        response = self.llm_api.generate(augmented_prompt,options={"temperature":.9,"top_p":.9,"max_gen_len":256})
        yield json.dumps({"status":"ok","type":"model","payload":{"response":response}})
        # Convert LLM's response to JSON
        operations = self.parse(response)
        for operation in operations:
            # Check the validity of the JSON
            valid,error_message = self.validate(operation)
            if not valid:
                yield json.dumps({"status":"error","type":"tasks","payload": {"type":"invalid_operation","message":f"{error_message} Please rephrase your query!"}})
            else:
                try:
                    # Replace contexts extracted from query with correct contexts if they exists
                    operation = self.refine(operation,contexts)
                    yield json.dumps({"status":"ok","type":"operation","payload":operation})
                    # Translate the JSON to bash commands and execute them
                    async for message in self.executor.execute(operation,commit):
                        yield message
                except Exception as e:
                    yield json.dumps({"status":"error","type":"tasks","payload":{"type":"invalid_execution","message":"No executable operation can be inferred from your query. Please rephrase it!"}})
                    print(e)

        yield json.dumps({"status":"done","type":"tasks","payload":None})

    def refine(self,operation,contexts):
        if operation["context"]:
            tmp = []
            for c in operation["context"]:
                context_names = [(context,len(c)/len(context)) for context in contexts if re.search("^"+c,context)]
                tmp += [context for context,_  in sorted(context_names,key=lambda x: x[1],reverse=True)]
            operation["context"] = tmp
        return operation
    def _recalibrate_datetime(self,start):
        has_time = start and re.search(r'\b(\d{1,2}:\d{1,2}(:\d{1,2})?)\b', start) is not None
        start = parse_datetime(start) if start else None
        start = (start+(datetime.datetime.now().date()-parse_datetime("2024-04-01 00:00:00").date())) if start else None
        if not has_time and start:
            start -= datetime.timedelta(hours=start.hour,minutes=start.minute,seconds=start.second)
        return (str_datetime(start) if start else None,has_time)

    def parse(self,text):
        schema = {
            "action": lambda x: x.lower(),
            "id": lambda x: list(map(int,filter(lambda x: len(x)>=1,("".join(c for c in x.lower() if c.isnumeric() or c==",")).split(",")))) or None,
            "title": None,
            "outdoor-related": lambda x: x.lower()=="true",
            "start": lambda x: x.lower(),
            "deadline": lambda x: x.lower(),
            "priority": lambda x: x.lower(),
            "context": lambda x: list(filter(lambda x: x!="all",map(lambda c: c.strip(),x.lower().split(",")))),
            "output context": lambda x: x.lower(),
            "done": lambda x: x.lower()=="true",
            "period": lambda x: x.lower(),
        }
        operations = []
        actions = self.parameters_by_action.keys()
        operation_texts = []
        start = False
        for line in text.split("\n"):
            line = line.strip()
            if len(line)==0:
                continue
            if any(line.lower().strip().startswith(action) for action in actions):
                operation_texts.append("--action "+line)
                start = True
            elif start:
                break
        for operation_text in operation_texts:
            operation = {}
            is_command = False
            for line in operation_text.replace("--","\n").split("\n"):
                line = line.strip()
                if len(line)==0:
                    continue
                keys = [k for k,v in schema.items() if line.lower().strip().startswith(k)]
                if keys:
                    is_command = True
                    arg = line[len(keys[0]):].strip()
                    if arg and arg.lower()!="none":
                        operation[keys[0]] = schema[keys[0]](arg) if schema[keys[0]] else arg
                elif is_command:
                    break
            operations.append({k:operation.get(k,None) for k,v in schema.items()})
        return operations

    parameters_by_action = {
        "show": ["id","title","start","deadline","priority","context"],
        "add": ["title","outdoor-related","start","deadline","priority","context","period"],
        "remove": ["id","title","start","deadline","priority","context"],
        "merge": ["context","output context"],
        "move":  ["id","title","priority","context","output context","done"],
        "prioritize": ["id","title","start","deadline","priority","context"],
        "mark": ["id","title","start","deadline","priority","context"],
    }

    def validate(self,operation):
        rules = {
            "action": None,
            "id": lambda x: len(x)>=1,
            "title": lambda x: len(x)>=1,
            "outdoor-related": lambda x: isinstance(x,bool),
            "start": lambda x: not not re.search(r'\b\d{4}-\d{1,2}-\d{1,2}(\s+\d{1,2}:\d{1,2}(:\d{1,2})?)?\b', x),
            "deadline": lambda x: not not re.search(r'\b\d{4}-\d{1,2}-\d{1,2}(\s+\d{1,2}:\d{1,2}(:\d{1,2})?)?\b', x),
            "priority": lambda x: any(e in x for e in ["high","maximum","low","minimum"]) or x.isnumeric(),
            "context": lambda x: isinstance(x,list),
            "output context": lambda x: len(x)>=1,
            "done": lambda x: isinstance(x,bool),
            "period": lambda x: x[:-1].isnumeric() and any(x.endswith(c) for c in ["s","m","h","d","w"]),
        }

        defaultMessage = "No valid operation can be inferred from your query."
        if operation["action"] not in ["show","add","remove","merge","move","prioritize","mark"]:
            return False,f'"{operation["action"]}" operation is not supported.'

        for action,parameters in self.parameters_by_action.items():
            for param in parameters:
                if operation[param] is not None and not rules[param](operation[param]):
                    return False,defaultMessage
        return True,None