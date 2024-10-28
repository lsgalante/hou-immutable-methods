import hou, labutils, math, os
from canvaseventtypes import *
import nodegraphdisplay as display
import nodegraphview as view
from PySide2.QtCore import Qt, QRect
from PySide2.QtGui import QColor, QCursor, QPen, QPixmap
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView


def action(uievent):

    if isinstance(uievent, ContextEvent):
        x = 1

    if isinstance(uievent, KeyboardEvent) and\
        uievent.eventtype == 'keyhit':

#        print(uievent.key)

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

        # Move node left
        if key == 'Ctrl+Shift+H':
            if round ((x%1), 1) <= 0.5:
                x = math.floor(x) - 0.5
            else:
                x = math.ceil(x) - 0.5
        # Layout nodes
        elif key == "Ctrl+Shift+A":
            node.parent().layoutChildren(horizontal_spacing=5, vertical_spacing=5), 
        # Move node down
        elif key == 'Ctrl+Shift+J':
            if round ((y%1), 2) > 0.85:
                y = math.ceil(y) - 0.15
            else:
                y = math.floor(y) - 0.15
        # Move node up
        elif key == 'Ctrl+Shift+K':
            if round((y%1), 2) < 0.85:
                y = math.floor(y) + 0.85
            else:
                y = math.ceil(y) + 0.85
        # Move node right
        elif key == 'Ctrl+Shift+L':
            if round( (x%1), 1) >= 0.5:
                x = math.ceil(x) + 0.5
            else:
                x = math.floor(x) + 0.5
        # Place dot
        elif key == "Shift+D":
            selected = hou.selectedNodes()
            if len(selected) == 1:
                context = node.parent()
                dot = context.createNetworkDot()
                dot.setInput(node)
                cursor_pos = editor.cursorPosition()
                dot.setPosition(cursor_pos)
        elif key == "Shift+G":
            if editor.getPref("gridmode") == "0":
                editor.setPref("gridmode", "2")
            else:
                editor.setPref("gridmode", "0")
        # Pan left
        elif key == 'H': view_xform[0] = -view_step * zoom_amt
        # Pan down
        elif key == 'J': view_xform[1] = -view_step * zoom_amt
        # Pan up
        elif key == 'K': view_xform[1] = view_step * zoom_amt
        # Pan right
        elif key == 'L': view_xform[0] = view_step * zoom_amt
        # Change update mode
        elif key == "M":
            if hou.updateModeSetting() == hou.updateMode.Manual:
                hou.setUpdateMode(hou.updateMode.AutoUpdate)
            else:
                hou.setUpdateMode(hou.updateMode.Manual)

        node.setPosition( (x, y) )
        xform = hou.Vector2(view_xform[0], view_xform[1])
        visible_bounds = editor.visibleBounds()
        visible_bounds.translate(xform)
        editor.setVisibleBounds(visible_bounds)

        # Draw outline
        draw_outline(uievent)


def draw_outline(uievent):
    editor = uievent.editor
    image = hou.NetworkImage()
    image.setPath('$HIP/drawings/bg.png')
    image.setRect(hou.BoundingRect(0, 0, 1, 1))

    screen_space = editor.screenBounds()
    visible_items = editor.networkItemsInBox(screen_space.min(), screen_space.max(), for_select=True)
    images = []
    for item in visible_items:
        pos = item[0].position()
        pos = hou.Vector2(pos.x()-0.025, pos.y()-0.35)
        pos2 = hou.Vector2(pos.x()+1.05, pos.y()+1)
        image.setRect(hou.BoundingRect(pos, pos2))
        images.append(image)

    editor.setBackgroundImages([image])
