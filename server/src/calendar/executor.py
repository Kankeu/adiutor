import json
import datetime

from todo_api import TodoAPI,Task,Context,parse_date,str_date,parse_datetime,str_datetime
from weather import Weather, Forecast

class Executor:

    def __init__(self):
        self.todo_api = TodoAPI()
        self.weather = Weather()

    async def execute(self,operation,commit):
        contains = lambda x,y: x is None or (isinstance(y,str) and (x in y))
        all_tasks = self.todo_api.get_all()
        # Prepare the data
        operation["start"] = parse_datetime(operation["start"]) if operation["start"] else None
        operation["deadline"] = parse_datetime(operation["deadline"]) if operation["deadline"] else None
        # Sometimes the model uses context instead  of output context, so this should correct that
        if operation["action"] == "move" and operation["context"] and not operation["output context"]:
            operation["output context"] = operation["context"][0]
            operation["context"] = None

        if operation["action"] == "add" and operation["start"] and not operation["deadline"]:
            operation["deadline"] = operation["start"]
            operation["start"] = None

        # Retrieve tasks and filter them
        cmds = [self._search(operation|{"context":context}) for context in (operation["context"] or [])] if operation["context"] else [self._search(operation|{"context":None})]
        tasks = self.todo_api.search(cmds)

        tasks = [t for t in tasks if not operation["start"] or (t.get_start() and operation["start"]<=t.get_start())]
        tasks = [t for t in tasks if not operation["deadline"] or (t.get_deadline() and operation["deadline"]>=t.get_deadline())]

        TodoAPI.start_interception(commit)

        if operation["action"]=="add":
            async for message in self._add(all_tasks,contains,operation):
                yield message
        # Set the numerical value of the priority
        if operation["action"]=="prioritize":
            if not operation["priority"] or not operation["priority"].isnumeric():
                is_max = contains("highest",operation["priority"]) or contains("maximum",operation["priority"])
                operation["priority"] = 99 if is_max else max([t.get_priority() for t in all_tasks if t.get_priority()],default=1)+1
            else:
                operation["priority"] = int(operation["priority"])

        elif operation["action"] in ["move","mark","merge"] and isinstance(operation["priority"],str):
            if contains("high",operation["priority"]) or contains("maximum",operation["priority"]):
                tasks = sorted(tasks,key=lambda t: t.get_priority(), reverse=True)
                if tasks:
                    tasks = [t for t in tasks if t.get_priority()>=min(90, tasks[0].get_priority())]
            if contains("low",operation["priority"]) or contains("minimum",operation["priority"]):
                tasks = sorted(tasks,key=lambda t: t.get_priority(), reverse=False)
                if tasks:
                    tasks = [t for t in tasks if t.get_priority()<=tasks[0].get_priority()]
            operation["priority"] = None
        # Filter by position
        tasks = [t for i,t in enumerate(tasks) if operation["id"] is None or i+1 in operation["id"]]
        if operation["action"]=="remove":
            for task in tasks:
                task.remove()

        if operation["action"]=="mark":
            for task in tasks:
                if operation["done"]:
                    task.done()

        if operation["action"] in ["prioritize","move","merge"]:
            for i,task in enumerate(tasks):
                if operation["priority"]:
                    task.set_priority(operation["priority"])
                if operation["output context"]:
                    task.set_context(Context(operation["output context"]))
                task.save()
        commands = TodoAPI.end_interception()
        yield json.dumps({"status":"ok","type":"tasks","payload":{"action":"execute","commands":[cmd.strip() for cmd in cmds]+commands}})

        all_tasks = tasks if operation["action"]=="show" else self.todo_api.get_all()
        action = "show" if operation["action"]=="show" else "show_all"

        yield json.dumps({"status":"ok","type":"tasks","payload":{"action":action,"tasks":[t.json() for t in all_tasks]}})

    def _search(self,operation):
        query = operation["title"] or ""
        context = "--context "+operation["context"] if operation["context"] else ""
        done = "--done" if operation["done"] and operation["action"]!="mark" else "--undone"
        return f"todo search '{query}' {context} {done}"

    async def _add(self,all_tasks,contains,operation):
        if operation["start"] and operation["deadline"]:
            # Search a free slot and postpone the proposed one if there is a collusion
            (operation["start"],operation["deadline"]),postponed = self._get_free_slot(all_tasks,operation["start"],operation["deadline"])
            if postponed:
                yield json.dumps({"status":"ok","type":"tasks","payload":{"action":"postpone","response":f"The task has been postponed to the free timeslot {str_datetime(operation['start'])} and {str_datetime(operation['deadline'])}"}})

        if operation["priority"] and (contains("high",operation["priority"]) or contains("maximum",operation["priority"])):
            operation["priority"] = max([t.get_priority() for t in all_tasks if t.get_priority()],default=1)+1
        yield json.dumps({"status":"ok","type":"tasks","payload":{"action":"weather_checking","response":"Checking weather forecasts..."}})
        # Retrieve weather forecasts for today and the next two days
        forecasts: list[Forecast] = await Weather().get("Kaiserslautern")
        yield json.dumps({"status":"ok","type":"tasks","payload":{"action":"forecast","forecasts":[f.json() for f in forecasts]}})
        # A good day is a day without an adverse weather at any hour
        good_days:list[Forecast] = [df for df in forecasts if any(not hf.get_adverse_weather() for hf in df.get_hourly_forecasts())]

        deadline = operation.get("deadline",datetime.datetime.today)

        def nearest_good_day(deadline,after=False):
            for df in good_days:
                if (df.get_date()>deadline if after else df.get_date()<=deadline):
                    return df.get_date()
            return None

        # Postpone ff it is an outdoor-related activity with a specific time slot
        if operation["outdoor-related"] and operation["start"] and operation["deadline"] and nearest_good_day(deadline.date()):
            next_good_day = nearest_good_day(deadline.date(),after=True)
            # Since the weather forecasts cover only 3 days, the fourth day should be taken by default if no good is found
            next_good_day = next_good_day if next_good_day else forecasts[-1].get_date() +  datetime.timedelta(days=1)
            day_shift = datetime.timedelta(days=(next_good_day-deadline.date()).days)
            operation["deadline"] = deadline + day_shift
            if operation["start"]:
                operation["start"] += day_shift
            yield json.dumps({"status":"ok","type":"tasks","payload":{"action":"postpone","response":f"Due to bad weather, the deadline has been postponed until {str_date(next_good_day)}"}})
        task = Task(title=operation["title"],start=operation["start"],deadline=operation["deadline"],priority=operation["priority"],context=Context(operation["context"][0]) if operation["context"] else None,period=operation["period"])
        task.save()

    # Check whether the time slot (start-deadline) is free. If not, postpone until a free slot is found.
    def _get_free_slot(self,all_tasks,start,deadline):
        postponed = False
        duration = deadline-start
        all_tasks = [t for t in all_tasks if t.get_start() and t.get_deadline()]
        while (conflicts := [(t.get_start(),t.get_deadline()) for t in all_tasks if t.get_start()<= start <t.get_deadline() or t.get_start()< deadline <=t.get_deadline()]):
            _,start = sorted(conflicts,key=lambda t: t[1],reverse=True)[0]
            deadline = start + duration
            postponed = True
        return (start,deadline),postponed
