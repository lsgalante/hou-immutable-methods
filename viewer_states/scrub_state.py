import hou


class ScrubState(object):
    def __init__(self, scene_viewer, state_name):
        self.state_name = state_name
        self.scene_viewer = scene_viewer
        self._base_x = self._base_frame = None

    def onGenerate(self, kwargs):
        self.scene_viewer.setPromptMessage(
            "Drag left/right to scrub along timeline"
        )

    def onExit(self, kwargs):
        self.scene_viewer.clearPromptMessage()

    def _scrub_abs(self, x):
        # Take the absolute position of the mouse pointer (as a percentage
        # of the total viewer width) and move that far along the current
        # frame range

        width, _ = self.scene_viewer.contentSize()
        pct = x / float(width)
        start_frame, end_frame = hou.playbar.frameRange()
        frame = int((end_frame - start_frame) * pct + start_frame)
        hou.setFrame(frame)

    def _scrub_rel(self, x):
        # Use the difference between the mouse pointer's current position
        # and the previous position to calculate how many frames to move
        # forward/back

        if self._base_x is not None:
            delta = int((x - self._base_x) / 10.0)
            frame = max(0, self._base_frame + delta)
            hou.setFrame(frame)
        else:
            self._base_x = x
            self._base_frame = hou.intFrame()

    def onMouseEvent(self, kwargs):
        device = kwargs["ui_event"].device()
        if device.isLeftButton():
            x = device.mouseX()
            if kwargs["mode"] == "abs":
                self._scrub_abs(x)
            elif kwargs["mode"] == "rel":
                self._scrub_rel(x)
        else:
            self._base_x = None


template = hou.ViewerStateTemplate("scrub", "Scrub", hou.objNodeTypeCategory())
template.bindFactory(ScrubState)

menu = hou.ViewerStateMenu("scrub", "Scrub")
menu.addRadioStrip("mode", "Mode", "rel")
menu.addRadioStripItem("mode", "rel", "Relative")
menu.addRadioStripItem("mode", "abs", "Absolute")
template.bindMenu(menu)
