import hou
import viewerstate.utils as su
import pprint


class State(object):
    HUD_TEMPLATE = {
        "title": "IM View",
        "rows":\
        [
            { "id": "pivot"  ,  "label": "Pivot"      , "value":    "Origin" },
            { "id": "pivot_g",  "type" : "choicegraph", "count": 2, "value": 0 }
        ]
    }

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.viewer     = scene_viewer

        # State variables
        self.movement_style      = "rotate"
        self.pivot_style         = "origin"
        self.enable_axis_drawble = 1
        self.interval            = 1

        # Drawables
        self.axis_drawable = hou.GeometryDrawable(
            scene_viewer = scene_viewer,
            geo_type     = hou.drawableGeometryType.Line,
            name         = "axis_drawable"
        )
        self.axis_drawable.show(True)

        self.pivot_drawable = hou.GeometryDrawable(
            scene_viewer = scene_viewer,
            geo_type     = hou.drawableGeometryType.Line,
            name         = "pivot_drawable")
        self.pivot_drawable.show(True)

        self.parm_text_drawable = hou.TextDrawable(
            scene_viewer = scene_viewer,
            name         = "parm_text_drawable",
            params       = {})
        self.parm_text_drawable.show(True)

    ##

    def get_cam_vals(self):
        rx = round(self.cam.evalParm("rx"), 3)
        ry = round(self.cam.evalParm("ry"), 3)
        rz = round(self.cam.evalParm("rz"), 3)
        tx = round(self.cam.evalParm("tx"), 3)
        ty = round(self.cam.evalParm("ty"), 3)
        tz = round(self.cam.evalParm("tz"), 3)
        px = round(self.cam.evalParm("px"), 3)
        py = round(self.cam.evalParm("py"), 3)
        pz = round(self.cam.evalParm("pz"), 3)
        prx = round(self.cam.evalParm("prx"), 3)
        pry = round(self.cam.evalParm("pry"), 3)
        prz = round(self.cam.evalParm("prz"), 3)
        r = (rx, ry, rz)
        t = (tx, ty, tz)
        p = (px, py, pz)
        pr = (prx, pry, prz)
        return(r, t, p, pr)

    def get_centroid(self):
        return

    def handle_rotate(self, key):
        rot_scale = self.state_parms["rot_scale"]["value"]
        if key == "h":
            ry = self.cam.evalParm("ry") % 360
            self.cam.parm("ry").set(ry + rot_scale)
        elif key == "j":
            rx = self.cam.evalParm("rx") % 360
            self.cam.parm("rx").set(rx - rot_scale)
        elif key == "k":
            rx = self.cam.evalParm("rx") % 360
            self.cam.parm("rx").set(rx + rot_scale)
        elif key == "l":
            ry = self.cam.evalParm("ry") % 360
            self.cam.parm("ry").set(ry - rot_scale)

    def handle_translate(self, key):
        if key == "h":
            tx = self.cam.evalParm("tx")
            self.cam.parm("tx").set(tx - self.interval)
        elif key == "j":
            ty = self.cam.evalParm("ty")
            self.cam.parm("ty").set(ty - self.interval)
        elif key == "k":
            ty = self.cam.evalParm("ty")
            self.cam.parm("ty").set(ty + self.interval)
        elif key == "l":
            tx = self.cam.evalParm("tx")
            self.cam.parm("tx").set(tx + self.interval)

    def handle_xform(self, key):
        eval("self.handle_" + self.movement_style + "(key)")

    def handle_zoom(self, key):
        zoom_scale = self.state_parms["zoom_scale"]["value"]
        ortho_w = self.cam.evalParm("orthowidth")
        if key == "Shift+-":
            zoom_scale -= 1
        elif key == "Shift+=":
            zoom_scale += 1
        elif key == "-":
            ortho_w += zoom_scale
        elif key == "=":
            ortho_w -= zoom_scale
        self.state_parms["zoom_scale"]["value"] = zoom_scale
        self.cam.parm("orthowidth").set(ortho_w)

    def print_cam_vals(self):
        r, t, p, pz = self.get_cam_vals()
        print("r:\n", r, "t:\n", t, "p:\n", p, "pr:\n", p)

    def print_kwargs(self, kwargs):
        ui_event = str(kwargs["ui_event"])
        ui_event = ui_event.replace("\\n", "\n")
        del kwargs["ui_event"]
        print("\n")
        pprint.pprint(kwargs)
        print(ui_event)

    def ui_refit(self):
        self.cam.parm("resx").set(1000)
        self.cam.parm("resy").set(1000)

        size = self.viewport.size()
        ratio = size[2] / size[3]
        self.cam.parm("aspect").set(ratio)

        self.pivot_drawable.setParams({"screen_space":\
            (-50, -50, 100, 100, 100/ratio, 0)})

        self.parm_text_drawable.setParams({
        })

    def update_pivot_drawable(self):
        pivot_drawable_geo = hou.Geometry()
        circle_verb = hou.sopNodeTypeCategory().nodeVerb("circle")
        circle_verb.setParms({"scale": 1.0, "type": 1})
        circle_verb.execute(pivot_drawable_geo, [])
        self.pivot_drawable.setGeometry(pivot_drawable_geo)
        self.pivot_drawable.setParams({
            "color1": hou.Vector4(1, 0, 0, 1),
            "fade_factor": 1.0
        })

    def update_text_drawable(self):
        r, t, p, pr = self.get_cam_vals()
        self.parm_text_drawable.setParams({
            "text": "<font size=4 color=#DCB269>Pivot............" + str(p)
                + "<br>---<br>Rotation........." + str(r)
                + "<br>---<br>Translation......" + str(t)
                + "<br>---<br>Pivot Rotation..." + str(pr) + "</font>",
            "margins": hou.Vector2(20, 90),
            "multi_line": True
        })

    def view_frame(self):
        self.viewport.frameAll()

    def view_reset(self):
        self.cam.parm("tx").set(0)
        self.cam.parm("ty").set(0)
        self.cam.parm("tz").set(100)

        self.cam.parm("rx").set(0)
        self.cam.parm("ry").set(0)
        self.cam.parm("rz").set(0)

        self.cam.parm("px").set(0)
        self.cam.parm("py").set(0)
        self.cam.parm("pz").set(-100)

    def view_home(self):
        self.viewport.home()

    def set_pivot(self):
        px = self.cam.parm("tx").eval() * -1
        py = self.cam.parm("ty").eval() * -1
        pz = self.cam.parm("tz").eval() * -1

        self.cam.parm("px").set(px)
        self.cam.parm("py").set(py)
        self.cam.parm("pz").set(pz)

    ##
    ##

    def onDraw(self, kwargs):
        self.update_text_drawable()
        self.pivot_drawable.draw(kwargs["draw_handle"], {})
        self.parm_text_drawable.draw(kwargs["draw_handle"], {})

    def onGenerate(self, kwargs):
        kwargs["state_flags"]["exit_on_node_select"] = False

        cam_exists = 0
        for node in hou.node("/obj").children():
            if node.name() == "im_cam":
                cam_exists = 1
        if cam_exists == 0:
            cam = hou.node("/obj").createNode("cam")
            cam.setName("im_cam")

        self.cam = hou.node("/obj/im_cam")
        self.viewport = self.viewer.selectedViewport()
        self.state_parms = kwargs["state_parms"]
        self.viewport.setCamera(self.cam)
        self.viewport.lockCameraToView(True)
        self.cam.parm("projection").set(1)
        self.ui_refit()
        self.update_text_drawable()
        self.update_pivot_drawable()
        self.viewer.hudInfo(template=self.HUD_TEMPLATE)

    def onKeyEvent(self, kwargs):
        key = kwargs["ui_event"].device().keyString()
        if key in ("h", "j", "k", "l"):
            self.handle_xform(key)
            return(True)
        elif key in("Shift+-", "Shift+=", "-", "="):
            self.handle_zoom(key)
            return(True)
        else:
            return(False)

    def onMenuAction(self, kwargs):
        action = kwargs["menu_item"]
        if action == "view_frame":
            self.view_frame()
        elif action == "view_reset":
            self.view_reset()
        elif action == "ui_refit":
            self.ui_refit()
        # elif action == "toggle_grid":
            # self.viewport.settings().setDisplayOrthoGrid(kwargs["toggle_grid"])
        elif action == "movement_style":
            self.movement_style = kwargs["movement_style"]
        elif action == "pivot_style":
            self.pivot_style = kwargs["pivot_style"]
        elif action in ("zoom_in", "zoom_out", "zoom_scale_up",
            "zoom_scale_down"):
            self.handle_zoom(action)
        elif action in ("xform_left", "xform_up", "xform_down", "xform_right"):
            self.handle_xform(action)
        elif action == "print_cam_vals":
            self.print_cam_vals()
        elif action == "print_kwargs":
            self.print_kwargs(kwargs)

    def onParmChangeEvent(self, kwargs):
        if kwargs["parm_name"] == "view_frame":
            self.view_frame()
        elif kwargs["parm_name"] == "view_reset":
            self.view_reset()

