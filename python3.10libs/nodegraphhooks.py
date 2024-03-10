import hou
from canvaseventtypes import *
import nodegraphdisplay as display
import nodegraphview as view

def createEventHandler(uievent, pending_actions):
    if isinstance(uievent, KeyboardEvent) and \
      uievent.eventtype == 'keyhit':
      # This is a key hit event.
        editor = uievent.editor
        
        stepsize = 1
        if uievent.key == 'H':
            bounds = editor.visibleBounds()
            bounds.translate(hou.Vector2(stepsize * -1, 0))
            editor.setVisibleBounds(bounds)

        elif uievent.key == 'J':
            bounds = editor.visibleBounds()
            bounds.translate(hou.Vector2(0, stepsize * -1))
            editor.setVisibleBounds(bounds)

        elif uievent.key == 'K':
            bounds = editor.visibleBounds()
            bounds.translate(hou.Vector2(0, stepsize))
            editor.setVisibleBounds(bounds)

        elif uievent.key == 'L':
            bounds = editor.visibleBounds()
            bounds.translate(hou.Vector2(stepsize, 0))
            editor.setVisibleBounds(bounds)

        elif uievent.key == "Shift+H":
            pane = editor.pane()
            frac = pane.getSplitFraction()
            pane.setSplitFraction(frac + 0.1)

        elif uievent.key == "Shift+L":
            pane = editor.pane()
            frac = pane.getSplitFraction()
            pane.setSplitFraction(frac - 0.1)


        elif display.setKeyPrompt(editor, uievent, 'h.pane.wsheet.jump'):
        # Check for the 'dive in' key.
            pos = uievent.mousepos
            # Find the node under the mouse.
            items = editor.networkItemsInBox(pos, pos, for_select = True)
            for (item, name, index) in items:
                if isinstance(item, hou.Node) and item.isNetwork():
                    view.diveIntoNode(editor, item)
                    break
            # We handled this event, but don't need to return an event handler
            # because this is a one-off event. We don't care what happens next.
            return None, True


    return None, False
