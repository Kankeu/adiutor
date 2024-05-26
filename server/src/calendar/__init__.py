import os
import sys
PARENT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(PARENT_DIR)

from .calendar import  Calendar
from .todo_api import TodoAPI
from .weather import Weather