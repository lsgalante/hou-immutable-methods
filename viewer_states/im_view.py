import hou
import viewerstate.utils as su
import pprint

def melog(msg):
    x = 1
    if not x:
       return
    if msg[0] + msg[1] == "on":
        print("")
    print("Function called: " + msg)


class State(object):
    HUD_TEMPLATE = {
        "title": "IM View",
        "rows": [
            {"id": "key_mode",   "label": "Key Mode",    "value": "Viewer", "key": "M"},
            {"id": "key_mode_g",  "type": "choicegraph", "count": 2},
            {"id": "mode",       "label": "Mode:",       "value": "Rotate"},
            {"id": "mode_g",      "type": "choicegraph", "count": 2},
            {"id": "scale_mod",  "label": "Scale Mod:",  "value": "Rotate"},
            {"id": "scale_mod_g", "type": "choicegraph", "count": 5},
            {"id": "target",     "label": "Target:",     "value": "Camera"},
            {"id": "target_g",    "type": "choicegraph", "count": 2},
            {"id": "viewport",   "label": "Viewport",    "value": 0},
            {"id": "viewport_g",  "type": "choicegraph", "count": 4},
            {"id": "layout",     "label": "Layout",      "value": "Split"},
            {"id": "layout_g",    "type": "choicegraph", "count": 3},
        ]
    }

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.viewer = scene_viewer
        self.reset = 1
        self.axes = [1, 1, 1]
        self.xform_mode = "Rotate"
        self.pivot_mode = "Floating"
        self.scale_modifier = "Rotate"
        self.current_viewport_id = 0

        self.key_mode = "Viewer"
        self.key_modes = ["Viewer", "Settings"]
        self.modes = ["Rotate", "Translate"]
        self.scales = ["Rotate", "Translate", "Zoom", "Distance", "FOV"]

        # Drawables
        self.axis_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="axis_drawable",
            params={"color1": hou.Vector4((1, 1, 1, 0.3))})
        self.axis_drawable.show(True)

        self.bbox_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="bbox_drawable",
            params={"color1": hou.Vector4((1, 1, 1, 0.3))})
        self.bbox_drawable.show(False)

        self.pivot_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="pivot_drawable")
        self.pivot_drawable.show(True)

        self.ray_drawable = hou.GeometryDrawable(
            scene_viewer=scene_viewer,
            geo_type=hou.drawableGeometryType.Line,
            name="ray_drawable",
            params={"color1": hou.Vector4((1, 0.8, 1, 0.5))})
        self.ray_drawable.show(True)

    ##

    def cam_to_state(self):
        melog("cam_to_state")
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

    def frame_viewports(self):
        melog("frame_viewports")
        for viewport in self.viewer.viewports():
            viewport.frameAll()
        self.cam_to_state()
        self.update_pivot_drawable()

    def get_centroid(self):
        melog("get_centroid")
        geo = self.get_geo()
        result_geo = hou.Geometry()
        centroid_verb = hou.sopNodeTypeCategory().nodeVerb("extractcentroid")
        centroid_verb.setParms({"partitiontype": 2})
        centroid_verb.execute(result_geo, [geo])
        pt = result_geo.point(0)
        p = pt.position()
        return(p)

    def get_current_viewport(self):
        melog("get_current_viewport")
        viewports = self.get_viewports()
        viewport = viewports[self.current_viewport_id]
        return(viewport)

    def get_distance(self):
        melog("get_distance")
        distance = self.state_parms["distance"]["value"]
        return(distance)

    def get_extrema(self):
        melog("get_extrema")
        geo = self.get_geo()
        bbox = geo.boundingBox()

    def get_geo(self):
        melog("get_geo")
        display_node = self.viewer.pwd().displayNode()
        geo = display_node.geometry()
        return(geo)

    def get_length(self):
        melog("get_length")
        t = self.state_parms["t"]["value"]
        p = self.state_parms["p"]["value"]
        length = t[2]
        return(length)

    def get_view_direction(self):
        melog("get_view_direction")
        r = self.state_parms["r"]["value"]
        return(r)

    def get_viewports(self):
        melog("get_viewports")
        viewports = self.viewer.viewports()
        viewports.reverse()
        return(viewports)

    def get_xform(self):
        melog("get_xform")
        t = self.state_parms["t"]["value"]
        r = self.state_parms["r"]["value"]
        p = self.state_parms["p"]["value"]
        pr = self.state_parms["pr"]["value"]
        return(t, r, p, pr)

    def handle_rotate(self, key):
        melog("handle_rotate")
        r = list(self.state_parms["r"]["value"])
        r_scale = self.state_parms["r_scale"]["value"]
        if key[-1] == "h":
            r[1] = (r[1] + r_scale) % 360
        elif key[-1] == "j":
            r[0] = (r[0] - r_scale) % 360
        elif key[-1] == "k":
            r[0] = (r[0] + r_scale) % 360
        elif key[-1] == "l":
            r[1] = (r[1] - r_scale) % 360
        self.state_parms["r"]["value"] = r

    def handle_translate(self, key):
        melog("handle_translate")
        true_pivot = list(self.state_parms["true_pivot"]["value"])
        t_scale = self.state_parms["t_scale"]["value"]
        if key[-1] == "h":
            true_pivot[0] -= t_scale
        elif key[-1] == "j":
            true_pivot[1] -= t_scale
        elif key[-1] == "k":
            true_pivot[1] += t_scale
        elif key[-1] == "l":
            true_pivot[0] += t_scale
        self.state_parms["true_pivot"]["value"] = true_pivot

    def handle_xform(self, key):
        melog("handle_xform")
        if self.xform_mode == "Rotate":
            if key in ["Shift+h", "Shift+j", "Shift+k", "Shift+l"]:
                self.handle_translate(key)
            else:
                self.handle_rotate(key)
        else:
            if key in ["Shift+h", "Shift+j", "Shift+k", "Shift +l"]:
                self.handle_rotate(key)
            else:
                self.handle_translate(key)
        self.update_global()

    def handle_zoom(self, key):
        melog("handle_zoom")
        zoom_scale = self.state_parms["zoom_scale"]["value"]
        if self.cam.evalParm("projection"):
            if key == "-": self.state_parms["ortho_width"]["value"] += zoom_scale
            elif key == "=": self.state_parms["ortho_width"]["value"] -= zoom_scale
        else:
            x=1
        self.update_global()

    def init_cam(self):
        melog("init_cam")
        x=1
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

    def next_key_mode(self):
        melog("next_key_mode")

    def next_projection(self):
        melog("next_projection")
        projection = self.cam.evalParm("projection")
        if projection:
            self.cam.parm("projection").set(0)
        else:
            self.cam.parm("projection").set(1)

    def next_scale_modifier(self):
        melog("next_scale_modifier")
        idx = self.scales.index(self.scale_modifier)
        self.scale_modifier = self.scales[(idx + 1) % len(self.scales)]
        self.update_hud()

    def next_viewport(self):
        melog("next_viewport")
        self.current_viewport_id = (self.current_viewport_id + 1) % 4
        viewports = list(self.viewer.viewports())
        viewports.reverse()
        viewport = viewports[self.current_viewport_id]
        print(viewport)
        self.update_hud()

    def next_xform_mode(self):
        melog("next_xform_mode")
        idx = self.modes.index(self.xform_mode)
        self.xform_mode = self.modes[(idx + 1) % len(self.modes)]
        self.update_hud()

    def pivot_to_camera(self):
        melog("pivot_to_camera")
        t = self.state_parms["t"]["value"]
        self.state_parms["true_pivot"]["value"] = list(t)
        self.update_global()

    def pivot_to_centroid(self):
        melog("pivot_to_centroid")
        centroid = self.get_centroid()
        self.state_parms["true_pivot"]["value"] = list(centroid)
        self.update_global()

    def pivot_to_origin(self):
        melog("pivot_to_origin")
        self.state_parms["t"]["value"] = [0, 0, self.get_distance()]
        self.state_parms["r"]["value"] = [45, 45, 0]
        self.state_parms["p"]["value"] = [0, 0, -self.get_distance()]
        self.state_parms["pr"]["value"] = [0, 0, 0]
        self.state_parms["true_pivot"]["value"] = [0, 0, 0]
        self.state_parms["ortho_width"]["value"] = 10
        self.update_global()

    def print_cam_vals(self):
        melog("print_cam_vals")
        t, r, p, pr = self.get_xform()
        print("r:\n", r, "t:\n", t, "p:\n", p, "pr:\n", pr)

    def print_centroid(self):
        melog("print_centroid")
        print(self.get_centroid())

    def print_kwargs(self, kwargs):
        melog("print_kwargs")
        ui_event = str(kwargs["ui_event"])
        ui_event = ui_event.replace("\\n", "\n")
        del kwargs["ui_event"]
        print("\n")
        pprint.pprint(kwargs)
        print(ui_event)

    def refit_ui(self):
        melog("refit_ui")
        self.cam.parm("resx").set(1000)
        self.cam.parm("resy").set(1000)
        size = self.viewport.size()
        ratio = size[2] / size[3]
        self.cam.parm("aspect").set(ratio)

    def reset_view(self):
        melog("reset_view")
        dist = self.get_distance()
        self.state_parms["t"]["value"] = [0, 0, dist]
        self.state_parms["r"]["value"] = [45, 45, 0]
        self.state_parms["p"]["value"] = [0, 0, -dist]
        self.state_parms["pr"]["value"] = [0, 0, 0]
        self.state_parms["true_pivot"]["value"] = [0, 0, 0]
        self.state_parms["ortho_width"]["value"] = 10
        self.update_global()

    def set_zoom_scale(self, key):
        melog("set_zoom_scale")
        if key == "Shift+-":
            self.state_parms["zoom_scale"]["value"] -= 1
        elif key == "Shift+=":
            self.state_parms["zoom_scale"]["value"] += 1

    def state_to_cam(self):
        melog("state_to_cam")
        x=1

    def toggle_axes(self, kwargs, action):
        melog("toggle_axes")
        if action == "show_all_axes":
            self.axes = [1, 1, 1]
        elif action == "hide_all_axes":
            self.axes = [0, 0, 0]
        elif action == "x_axis":
            self.axes[0] = kwargs["x_axis"]
        elif action == "y_axis":
            self.axes[1] = kwargs["y_axis"]
        elif action == "z_axis":
            self.axes[2] = kwargs["z_axis"]
        self.update_axis_drawable()
        print("\n----")
        print("Axis state: ", self.axes)

    def toggle_bbox(self, kwargs, action):
        melog("toggle_bbox")
        enabled = kwargs["toggle_bbox"]
        self.update_bbox_drawable()

    def update_axis_drawable(self):
        melog("update_axis_drawable")
        axis_scale = self.state_parms["axis_scale"]["value"]
        geo = hou.Geometry()
        geo.addAttrib(hou.attribType.Point, "Cd", (1, 1, 1))
        for idx in (0, 1, 2):
            if self.axes[idx]:
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

    def update_bbox_drawable(self):
        melog("update_bbox_drawable")
        geo = self.get_geo()
        bbox = geo.boundingBox()
        p0 = (bbox[0], bbox[1], bbox[2])
        p1 = (bbox[0], bbox[1], bbox[5])
        p2 = (bbox[3], bbox[1], bbox[5])
        p3 = (bbox[3], bbox[1], bbox[2])
        p4 = (bbox[0], bbox[4], bbox[2])
        p5 = (bbox[0], bbox[4], bbox[5])
        p6 = (bbox[3], bbox[4], bbox[5])
        p7 = (bbox[3], bbox[4], bbox[2])
        print(bbox)

    def update_cam_parms(self):
        melog("update_cam_parms")
        t, r, p, pr = self.get_xform()
        self.cam.parmTuple("r").set(r)
        self.cam.parmTuple("t").set(t)
        self.cam.parmTuple("p").set(p)
        self.cam.parmTuple("pr").set(pr)
        self.cam.parm("orthowidth").set(self.state_parms["ortho_width"]["value"])

    def update_global(self):
        melog("update_global")
        self.update_state_parms()
        self.update_cam_parms()
        self.update_pivot_drawable()
        self.update_ray_drawable()

    def update_hud(self):
        melog("update_hud")
        updates = {
            "mode": {"value": self.xform_mode},
            "mode_g": {"value": self.modes.index(self.xform_mode)},
            "scale_modifier": {"value": self.scale_modifier},
            "scale_modifier_g": {"value": self.scales.index(self.scale_modifier)},
            "viewport": {"value": self.current_viewport_id},
            "viewport_g": {"value": self.current_viewport_id}
        }
        self.viewer.hudInfo(hud_values=updates)

    def update_pivot_drawable(self):
        melog("update_pivot_drawable")
        r = list(self.state_parms["r"]["value"])
        t = list(self.state_parms["t"]["value"])
        p = list(self.state_parms["p"]["value"])
        ortho_width = self.state_parms["ortho_width"]["value"]
        s = ortho_width / 2
        pos = hou.Vector3(p) + hou.Vector3(t)
        geo = hou.Geometry()
        circle_verb = hou.sopNodeTypeCategory().nodeVerb("circle")
        circle_verb.setParms({"type": 1, "r": r, "t": pos, "scale": s * 0.015})
        circle_verb.execute(geo, [])
        self.pivot_drawable.setGeometry(geo)
        self.pivot_drawable.setParams({
            "color1": hou.Vector4(0.0, 0.0, 1, 1),
            "fade_factor": 1.0
        })

    def update_ray_drawable(self):
        melog("update_ray_drawable")
        t = self.state_parms["t"]["value"]
        r = self.state_parms["r"]["value"]
        p = self.state_parms["p"]["value"]
        true_pivot = self.state_parms["true_pivot"]["value"]

        rot = hou.hmath.buildRotate(r)
        cam_pos = hou.Vector3(0, 0, self.get_length()) * rot
        cam_pos += hou.Vector3(true_pivot[0], true_pivot[1], true_pivot[2])

        pivot_pos = hou.Vector3(t) + hou.Vector3(p)

        geo = hou.Geometry()
        pts = geo.createPoints((cam_pos, pivot_pos))
        prim = geo.createPolygon()
        prim.addVertex(pts[0])
        prim.addVertex(pts[1])
        self.ray_drawable.setGeometry(geo)

    def update_state_parms(self):
        melog("update_state_parms")
        true_pivot = self.state_parms["true_pivot"]["value"]
        distance = self.state_parms["distance"]["value"]
        self.state_parms["t"]["value"][0] = true_pivot[0]
        self.state_parms["t"]["value"][1] = true_pivot[1]
        # self.state_parms["t"]["value"][2] = true_pivot[2] + distance
        self.state_parms["t"]["value"][2] = distance
        self.state_parms["p"]["value"][0] = 0
        self.state_parms["p"]["value"][1] = 0
        self.state_parms["p"]["value"][2] = true_pivot[2] - distance

    def update_viewports(self):
        melog("update_viewports")
        self.viewports = self.get_viewports()

    ##
    ##

    def onDraw(self, kwargs):
        self.axis_drawable.draw(kwargs["draw_handle"], {})
        self.pivot_drawable.draw(kwargs["draw_handle"], {})
        self.ray_drawable.draw(kwargs["draw_handle"], {})

    def onGenerate(self, kwargs):
        melog("onGenerate")
        # Integrate with node graph
        kwargs["state_flags"]["exit_on_node_select"] = False
        # Init vars
        self.viewer.hudInfo(template=self.HUD_TEMPLATE)
        self.update_hud
        self.viewport = self.viewer.selectedViewport()
        self.state_parms = kwargs["state_parms"]
        # Call functions
        self.init_cam()
        self.cam_to_state()
        self.refit_ui()
        self.update_axis_drawable()
        self.update_pivot_drawable()
        self.update_ray_drawable()
        self.reset_view()

    def onKeyEvent(self, kwargs):
        melog("onKeyEvent")
        key = kwargs["ui_event"].device().keyString()
        # Shifties
        if key[-1] in ("h", "j", "k", "l"):
            self.handle_xform(key)
            return(True)
        elif key in("Shift+-", "Shift+="):
            self.set_zoom_scale(key)
            return(True)
        # Non-shifties
        elif key == "m":
            self.next_key_mode()
            return(True)
        elif key in("-", "="):
            self.handle_zoom(key)
            return(True)
        else:
            return(False)

    def onMenuAction(self, kwargs):
        melog("onMenuAction")
        action = kwargs["menu_item"]
        if action == "pivot_to_camera":
            self.pivot_to_camera()
        elif action == "pivot_to_centroid":
            self.pivot_to_centroid()
        elif action == "pivot_to_origin":
            self.pivot_to_origin()
        elif action == "frame_viewports":
            self.frame_viewports()
        elif action == "reset_view":
            self.reset_view()
        elif action == "toggle_bbox":
            self.toggle_bbox(kwargs, action)
        elif action in ["show_all_axes", "hide_all_axes", "x_axis", "y_axis",
            "z_axis"]:
            self.toggle_axes(kwargs, action)
        elif action == "pivot_to_origin":
            self.pivot_to_origin()
        elif action == "pivot_to_centroid":
            self.pivot_to_centroid()
        elif action == "frame_viewports":
            self.frame_viewports()
        elif action == "reset_view":
            self.reset_view()
        elif action == "refit_ui":
            self.refit_ui()
        elif action == "print_cam_vals":
            self.print_cam_vals()
        elif action == "print_kwargs":
            self.print_kwargs(kwargs)
        elif action == "print_centroid":
            self.print_centroid()

    def onParmChangeEvent(self, kwargs):
        melog("onParmChangeEvent")
        parm = kwargs["parm_name"]
        if parm == "axis_scale":
            self.update_axis_drawable()
        elif parm == "distance":
            self.update_global()
        elif parm == "t":
            self.update_global()
        elif parm == "r":
            self.update_global()
        elif parm == "p":
            self.update_global()
        elif parm == "pr":
            self.update_global()
        elif parm == "true_pivot":
            self.update_global()