def make_menu(template):

    menu = hou.ViewerStateMenu("im_view_menu", "IM View Menu")

    # key_context = "h.pane.gview.state.sop.im_view"

    # key_zoom_in         = key_context + ".zoom_in"
    # key_zoom_out        = key_context + ".zoom_out"
    # key_zoom_scale_up   = key_context + ".zoom_scale_up"
    # key_zoom_scale_down = key_context + ".zoom_scale_down"
    # key_xform_left      = key_context + ".xform_left"
    # key_xform_down      = key_context + ".xform_down"
    # key_xform_up        = key_context + ".xform_up"
    # key_xform_right     = key_context + ".xform_right"

    # hou.hotkeys.addContext(key_context,        "im_view operation", "IM view hotkeys")

    # hou.hotkeys.addCommand(key_zoom_in,         "IM Zoom In",         "IM Zoom In")
    # hou.hotkeys.addCommand(key_zoom_out,        "IM Zoom Out",        "IM Zoom Out")
    # hou.hotkeys.addCommand(key_zoom_scale_up,   "IM Zoom Scale Up",   "IM Zoom Scale Up")
    # hou.hotkeys.addCommand(key_zoom_scale_down, "IM Zoom Scale Down", "IM Zoom Scale Down")
    # hou.hotkeys.addCommand(key_xform_left,      "IM xform left",      "IM xform left")
    # hou.hotkeys.addCommand(key_xform_down,      "IM xform down",      "IM xform down")
    # hou.hotkeys.addCommand(key_xform_up,        "IM xform up",        "IM xform up")
    # hou.hotkeys.addCommand(key_xform_right,     "IM xform right",     "IM xform right")

    menu.addActionItem("view_reset",  "Reset View")
    menu.addActionItem("view_frame",  "Frame View")
    menu.addActionItem("ui_refit",    "Refit UI")
    # menu.addToggleItem("toggle_grid", "Toggle Grid", 0)

    menu.addSeparator()

    menu.addRadioStrip("movement_style", "Movement style", "rotate")
    menu.addRadioStripItem("movement_style", "rotate", "Rotate")
    menu.addRadioStripItem("movement_style", "translate", "Translate")

    menu.addRadioStrip("pivot_style", "Pivot style", "origin")
    menu.addRadioStripItem("pivot_style", "origin", "Origin")
    menu.addRadioStripItem("pivot_style", "floating", "Floating")

    menu.addSeparator()

    menu.addActionItem("zoom_in", "Zoom In")
    menu.addActionItem("zoom_out", "Zoom Out")
    menu.addActionItem("zoom_scale_up", "Zoom Scale Up")
    menu.addActionItem("zoom_scale_down", "Zoom Scale Down")

    menu.addSeparator()

    submenu0 = hou.ViewerStateMenu("xform", "xform")
    submenu0.addActionItem("xform_left", "xform left")
    submenu0.addActionItem("xform_up",  "xform up")
    submenu0.addActionItem("xform_down", "xform down")
    submenu0.addActionItem("xform_right", "xform right")
    menu.addMenu(submenu0)

    menu.addSeparator()

    menu.addActionItem("print_cam_vals", "Print Cam Vals")
    menu.addActionItem("print_kwargs",   "Print Kwargs")

    template.bindMenu(menu)

def make_parameters(template):
    template.bindParameter(hou.parmTemplateType.Button, name="view_frame",
        label="Frame")
    template.bindParameter(hou.parmTemplateType.Button, name="view_reset",
        label="Reset")
    template.bindParameter(hou.parmTemplateType.Int, name="zoom_scale",
        label="Zoom Scale", default_value=5, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int, name="rot_scale",
        label="Rotation Scale", default_value=10, toolbox=True)

    template.bindParameter(hou.parmTemplateType.Float, name="pivot",
        label="Pivot", num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float, name="rotation",
        label="Rotation", num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float, name="translation",
        label="Translation", num_components=3, toolbox=False)

def createViewerStateTemplate():

    # Initialize the state template
    template = hou.ViewerStateTemplate(\
      type_name="im_view",
      label="IM View",
      category=hou.sopNodeTypeCategory(),
      contexts=[hou.objNodeTypeCategory()])

    make_menu(template)
    make_parameters(template)

    # Bind the state handle(s)
    # template.bindHandleStatic("xform", "start_handle",
      # [("startx", "tx"), ("starty", "ty"), ("startz", "tz")])

    # Bind the state icon
    template.bindIcon("DESKTOP_application_sierra")
    # Bind the state
    template.bindFactory(State)


    return template
