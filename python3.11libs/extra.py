import hou
import math
from canvaseventtypes import *
import nodegraphdisplay as display
import nodegraphview as view


def action(uievent):

    if isinstance(uievent, ContextEvent):
        x = 1

    if isinstance(uievent, KeyboardEvent) and\
        uievent.eventtype == 'keyhit':

        editor       = uievent.editor
        node         = editor.currentNode()
        x            = node.position()[0]
        y            = node.position()[1]
        key          = uievent.key
        screen_size  = editor.screenBounds().size()
        visible_size = editor.visibleBounds().size()
        zoom_amt     = visible_size[0] / screen_size[0]
        view_xform   = [0, 0]
        view_step    = 160

        print (key)

        if key == 'Ctrl+Shift+H':          # Move Node Left
            if round ((x%1), 1) <= 0.5:
                x = math.floor(x) - 0.5
            else: x = math.ceil(x) - 0.5

        elif key == 'Ctrl+Shift+J':        # Move Node Down
            if round ((y%1), 2) > 0.85:
                y = math.ceil(y) - 0.15
            else: y = math.floor(y) - 0.15

        elif key == 'Ctrl+Shift+K':        # Move Node Up
            if round((y%1), 2) < 0.85:
                y = math.floor(y) + 0.85
            else: y = math.ceil(y) + 0.85

        elif key == 'Ctrl+Shift+L':        # Move Node Right
            if round( (x%1), 1) >= 0.5:
                x = math.ceil(x) + 0.5
            else: x = math.floor(x) + 0.5

        elif key == "Shift+D":             # Insert Dot
            selected = hou.selectedNodes()
            if len(selected) == 1:
                context = node.parent()
                dot     = context.createNetworkDot()
                dot.setInput (node)
                cursor_pos = editor.cursorPosition()
                dot.setPosition(cursor_pos)

        elif key == "Shift+G":
            if editor.getPref("gridmode") == "0":
                editor.setPref("gridmode", "2")
            else:
                editor.setPref("gridmode", "0")

        elif key == 'H':                   # Pan Left
            view_xform[0] = -view_step * zoom_amt
        elif key == 'J':                   # Pan Down
            view_xform[1] = -view_step * zoom_amt
        elif key == 'K':                   # Pan Up
            view_xform[1] = view_step * zoom_amt
        elif key == 'L':                   # Pan Right
            view_xform[0] = view_step * zoom_amt

        elif key == "M":                   # Toggle Update Mode
            if hou.updateModeSetting() == hou.updateMode.Manual:
                hou.setUpdateMode (hou.updateMode.AutoUpdate)

            else:
                hou.setUpdateMode (hou.updateMode.Manual)

        node.setPosition ((x, y))
        visible_bounds = editor.visibleBounds ()
        visible_bounds.translate (hou.Vector2(view_xform[0], view_xform[1]))
        editor.setVisibleBounds (visible_bounds)
