import re
import subprocess
import datetime
from weather import parse_date,str_date,parse_datetime,str_datetime

# Interface to communicate with the bash
class TodoAPI:

    # Retrieve all tasks
    def get_all(self):
        def query(cmd):
            text = self.execute(cmd)
            return [self.get_task(line.split("|")[0].strip()) for line in text.strip().split("\n") if len(line.strip())>0]
        tasks = query("todo --flat")
        d = lambda x,y: y if x is None else x
        dt = lambda t: t.get_deadline()
        for task in query("todo future"):
            indexes = [i for i, t in enumerate(tasks) if d(t.get_priority(),1)<=d(task.get_priority(),1) and (not dt(t) or (dt(task) and dt(t)>=dt(task)))]
            tasks.insert(indexes[0] if indexes else len(tasks),task)
        return tasks+query("todo search '' --done")

    # Execute todo search commands
    def search(self,cmds):
        tasks = []
        for cmd in cmds:
            text = self.execute(cmd)
            tasks += [self.get_task(line.split("|")[0].strip()) for line in text.strip().split("\n") if len(line.strip())>0]
        d = lambda x,y: y if x is None else x
        max_delta = datetime.timedelta(days=datetime.datetime.now().year * 365.2422)
        key = lambda t: (-d(t.get_priority(),1),(t.get_deadline()-datetime.datetime.now() if t.get_deadline() else max_delta),t.get_id())
        return sorted(tasks,key=key)

    # Retrieve and parse task into Python object
    def get_task(self,id):
        text = self.execute(f"todo task {id}")
        task = Task(id)
        lines = text.strip().split("\n")
        for i,line in enumerate(lines):
            line = line.strip()
            if line.lower().startswith("created:"):
                task.set_created_at(parse_datetime(line.lower()[len("created:"):].strip().split(" ")[0]))
            if line.lower().startswith("start:"):
                start = line.lower()[len("start:"):].strip()
                if start!="@created":
                    task.set_start(parse_datetime(start))
            if line.lower().startswith("status:"):
                task.set_status(line.lower()[len("status:"):].strip())
            if i==len(lines)-3:
                tmp = line
                if "#" in line:
                    tmp, context = line.split("#")
                    task.set_context(Context(context.strip()))
                if "★" in line:
                    tmp,priority = tmp.split("★")
                    task.set_priority(int(priority.strip()))
                if "⌛" in line:
                    task.set_deadline(parse_datetime(tmp.split("⌛")[1].strip())+datetime.timedelta(hours=1))
            if i==len(lines)-1:
                task.set_title(line.strip())
        return task
    # Execute bask command
    def execute(self,commands):
        if TodoAPI.intercepting is not None:
            TodoAPI.intercepting.append(commands)
            if not TodoAPI.intercepting[0]:
                return None

        p = subprocess.run(["bash", "-c", commands], capture_output=True, text=True)
        out = p.stdout
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', out)

    intercepting = None

    @staticmethod
    def start_interception(commit):
        TodoAPI.intercepting = [commit]

    @staticmethod
    def end_interception():
        intercepting = TodoAPI.intercepting[1:]
        TodoAPI.intercepting = None
        return intercepting

# Represent a task as Python object
class Task:

    def __init__(self,id=None,title=None,start=None,deadline=None,priority=1,context=None,period=None,status=None,created_at=None):
        self.api = TodoAPI()
        self.id = id
        self.title = title
        self.start = start
        self.deadline = deadline
        self.priority = priority
        self.context = context
        self.period = period
        self.status = status
        self.created_at = created_at

    def get_id(self):
        return self.id
    def set_id(self,id):
        self.id = id
    def get_title(self):
        return self.title
    def set_title(self,title):
        self.title = title
    def get_start(self):
        return self.start
    def set_start(self,start):
        self.start = start
    def get_status(self):
        return self.status
    def set_status(self,status):
        self.status = status
    def get_deadline(self):
        return self.deadline
    def set_deadline(self,deadline):
        self.deadline = deadline
    def get_context(self):
        return self.context
    def set_context(self,context):
        self.context = context
    def set_period(self,period):
        self.period = period
    def get_period(self):
        return self.period
    def get_priority(self):
        return self.priority
    def set_priority(self,priority):
        self.priority = priority
    def get_created_at(self):
        return self.created_at
    def set_created_at(self,created_at):
        self.created_at = created_at
    def save(self):
        title = '"'+self.get_title()+'"'
        start = self.get_start()
        deadline = self.get_deadline()
        priority = str(self.get_priority()) if self.get_priority() else None
        context = self.get_context()
        period = self.get_period()
        start = "" if not start else "--start '"+str_datetime(start)+"'"
        deadline = "" if not deadline else "--deadline '"+str_datetime(deadline)+"'"
        priority = "" if not priority else "--priority "+priority
        context = "" if not context else "--context "+context.get_name()
        period = "" if not period else "--period "+period
        if self.id:
            return self.api.execute(f"todo task {self.id} --title {title} {start} {deadline} {priority} {context} {period}")
        return self.api.execute(f"todo add {title} {start} {deadline} {priority} {context} {period}")
    def done(self):
        return self.api.execute(f"todo done {self.id}")
    def remove(self):
        return self.api.execute(f"todo rm {self.id}")
    def __repr__(self):
        return f"{self.id} {self.title} {self.start} {self.deadline} {self.priority} {self.context} {self.status} {self.created_at}"
    def json(self):
        return {
            "id": self.get_id(),
            "title": self.get_title(),
            "start": str_datetime(self.get_start()) if self.get_start() else None,
            "deadline": str_datetime(self.get_deadline()) if self.get_deadline() else None,
            "priority": self.get_priority(),
            "context": self.get_context().json() if self.get_context() else None,
            "status": self.get_status()
        }
# Represent a context as Python object
class Context:

    def __init__(self,name):
        self.api = TodoAPI()
        self.name = name
    def get_name(self):
        return self.name
    def move(self,context):
        return self.api.execute(f"todo mv {self.name} {context.name}")
    def remove(self):
        return self.api.execute(f"todo rmctx {self.name} --force")
    def get_all(self):
        text = self.api.execute(f"todo search '' -c {self.name}")
        return sorted([self.api.get_task(line.split("|")[0].strip()) for line in text.strip().split("\n")],key=lambda t: t.get_priority() or 1)
    def __repr__(self):
        return f"{self.name}"
    def json(self):
        return {
            "name": self.get_name()
        }