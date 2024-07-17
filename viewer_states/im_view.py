import hou
import viewerstate.utils as su
import pprint


class State(object):
    HUD_TEMPLATE = {
        "title": "IM View",
        "rows":\
        [
            {"id": "projection", "label": "Projection:", "value": "Orthographic"},
            {"id": "pivot_style", "label": "Pivot Style:", "value": "Origin"},
            {"id": "movement_style", "label": "Movement Style:",
                "value": "Rotate", "key": "M"},
            {"id": "xform", "label": "Xform", "key": "H/J/K/L"}
        ]
    }

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.viewer = scene_viewer
        self.reset = 1
        self.x_axis = 1
        self.y_axis = 1
        self.z_axis = 1

        # Drawables
        self.axis_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="axis_drawable",
            params={"color1": hou.Vector4((1, 1, 1, 0.3))})
        self.axis_drawable.show(True)

        self.pivot_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="pivot_drawable")
        self.pivot_drawable.show(True)

        self.ray_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="ray_drawable",
            params={"color1": hou.Vector4((1, 1, 1, 0.5))})
        self.ray_drawable.show(True)

    ##

    def get_centroid(self):
        display_node = self.viewer.pwd().displayNode()
        geo = display_node.geometry()
        result_geo = hou.Geometry()
        centroid_verb = hou.sopNodeTypeCategory().nodeVerb("extractcentroid")
        centroid_verb.setParms({"partitiontype": 2})
        centroid_verb.execute(result_geo, [geo])
        pt = result_geo.point(0)
        p = pt.position()
        return(p)

    def get_direction(self):
        r = self.state_parms["r"]["value"]
        return(r)

    def get_distance(self):
        distance = self.state_parms["distance"]["value"]
        return(distance)

    def get_length(self):
        t = self.state_parms["t"]["value"]
        p = self.state_parms["p"]["value"]
        length = t[2]
        return(length)

    def get_xform(self):
        t = self.state_parms["t"]["value"]
        r = self.state_parms["r"]["value"]
        p = self.state_parms["p"]["value"]
        pr = self.state_parms["pr"]["value"]
        return(t, r, p, pr)

    def global_updates(self):
        self.update_state_parms()
        self.update_cam_parms()
        self.update_pivot_drawable()
        self.update_ray_drawable()

    def handle_rotate(self, key):
        r = list(self.state_parms["r"]["value"])
        r_scale = self.state_parms["r_scale"]["value"]
        if key == "h":
            r[1] = (r[1] + r_scale) % 360
        elif key == "j":
            r[0] = (r[0] - r_scale) % 360
        elif key == "k":
            r[0] = (r[0] + r_scale) % 360
        elif key == "l":
            r[1] = (r[1] - r_scale) % 360
        self.state_parms["r"]["value"] = r

    def handle_translate(self, key):
        t = list(self.state_parms["t"]["value"])
        t_scale = self.state_parms["t_scale"]["value"]
        if key == "h":
            t[0] -= t_scale
        elif key == "j":
            t[1] -= t_scale
        elif key == "k":
            t[1] += t_scale
        elif key == "l":
            t[0] += t_scale
        self.state_parms["t"]["value"] = t

    def handle_xform(self, key):
        movement_style = "rotate"
        if self.state_parms["movement_style"]["value"]:
            movement_style = "translate"
        eval("self.handle_" + movement_style + "(key)")
        self.global_updates()

    def handle_zoom(self, key):
        zoom_scale = self.state_parms["zoom_scale"]["value"]
        if self.cam.evalParm("projection"):
            if key == "-": self.state_parms["ortho_width"]["value"] += zoom_scale
            elif key == "=": self.state_parms["ortho_width"]["value"] -= zoom_scale
        else:
            x=1
        self.global_updates()

    def pivot_to_camera(self):
        t = self.state_parms["t"]["value"]
        r = self.state_parms["r"]["value"]
        p = self.state_parms["p"]["value"]

    def pivot_to_centroid(self):
        centroid = self.get_centroid()
        self.state_parms["true_center"]["value"] = list(centroid)
        self.global_updates()

    def pivot_to_origin(self):
        t = self.state_parms["t"]["value"]
        self.state_parms["p"]["value"][0] = -t[0]
        self.state_parms["p"]["value"][1] = -t[1]
        self.state_parms["p"]["value"][2] = -t[2]
        self.global_updates()

    def print_cam_vals(self):
        t, r, p, pr = self.get_xform()
        print("r:\n", r, "t:\n", t, "p:\n", p, "pr:\n", pr)

    def print_centroid(self):
        print(self.get_centroid())

    def print_kwargs(self, kwargs):
        ui_event = str(kwargs["ui_event"])
        ui_event = ui_event.replace("\\n", "\n")
        del kwargs["ui_event"]
        print("\n")
        pprint.pprint(kwargs)
        print(ui_event)

    def refit_ui(self):
        self.cam.parm("resx").set(1000)
        self.cam.parm("resy").set(1000)
        size = self.viewport.size()
        ratio = size[2] / size[3]
        self.cam.parm("aspect").set(ratio)

    def set_cam(self):
        cam_exists = 0
        for node in hou.node("/obj").children():
            if node.name() == "im_cam":
                cam_exists = 1
        if cam_exists == 0:
            cam = hou.node("/obj").createNode("cam")
            cam.setName("im_cam")
        self.cam = hou.node("/obj/im_cam")
        self.viewport.setCamera(self.cam)
        self.viewport.lockCameraToView(True)
        # self.state_parms["projection"]["value"] = "orthographic"

    def set_zoom_scale(self, key):
        if key == "Shift+-":
            self.state_parms["zoom_scale"]["value"] -= 1
        elif key == "Shift+=":
            self.state_parms["zoom_scale"]["value"] += 1

    def state_to_cam(self):
        x=1

    def cam_to_state(self):
        t = self.cam.parmTuple("t").eval()
        p = self.cam.parmTuple("p").eval()
        r = self.cam.parmTuple("r").eval()
        pr = self.cam.parmTuple("pr").eval()
        ortho_width = self.cam.evalParm("orthowidth")
        self.state_parms["t"]["value"] = list(t)
        self.state_parms["p"]["value"] = list(p)
        self.state_parms["r"]["value"] = list(r)
        self.state_parms["pr"]["value"] = list(pr)
        self.state_parms["ortho_width"]["value"] = ortho_width

    def toggle_movement_style(self):
        movement_style = self.state_parms["movement_style"]["value"]
        movement_style = (movement_style + 1) % 2
        self.state_parms["movement_style"]["value"] = movement_style

    def toggle_projection(self):
        projection = self.cam.evalParm("projection")
        if projection:
            self.cam.parm("projection").set(0)
        else:
            self.cam.parm("projection").set(1)

    def update_cam_parms(self):
        t, r, p, pr = self.get_xform()
        self.cam.parmTuple("r").set(r)
        self.cam.parmTuple("t").set(t)
        self.cam.parmTuple("p").set(p)
        self.cam.parmTuple("pr").set(pr)
        self.cam.parm("orthowidth").set(self.state_parms["ortho_width"]["value"])

    def update_hud(self):
        movement_style = ("Rotate", "Translate")\
            [self.state_parms["movement_style"]["value"]]
        updates = {
            "movement_style": {"value": movement_style}
        }
        self.viewer.hudInfo(hud_values=updates)

    def update_state_parms(self):
        print("x")
        true_center = self.state_parms["true_center"]["value"]
        distance = self.state_parms["distance"]["value"]
        self.state_parms["t"]["value"][0] = true_center[0]
        self.state_parms["t"]["value"][1] = true_center[1]
        self.state_parms["t"]["value"][2] = distance
        self.state_parms["p"]["value"][0] = 0
        self.state_parms["p"]["value"][1] = 0
        self.state_parms["p"]["value"][2] = true_center[2] - distance

    def update_axis_drawable(self):
        axes = (self.state_parms["x_axis"]["value"],
            self.state_parms["y_axis"]["value"],
            self.state_parms["z_axis"]["value"])
        axis_scale = self.state_parms["axis_scale"]["value"]
        geo = hou.Geometry()
        geo.addAttrib(hou.attribType.Point, "Cd", (1, 1, 1))
        for idx in (0, 1, 2):
            if axes[idx]:
                p0 = [0, 0, 0]
                p1 = [0, 0, 0]
                p0[idx] = -axis_scale
                p1[idx] = axis_scale
                pts = geo.createPoints((p0, p1))
                cd = [0, 0, 0]
                cd[idx] = 1
                pts[0].setAttribValue("Cd", cd)
                pts[1].setAttribValue("Cd", cd)
                prim = geo.createPolygon(is_closed=False)
                prim.addVertex(pts[0])
                prim.addVertex(pts[1])
        self.axis_drawable.setGeometry(geo)
        self.axis_drawable.setParams({"fade_factor": 0.0})

    def update_pivot_drawable(self):
        r = list(self.state_parms["r"]["value"])
        t = list(self.state_parms["t"]["value"])
        p = list(self.state_parms["p"]["value"])
        ortho_width = self.state_parms["ortho_width"]["value"]
        s = ortho_width / 2
        pos = hou.Vector3(p) + hou.Vector3(t)
        geo = hou.Geometry()
        circle_verb = hou.sopNodeTypeCategory().nodeVerb("circle")
        circle_verb.setParms({"scale": 1.0, "type": 1, "r": r, "t": pos,
            "scale": s * 0.025})
        circle_verb.execute(geo, [])
        self.pivot_drawable.setGeometry(geo)
        self.pivot_drawable.setParams({
            "color1": hou.Vector4(1, 0, 0, 1),
            "fade_factor": 1.0
        })

    def update_ray_drawable(self):
        t = self.state_parms["t"]["value"]
        r = self.state_parms["r"]["value"]
        p = self.state_parms["p"]["value"]
        true_center = self.state_parms["true_center"]["value"]

        rot = hou.hmath.buildRotate(r)
        cam_pos = hou.Vector3(0, 0, self.get_length()) * rot
        cam_pos += hou.Vector3(true_center[0], true_center[1], true_center[2])

        pivot_pos = hou.Vector3(t) + hou.Vector3(p)

        geo = hou.Geometry()
        pts = geo.createPoints((cam_pos, pivot_pos))
        prim = geo.createPolygon()
        prim.addVertex(pts[0])
        prim.addVertex(pts[1])
        self.ray_drawable.setGeometry(geo)

    def frame_viewports(self):
        for viewport in self.viewer.viewports():
            viewport.frameAll()
        self.cam_to_state()
        self.update_pivot_drawable()

    ##
    ##

    def onDraw(self, kwargs):
        self.axis_drawable.draw(kwargs["draw_handle"], {})
        self.pivot_drawable.draw(kwargs["draw_handle"], {})
        self.ray_drawable.draw(kwargs["draw_handle"], {})

    def onGenerate(self, kwargs):
        kwargs["state_flags"]["exit_on_node_select"] = False
        self.viewport = self.viewer.selectedViewport()
        self.state_parms = kwargs["state_parms"]
        self.set_cam()
        self.refit_ui()
        self.update_axis_drawable()
        self.viewer.hudInfo(template=self.HUD_TEMPLATE)
        self.cam_to_state()
        self.global_updates()

    def onKeyEvent(self, kwargs):
        key = kwargs["ui_event"].device().keyString()
        if key in ("h", "j", "k", "l"):
            self.handle_xform(key)
            return(True)
        elif key == "m":
            self.toggle_movement_style()
            self.update_hud()
            return(True)
        elif key == "o":
            self.toggle_projection()
            return(True)
        elif key in("Shift+-", "Shift+="):
            self.set_zoom_scale(key)
            return(True)
        elif key in("-", "="):
            self.handle_zoom(key)
            return(True)
        else:
            return(False)

    def onMenuAction(self, kwargs):
        action = kwargs["menu_item"]

        # Axes menu

        # Pivot menu
        if action == "pivot_to_origin":
            self.pivot_to_origin()
        elif action == "pivot_to_centroid":
            self.pivot_to_centroid()

        # View menu
        elif action == "frame_viewports":
            self.frame_viewports()
        elif action == "reset_view":
            self.reset_view()
        elif action == "refit_ui":
            self.refit_ui()
        # elif action == "toggle_grid":
            # self.viewport.settings().setDisplayOrthoGrid(kwargs["toggle_grid"])

        # Zoom menu
        elif action in ("zoom_in", "zoom_out"):
            self.handle_zoom(action)
        elif action in ("zoom_scale_up", "zoom_scale_down"):
            self.set_zoom_scale(action)

        # Xform menu
        elif action in ("xform_left", "xform_up", "xform_down", "xform_right"):
            self.handle_xform(action)

        # Radio section
        elif action == "projection":
            self.toggle_projection()
        elif action == "movement_style":
            self.movement_style = kwargs["movement_style"]

        # Print menu
        elif action == "print_cam_vals":
            self.print_cam_vals()
        elif action == "print_kwargs":
            self.print_kwargs(kwargs)
        elif action == "print_centroid":
            self.print_centroid()

    def onParmChangeEvent(self, kwargs):
        parm = kwargs["parm_name"]
        # Button
        if parm == "frame_viewports":
            self.frame_viewports()
        elif parm == "reset_view":
            self.reset_view()
        # Scale
        elif parm == "axis_scale":
            self.update_axis_drawable()
        # Menu
        elif parm in ("x_axis", "y_axis", "z_axis"):
            self.update_axis_drawable()

        elif parm == "distance":
            self.global_updates()

        # Xform
        elif parm == "t":
            self.global_updates()
        elif parm == "r":
            self.global_updates()
        elif parm == "p":
            self.global_updates()
        elif parm == "pr":
            self.global_updates()

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

    axis_menu = hou.ViewerStateMenu("axes", "Axes")
    axis_menu.addActionItem("show_all_axes", "Show All Axes")
    axis_menu.addActionItem("disable_all_axes", "Disable All Axes")
    axis_menu.addSeparator()
    axis_menu.addToggleItem("show_x_axis", "X Axis", 1)
    axis_menu.addToggleItem("show_y_axis", "Y Axis", 1)
    axis_menu.addToggleItem("show_z_axis", "Z Axis", 1)
    menu.addMenu(axis_menu)

    pivot_menu = hou.ViewerStateMenu("pivot", "Pivot")
    pivot_menu.addActionItem("pivot_to_origin", "Move to Origin")
    pivot_menu.addActionItem("pivot_to_centroid", "Move to Centroid")
    menu.addMenu(pivot_menu)

    view_menu = hou.ViewerStateMenu("view", "View")
    view_menu.addActionItem("reset_view",  "Reset")
    view_menu.addActionItem("frame_viewports", "Frame Viewports")
    view_menu.addActionItem("refit_ui",    "Refit UI")
    view_menu.addSeparator()
    view_menu.addActionItem("top", "Top")
    view_menu.addActionItem("bottom", "Bottom")
    view_menu.addActionItem("left", "Left")
    view_menu.addActionItem("right", "Right")
    view_menu.addActionItem("front", "Front")
    view_menu.addActionItem("back", "Back")
    menu.addMenu(view_menu)
    # menu.addToggleItem("toggle_grid", "Toggle Grid", 0)

    xform_menu = hou.ViewerStateMenu("xform", "Xform")
    xform_menu.addActionItem("xform_left", "xform left")
    xform_menu.addActionItem("xform_up",  "xform up")
    xform_menu.addActionItem("xform_down", "xform down")
    xform_menu.addActionItem("xform_right", "xform right")
    menu.addMenu(xform_menu)

    zoom_menu = hou.ViewerStateMenu("zoom", "Zoom")
    zoom_menu.addActionItem("zoom_in", "Zoom In")
    zoom_menu.addActionItem("zoom_out", "Zoom Out")
    zoom_menu.addActionItem("zoom_scale_up", "Zoom Scale Up")
    zoom_menu.addActionItem("zoom_scale_down", "Zoom Scale Down")
    menu.addMenu(zoom_menu)

    menu.addSeparator()

    menu.addActionItem("toggle_projection", "Toggle Projection")

    menu.addRadioStrip("movement_style", "Movement style", "rotate")
    menu.addRadioStripItem("movement_style", "rotate", "Rotate")
    menu.addRadioStripItem("movement_style", "translate", "Translate")

    menu.addSeparator()

    print_menu = hou.ViewerStateMenu("print", "Print")
    print_menu.addActionItem("print_cam_vals", "Print Cam Vals")
    print_menu.addActionItem("print_kwargs", "Print Kwargs")
    print_menu.addActionItem("print_centroid", "Print Centroid")
    menu.addMenu(print_menu)

    template.bindMenu(menu)