def make_menu(template):
    menu = hou.ViewerStateMenu("im_view_menu", "IM View Menu")

    menu.addActionItem("pivot_to_camera", "Pivot to Camera")
    menu.addActionItem("pivot_to_centroid", "Pivot to Centroid")
    menu.addActionItem("pivot_to_origin", "Pivot to Origin")

    menu.addSeparator()

    menu.addActionItem("frame_viewports", "Frame Viewports")
    menu.addActionItem("reset_view", "Reset View")
    menu.addToggleItem("toggle_bbox", "Bounding Box", 0)

    menu.addSeparator()

    axis_menu = hou.ViewerStateMenu("axes", "Axes")
    axis_menu.addActionItem("show_all_axes", "Show All")
    axis_menu.addActionItem("hide_all_axes", "Hide All")
    axis_menu.addSeparator()
    axis_menu.addToggleItem("x_axis", "X Axis", 1)
    axis_menu.addToggleItem("y_axis", "Y Axis", 1)
    axis_menu.addToggleItem("z_axis", "Z Axis", 1)
    menu.addMenu(axis_menu)

    view_menu = hou.ViewerStateMenu("view", "View")
    view_menu.addActionItem("refit_ui", "Refit UI")
    view_menu.addSeparator()
    view_menu.addActionItem("top", "Top")
    view_menu.addActionItem("bottom", "Bottom")
    view_menu.addActionItem("left", "Left")
    view_menu.addActionItem("right", "Right")
    view_menu.addActionItem("front", "Front")
    view_menu.addActionItem("back", "Back")
    menu.addMenu(view_menu)
    # menu.addToggleItem("toggle_grid", "Toggle Grid", 0)

    layout_menu = hou.ViewerStateMenu("layout_menu", "Layout")
    layout_menu.addRadioStrip("layout", "Layout", "spreadsheet")
    layout_menu.addRadioStripItem("layout", "spreadsheet", "Spreadsheet")
    layout_menu.addRadioStripItem("layout", "split", "Split")
    layout_menu.addRadioStripItem("layout", "full", "Full")
    menu.addMenu(layout_menu)

    menu.addSeparator()

    print_menu = hou.ViewerStateMenu("print", "Print")
    print_menu.addActionItem("print_cam_vals", "Cam Vals")
    print_menu.addActionItem("print_kwargs", "Kwargs")
    print_menu.addActionItem("print_centroid", "Centroid")
    menu.addMenu(print_menu)

    template.bindMenu(menu)

def make_parameters(template):
    template.bindParameter(hou.parmTemplateType.Separator,
        "sep0", toolbox=False)
    template.bindParameter(hou.parmTemplateType.Int,
        "axis_scale", "Axis Scale", default_value=4, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Int,
        "r_scale", "R Scale", default_value=15, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int,
        "t_scale", "T Scale", default_value=1, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int,
        "zoom_scale", "Z Scale", default_value=2, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Separator,
        "sep1", toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        "distance", "Distance", default_value=10.0)
    template.bindParameter(hou.parmTemplateType.Float,
        "ortho_width", "FOV", default_value=10.0)
    template.bindParameter(hou.parmTemplateType.Separator,
        "sep2", toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        "t", "Translation", num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        "r", "Rotation", num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        "p", "Pivot", num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        "pr", "Pivot Rotation", num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,
        "true_pivot", "True pivot", num_components=3, toolbox=False)

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
