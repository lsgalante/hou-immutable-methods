import hou
import math
from canvaseventtypes import *
import nodegraphdisplay as display
import nodegraphview as view

from importlib import reload
import extra

def createEventHandler(uievent, pending_actions):
    reload(extra)
    if extra.action(uievent):
        return None, True
    else:
        return None, False

