import hou
import viewerstate.utils as su

class State(object):

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.viewer     = scene_viewer
        self.viewport   = self.viewer.curViewport()

        self.drawable = hou.TextDrawable( scene_viewer, "my_guide" )
        self.drawable.show(True)

        self.pivot_mode = 0
        self.interval = 1

    ##

    def get_cam_vals(self):
        r = [ round(self.cam.evalParm("rx"), 3),
              round(self.cam.evalParm("ry"), 3),
              round(self.cam.evalParm("rz"), 3) ]
        t = [ round(self.cam.evalParm("tx"), 3),
              round(self.cam.evalParm("ty"), 3),
              round(self.cam.evalParm("tz"), 3) ]
        p = [ round(self.cam.evalParm("px"), 3),
              round(self.cam.evalParm("py"), 3),
              round(self.cam.evalParm("pz"), 3) ]
        pz = [ round(self.cam.evalParm("prx"), 3),
               round(self.cam.evalParm("pry"), 3),
               round(self.cam.evalParm("prz"), 3) ]
        return(r, t, p, pz)

    def get_centroid(self):
        return

    def print_cam_vals(self):
        r, t, p, pz = self.get_cam_vals()
        print("r:\n", r, "t:\n", t, "p:\n", p, "pr:\n", p)

    def rotate(self, axis, degrees):
        x = 1
        rot4 = hou.hmath.buildRotateAboutAxis(axis, degrees)
        rot3 = self.cam.rotation() * rot4.extractRotationMatrix3()
        self.cam.setRotation(rot3)

    def setAspect(self):
        self.cam.parm("resx").set(1000)
        self.cam.parm("resy").set(1000)

        size = self.viewport.size()
        ratio = size[2] / size[3]
        self.cam.parm("aspect").set(ratio)

    def setFrame(self):
        self.viewport.frameAll()

    def setHome(self):
        self.viewport.home()

    def setPivot(self):
        px = self.cam.parm("tx").eval() * -1
        py = self.cam.parm("ty").eval() * -1
        pz = self.cam.parm("tz").eval() * -1

        self.cam.parm("px").set(px)
        self.cam.parm("py").set(py)
        self.cam.parm("pz").set(pz)

    def setScale(self, change):
        scale  = self.state_parms["scale"]["value"]
        scale += change
        self.state_parms["scale"]["value"] = scale

    def zoom(self, multiplier):
        scale    = self.state_parms["scale"]["value"]
        ortho_w  = self.cam.evalParm("orthowidth")
        ortho_w += scale * multiplier
        self.cam.parm("orthowidth").set(ortho_w)

    ##
    ##

    def onDraw(self, kwargs):
        handle = kwargs["draw_handle"]

        (x, y, width, height) = self.viewer.curViewport().size()
        margin=10

        params = {
            "text"     : "[__]",
            "translate": hou.Vector3(width/2, height/2, 0),
            "origin"   : hou.drawableTextOrigin.UpperLeft,
            "margins"  : hou.Vector2(margin, -margin)
        }

        self.drawable.draw(handle, params)


    def onGenerate(self, kwargs):
        kwargs["state_flags"]["exit_on_node_select"] = False

        HUD_TEMPLATE=\
        {
            "title": "IM View",
            "rows":\
            [
                { "id": "pivot"  ,  "label": "Pivot"      , "value":    "Origin" },
                { "id": "pivot_g",  "type" : "choicegraph", "count": 2, "value": self.pivot_mode }
            ]
        }

        self.viewer.hudInfo(template=HUD_TEMPLATE)
        is_cam = 0

        for node in hou.node("/obj").children():
            if node.name() == "im_cam":
                is_cam = 1

        if is_cam == 0:
            cam = hou.node("/obj").createNode("cam")
            cam.setName("im_cam")

        self.cam = hou.node("/obj/im_cam")
        self.viewport.setCamera(self.cam)
        self.viewport.lockCameraToView(True)
        self.cam.parm("projection").set(1)
        self.setAspect()
        self.state_parms = kwargs["state_parms"]

        px = self.cam.evalParm("px")
        py = self.cam.evalParm("py")
        pz = self.cam.evalParm("pz")
        self.state_parms["pivot"]["value"] = [px, py, pz]

    def onResume(self, kwargs):
        x = 1

    def onKeyEvent(self, kwargs):
        key = kwargs["ui_event"].device().keyString()

        x_axis = hou.Vector3(1, 0, 0)
        y_axis = hou.Vector3(0, 1, 0)
        z_axis = hou.Vector3(0, 0, 1)

        if key == "Shift+h":
            tx = self.cam.evalParm("tx")
            self.cam.parm("tx").set(tx - self.interval)

        elif key == "Shift+j":
            ty = self.cam.evalParm("ty")
            self.cam.parm("ty").set(ty - self.interval)

        elif key == "Shift+k":
            ty = self.cam.evalParm("ty")
            self.cam.parm("ty").set(ty + self.interval)

        elif key == "Shift+l":
            tx = self.cam.evalParm("tx")
            self.cam.parm("tx").set(tx + self.interval)

        elif key == "Shift+g":
            self.viewer.setGroupListVisible(not self.viewer.isGroupListVisible())

        elif key == "Shift+p":

            self.pivot_mode = (self.pivot_mode + 1) % 2

            mode_label = ""
            if self.pivot_mode == 0:
                mode_label = "Origin"
            else:
                mode_label = "Oo"

            updates = {
                "pivot"  : {"value": mode_label},
                "pivot_g": {"value": self.pivot_mode}
            }
            self.viewer.hudInfo(hud_values=updates)

        elif key == "h":
            ry = self.cam.parm("ry").eval()
            ry = ry%360
            self.cam.parm("ry").set(ry + 10)

        elif key == "j":
            rx = self.cam.parm("rx").eval()
            rx = rx%360
            self.cam.parm("rx").set(rx - 10)

        elif key == "k":
            rx = self.cam.parm("rx").eval()
            rx = rx%360
            self.cam.parm("rx").set(rx + 10)

        elif key == "l":
            ry = self.cam.parm("ry").eval()
            ry = ry%360
            self.cam.parm("ry").set(ry - 10)


        elif key == "f":
            self.viewport.frameAll()
        elif key == "2":
            self.reset(x_axis, 90)
        elif key == "3":
            self.reset(y_axis, 90)


        elif key == "-":
            self.zoom(1)
        elif key == "=":
            self.zoom(-1)

        elif key == "Shift+-":
            self.setScale(-5)
        elif key == "Shift+=":
            self.setScale(5)

        key = None
        # return False if the event is not consumed
        return False


    def onMenuAction(self, kwargs):
        x = 1
        menu_item = kwargs["menu_item"]

        if menu_item == "reset":
            self.cam.parm("tx").set(0)
            self.cam.parm("ty").set(0)
            self.cam.parm("tz").set(100)

            self.cam.parm("rx").set(0)
            self.cam.parm("ry").set(0)
            self.cam.parm("rz").set(0)

            self.cam.parm("px").set(0)
            self.cam.parm("py").set(0)
            self.cam.parm("pz").set(-100)

        elif menu_item == "set_home":
            self.setHome()

        elif menu_item == "set_frame":
            self.setFrame()

        elif menu_item == "set_pivot":
            self.setPivot()

        elif menu_item == "print_cam_vals":
            self.printCamVals()
