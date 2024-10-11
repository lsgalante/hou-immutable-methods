import hou
from canvaseventtypes import *
import nodegraphdisplay as display
import nodegraphview as view


def action(uievent):
    if isinstance(uievent, KeyboardEvent) and\
        uievent.eventtype == 'keyhit':
        editor = uievent.editor
        node = editor.currentNode()
        parent = node.parent()
        key = uievent.key
        step_x = 5
        step_y = 5

        if key == "A":
            parent.layoutChildren(horizontal_spacing=step_x, vertical_spacing=step_y)