def make_parameters(template):
    template.bindParameter(hou.parmTemplateType.Button,
        name="frame_viewports", label="Frame",
        align=True)
    template.bindParameter(hou.parmTemplateType.Button,
        name="reset_view", label="Reset")

    template.bindParameter(hou.parmTemplateType.Separator, name="sep0",
        toolbox=False)

    template.bindParameter(hou.parmTemplateType.Int,
        name="axis_scale", label="Axis Scale",
        default_value = 4, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Int,
        name="r_scale", label="Rotation Scale",
        default_value=15, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int,
        name="t_scale", label="Translation Scale",
        default_value=1, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int,
        name="zoom_scale", label="Zoom Scale",
        default_value=2, toolbox=True)

    template.bindParameter(hou.parmTemplateType.Separator, name="sep1",
        toolbox=False)

    template.bindParameter(hou.parmTemplateType.Menu,
        name="movement_style", label="Movement",
        menu_items = (('rotate', 'Rotate'), ('translate', 'Translate')),
        default_value="rotate", toolbox=False)
    template.bindParameter(hou.parmTemplateType.Toggle,
        name="x_axis", label="X",
        default_value=True, align=True, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Toggle,
        name="y_axis", label="Y",
        default_value=True, align=True, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Toggle,
        name="z_axis", label="Z",
        default_value=True, align=False, toolbox=False)

    template.bindParameter(hou.parmTemplateType.Separator, name="sep2",
        toolbox=False)

    template.bindParameter(hou.parmTemplateType.Float,
        name="distance", label="Distance",
        default_value=10.0)
    template.bindParameter(hou.parmTemplateType.Float,
        name="ortho_width", label="Ortho Width",
        default_value=10.0)

    template.bindParameter(hou.parmTemplateType.Separator, name="sep3",
        toolbox=False)

    template.bindParameter(hou.parmTemplateType.Float,
        name="t", label="Translation",
        num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        name="r", label="Rotation",
        num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        name="p", label="Pivot",
        num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        name="pr", label="Pivot Rotation",
        num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        name="true_center", label="True Center",
        num_components=3, toolbox=False)

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
