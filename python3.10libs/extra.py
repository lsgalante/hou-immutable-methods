import hou
import math
from canvaseventtypes import *
import nodegraphdisplay as display
import nodegraphview as view


def action(uievent):
    if isinstance(uievent, ContextEvent):
        # print(uievent)
        x = 1

    if isinstance(uievent, KeyboardEvent) and \
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


        if key == 'Ctrl+Shift+H':          # Node Left
            if round( (x%1), 1 ) <= 0.5:
                  x = math.floor( x )  - 0.5
            else: x = math.ceil(  x )  - 0.5
        elif key == 'Ctrl+Shift+J':        # Node Down
            if round( (y%1 ), 2 ) > 0.85:
                  y = math.ceil(  y ) - 0.15
            else: y = math.floor( y ) - 0.15
        elif key == 'Ctrl+Shift+K':        # Node Up
            if round( ( y%1 ), 2 ) < 0.85:
                  y = math.floor( y ) + 0.85
            else: y = math.ceil(  y ) + 0.85
        elif key == 'Ctrl+Shift+L':        # Node Right
            if round( ( x%1 ), 1 ) >= 0.5:
                  x = math.ceil(  x ) + 0.5
            else: x = math.floor( x ) + 0.5
        
        elif key == 'H':                            # View Left
            view_xform[0] = -view_step * zoom_amt
        elif key == 'J':                            # View Down
            view_xform[1] = -view_step * zoom_amt
        elif key == 'K':                            # View Up
            view_xform[1] =  view_step * zoom_amt
        elif key == 'L':                            # View Right
            view_xform[0] =  view_step * zoom_amt

        elif key == "M":
            update_mode = hou.updateModeSetting()
            if update_mode == hou.updateMode.AutoUpdate:
                hou.setUpdateMode(hou.updateMode.Manual)
            elif update_mode == hou.updateMode.OnMouseUp:
                hou.setUpdateMode(hou.updateMode.Manual)
            elif update_mode == hou.updateMode.Manual:
                hou.setUpdateMode(hou.updateMode.AutoUpdate)
        ###

        # print(node.position())
        node.setPosition( (x, y) )

        visible_bounds = editor.visibleBounds()
        visible_bounds.translate(hou.Vector2(view_xform[0], view_xform[1]))
        editor.setVisibleBounds(visible_bounds)
