import hou
import pprint
import traceback
import viewerstate.utils as su

class State(object):
    HUD_TEMPLATE = {
        "title": "IM View",
        "rows": [
            {"id": "key_mode",     "label": "Key mode",    "key": "M"},
            {"id": "key_mode_g",   "type":  "choicegraph", "count": 2},
            {"type": "divider"},
            {"id": "xform_mode",   "label": "Xform mode"},
            {"id": "xform_mode_g", "type":  "choicegraph", "count": 2},
            {"id": "scale_mod",    "label": "Scale mod"},
            {"id": "scale_mod_g",  "type":  "choicegraph", "count": 5},
            {"id": "target",       "label": "Target"},
            {"id": "target_g",     "type":  "choicegraph", "count": 2},
            {"id": "viewport",     "label": "Viewport"},
            {"id": "viewport_g",   "type":  "choicegraph", "count": 4},
            {"id": "layout",       "label": "Layout"},
            {"id": "layout_g",     "type":  "choicegraph", "count": 3},
        ]
    }

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.viewer = scene_viewer
        self.reset = 1
        self.axes = [1, 1, 1]
        self.spreadsheet = None

        self.state_state = {
            "key_mode": "viewer",
            "key_mode_arr": ("viewer", "settings"),
            "setting": "xform_mode",
            "setting_arr": ("xform_mode", "scale_mod", "target", "viewport", "layout"),
            "xform_mode": "rotate",
            "xform_mode_arr": ("rotate", "translate"),
            "scale_mod": "rotate",
            "scale_mod_arr": ("rotate", "translate", "zoom", "distance", "fov"),
            "target": "camera",
            "target_arr": ["camera", "pivot"],
            "viewport": "",
            "viewport_arr": [],
            "layout": "split",
            "layout_arr": ("split", "spreadsheet", "full")
        }

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
        self.log("cam_to_state", severity=hou.severityType.ImportantMessage)
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

    def dispatch_settings(self, key):
        self.log("dispatch_settings", severity=hou.severityType.ImportantMessage)
        if key in ("j", "k"):
            idx = self.state_state["setting_arr"].index(self.state_state["setting"])
            if key == "j":
                idx = (idx + 1) % len(self.state_state["setting_arr"])
            elif key == "k":
                idx = (idx - 1) % len(self.state_state["setting_arr"])
            self.state_state["setting"] = self.state_state["setting_arr"][idx]
        elif key in ("h", "l"):
            idx = -1
            mod = -1
            setting = self.state_state["setting"]
            array = self.state_state[setting + "_arr"]
            idx = array.index(self.state_state[setting])
            mod = len(array)
            if key == "h":
                idx = (idx - 1) % mod
            elif key == "l":
                idx = (idx + 1) % mod
            choice = array[idx]
            self.log("Setting: " + setting)
            self.log("Choice: " + choice)
            self.state_state[setting] = choice
            if setting == "layout":
                self.update_layout()
        self.update_hud()

    def dispatch_xform(self, key):
        self.log("dispatch_xform", severity=hou.severityType.ImportantMessage)
        if key in ("Shift+h", "Shift+j", "Shift+k", "Shift+l"):
            if self.state_state["xform_mode"] == "rotate":
                self.handle_xform("translate", key)
            elif self.state_state["xform_mode"] == "translate":
                self.handle_xform("rotate", key)
        elif key in ("h", "j", "k", "l"):
            if self.state_state["xform_mode"] == "rotate":
                self.handle_xform("rotate", key)
            elif self.state_state["xform_mode"] == "translate":
                self.handle_xform("translate", key)
        elif key in ("Shift+-", "Shift+="):
            self.set_zoom_scale(key)
        elif key in("-", "="):
            self.handle_xform("zoom", key)
        self.interpret_true_pivot()
        self.update_cam_parms()
        self.update_drawable(("pivot", "ray"))

    def frame_viewports(self):
        self.log("frame_viewports")
        for viewport in self.viewer.viewports():
            viewport.frameAll()
        self.cam_to_state()
        self.update_drawable(("pivot"))

    def get_centroid(self):
        self.log("get_centroid", severity=hou.severityType.ImportantMessage)
        geo = self.get_geo()
        result_geo = hou.Geometry()
        centroid_verb = hou.sopNodeTypeCategory().nodeVerb("extractcentroid")
        centroid_verb.setParms({"partitiontype": 2})
        centroid_verb.execute(result_geo, [geo])
        pt = result_geo.point(0)
        p = pt.position()
        return(p)

    def get_current_viewport(self):
        self.log("get_current_viewport", severity=hou.severityType.ImportantMessage)
        viewports = self.get_viewports()
        viewport = viewports[self.state_state["viewport"]]
        return(viewport)

    def get_distance(self):
        self.log("get_distance", severity=hou.severityType.ImportantMessage)
        distance = self.state_parms["distance"]["value"]
        return(distance)

    def get_extrema(self):
        self.log("get_extrema", severity=hou.severityType.ImportantMessage)
        geo = self.get_geo()
        bbox = geo.boundingBox()

    def get_geo(self):
        self.log("get_geo", severity=hou.severityType.ImportantMessage)
        display_node = self.viewer.pwd().displayNode()
        geo = display_node.geometry()
        return(geo)

    def get_length(self):
        self.log("get_length", severity = hou.severityType.ImportantMessage)
        t = self.state_parms["t"]["value"]
        p = self.state_parms["p"]["value"]
        length = t[2]
        return(length)

    def get_view_direction(self):
        self.log("get_view_direction", severity=hou.severityType.ImportantMessage)
        r = self.state_parms["r"]["value"]
        return(r)

    def get_viewports(self):
        self.log("get_viewports", severity=hou.severityType.ImportantMessage)
        viewports = self.viewer.viewports()
        viewports.reverse()
        return(viewports)

    def get_xform(self):
        self.log("get_xform", severity=hou.severityType.ImportantMessage)
        t = self.state_parms["t"]["value"]
        r = self.state_parms["r"]["value"]
        p = self.state_parms["p"]["value"]
        pr = self.state_parms["pr"]["value"]
        return(t, r, p, pr)

    def handle_xform(self, xform, key):
        self.log("handle_xform", severity=hou.severityType.ImportantMessage)
        if xform == "rotate":
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
        elif xform == "translate":
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
        elif xform == "zoom":
            zoom_scale = self.state_parms["zoom_scale"]["value"]
            if self.cam.evalParm("projection"):
                if key == "-": self.state_parms["ortho_width"]["value"] += zoom_scale
                elif key == "=": self.state_parms["ortho_width"]["value"] -= zoom_scale
            else:
                x=1
            self.interpret_true_pivot()
            self.update_cam_parms()
            self.update_drawable(("pivot", "ray"))

    def init_cam(self):
        self.log("init_cam", severity=hou.severityType.ImportantMessage)
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

    def init_layout(self):
        self.log("ass")
        panes = hou.ui.panes()
        for pane in panes:
            tabs = pane.tabs()
            for tab in tabs:
                type = tab.type()
                if type == hou.paneTabType.DetailsView:
                    self.spreadsheet = tab
        self.log(self.spreadsheet.pane().getSplitFraction())
        self.spreadsheet.pane().setIsSplitMinimized(True)

    def interpret_true_pivot(self):
        self.log("interpret_true_pivot", severity=hou.severityType.ImportantMessage)
        true_pivot = self.state_parms["true_pivot"]["value"]
        distance = self.state_parms["distance"]["value"]
        self.state_parms["t"]["value"][0] = true_pivot[0]
        self.state_parms["t"]["value"][1] = true_pivot[1]
        self.state_parms["t"]["value"][2] = distance
        self.state_parms["p"]["value"][0] = 0
        self.state_parms["p"]["value"][1] = 0
        self.state_parms["p"]["value"][2] = true_pivot[2] - distance

    def next_key_mode(self):
        self.log("next_key_mode", severity=hou.severityType.ImportantMessage)
        idx = self.state_state["key_mode_arr"].index(self.state_state["key_mode"])
        idx = (idx + 1) % len(self.state_state["key_mode_arr"])
        self.state_state["key_mode"] = self.state_state["key_mode_arr"][idx]
        self.update_hud()

    def pivot_to_camera(self):
        self.log("pivot_to_camera", severity=hou.severityType.ImportantMessage)
        t = self.state_parms["t"]["value"]
        self.state_parms["true_pivot"]["value"] = list(t)
        self.interpret_true_pivot()
        self.update_cam_parms()
        self.update_drawable(("pivot", "ray"))

    def pivot_to_centroid(self):
        self.log("pivot_to_centroid", severity=hou.severityType.ImportantMessage)
        centroid = self.get_centroid()
        self.state_parms["true_pivot"]["value"] = list(centroid)
        self.interpret_true_pivot()
        self.update_cam_parms()
        self.update_drawable(("pivot", "ray"))

    def pivot_to_origin(self):
        self.log("pivot_to_origin", severity=hou.severityType.ImportantMessage)
        self.state_parms["t"]["value"] = [0, 0, self.get_distance()]
        self.state_parms["r"]["value"] = [45, 45, 0]
        self.state_parms["p"]["value"] = [0, 0, -self.get_distance()]
        self.state_parms["pr"]["value"] = [0, 0, 0]
        self.state_parms["true_pivot"]["value"] = [0, 0, 0]
        self.state_parms["ortho_width"]["value"] = 10
        self.interpret_true_pivot()
        self.update_cam_parms()
        self.update_drawable(("pivot", "ray"))

    def print(self, key):
        self.log("print", severity=hou.severityType.ImportantMessage)
        if key == "cam_vals":
            t, r, p, pr = self.get_xform()
            print("r:\n", r, "t:\n", t, "p:\n", p, "pr:\n", pr)
        elif key == "centroid":
            print(self.get_centroid())
        elif key == "hud_state":
            x=1
        elif key == "kwargs":
            ui_event = str(kwargs["ui_event"])
            ui_event = ui_event.replace("\\n", "\n")
            del kwargs["ui_event"]
            print("\n")
            pprint.pprint(kwargs)
            print(ui_event)

    def refit_ui(self):
        self.log("refit_ui", severity=hou.severityType.ImportantMessage)
        self.cam.parm("resx").set(1000)
        self.cam.parm("resy").set(1000)
        size = self.viewport.size()
        ratio = size[2] / size[3]
        self.cam.parm("aspect").set(ratio)

    def reset_view(self):
        self.log("reset_view", severity=hou.severityType.ImportantMessage)
        dist = self.get_distance()
        self.state_parms["t"]["value"] = [0, 0, dist]
        self.state_parms["r"]["value"] = [45, 45, 0]
        self.state_parms["p"]["value"] = [0, 0, -dist]
        self.state_parms["pr"]["value"] = [0, 0, 0]
        self.state_parms["true_pivot"]["value"] = [0, 0, 0]
        self.state_parms["ortho_width"]["value"] = 10
        self.interpret_true_pivot()
        self.update_cam_parms()
        self.update_drawable(("pivot", "ray"))

    def set_zoom_scale(self, key):
        self.log("set_zoom_scale", severity=hou.severityType.ImportantMessage)
        if key == "Shift+-":
            self.state_parms["zoom_scale"]["value"] -= 1
        elif key == "Shift+=":
            self.state_parms["zoom_scale"]["value"] += 1

    def state_to_cam(self):
        self.log("state_to_cam", severity=hou.severityType.ImportantMessage)
        x=1

    def toggle_axes(self, kwargs, action):
        self.log("toggle_axes", severity=hou.severityType.ImportantMessage)
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
        self.update_drawable(("axis"))
        print("\n----")
        print("Axis state: ", self.axes)

    def toggle_bbox(self, kwargs, action):
        self.log("toggle_bbox", severity=hou.severityType.ImportantMessage)
        enabled = kwargs["toggle_bbox"]
        self.update_drawable(("bbox"))

    def update_drawable(self, drawable_arr):
        self.log("update_drawable", severity=hou.severityType.ImportantMessage)
        if "bbox" in drawable_arr:
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
        if "axis" in drawable_arr:
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
        if "pivot" in drawable_arr:
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
        if "ray" in drawable_arr:
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

    def update_cam_parms(self):
        self.log("update_cam_parms", severity=hou.severityType.ImportantMessage)
        t, r, p, pr = self.get_xform()
        self.cam.parmTuple("r").set(r)
        self.cam.parmTuple("t").set(t)
        self.cam.parmTuple("p").set(p)
        self.cam.parmTuple("pr").set(pr)
        self.cam.parm("orthowidth").set(self.state_parms["ortho_width"]["value"])

    def update_hud(self):
        self.log("update_hud", severity=hou.severityType.ImportantMessage)
        updates = {
            "key_mode":     {"value": self.state_state["key_mode"].capitalize()},
            "key_mode_g":   {"value": self.state_state["key_mode_arr"].index(self.state_state["key_mode"])},
            "xform_mode":   {"value": self.state_state["xform_mode"].capitalize()},
            "xform_mode_g": {"value": self.state_state["xform_mode_arr"].index(self.state_state["xform_mode"])},
            "scale_mod":    {"value": self.state_state["scale_mod"].capitalize()},
            "scale_mod_g":  {"value": self.state_state["scale_mod_arr"].index(self.state_state["scale_mod"])},
            "target":       {"value": self.state_state["target"].capitalize()},
            "target_g":     {"value": self.state_state["target_arr"].index(self.state_state["target"])},
            "viewport":     {"value": self.state_state["viewport"].capitalize()},
            "viewport_g":   {"value": self.state_state["viewport_arr"].index(self.state_state["viewport"])},
            "layout":       {"value": self.state_state["layout"].capitalize()},
            "layout_g":     {"value": self.state_state["layout_arr"].index(self.state_state["layout"])}
        }
        if self.state_state["key_mode"] == "settings":
            updates[self.state_state["setting"]]["value"] = "[" + updates[self.state_state["setting"]]["value"] + "]"
        self.viewer.hudInfo(hud_values=updates)

    def update_layout(self):
        self.log("update_layout")
        layout = self.state_state["layout"]
        if layout == "split":
            self.viewer.setViewportLayout(hou.geometryViewportLayout.QuadBottomSplit)
            if self.spreadsheet.pane().isMaximized():
                self.spreadsheet.setIsMaximized(False)
            self.refit_ui()
        elif layout == "spreadsheet":
            self.viewer.setViewportLayout(hou.geometryViewportLayout.Single)
            if not self.spreadsheet:
                self.spreadsheet = self.viewer.pane().splitVertically()
                # self.spreadsheet.createTab(hou.paneTabType.DetailsView)
                tabs = self.spreadsheet.tabs()
                tabs[0].setType(hou.paneTabType.DetailsView)
        elif layout == "full":
            self.viewer.setViewportLayout(hou.geometryViewportLayout.Single)
            if self.spreadsheet:
                self.spreadsheet.tabs()[0].close()
                self.spreadsheet = None
            self.refit_ui()

    def update_viewport_arr(self):
        self.log("update_viewports", severity=hou.severityType.ImportantMessage)
        viewports = list(self.viewer.viewports())
        viewports.reverse()
        self.state_state["viewport_arr"] = []
        for viewport in viewports:
            self.state_state["viewport_arr"].append(viewport.name())

    ##
    ##

    def onDraw(self, kwargs):
        self.axis_drawable.draw(kwargs["draw_handle"], {})
        self.pivot_drawable.draw(kwargs["draw_handle"], {})
        self.ray_drawable.draw(kwargs["draw_handle"], {})

    def onGenerate(self, kwargs):
        # Integrate with node graph
        kwargs["state_flags"]["exit_on_node_select"] = False
        # Init vars
        self.viewer.hudInfo(template=self.HUD_TEMPLATE)
        self.viewport = self.viewer.selectedViewport()
        self.state_parms = kwargs["state_parms"]
        # Call functions
        self.init_cam()
        self.cam_to_state()
        self.refit_ui()
        self.update_viewport_arr()
        self.state_state["viewport"] = self.state_state["viewport_arr"][0]
        self.update_hud()
        self.update_drawable(("axis"))
        self.init_layout()
        self.reset_view()

    def onKeyEvent(self, kwargs):
        key = kwargs["ui_event"].device().keyString()
        if key == "m":
            self.next_key_mode()
            return(True)
        elif key in ["h", "j", "k", "l", "-", "=", "Shift+h", "Shift+j",
            "Shift+k", "Shift+l", "Shift+-", "Shift+="]:
            if self.state_state["key_mode"] == "viewer":
                self.dispatch_xform(key)
            elif self.state_state["key_mode"] == "settings":
                self.dispatch_settings(key)
            return(True)
        else:
            return(False)

    def onMenuAction(self, kwargs):
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
        make_updates = (0, 0, 0, 0, 0)
        if kwargs["parm_name"] == "axis_scale":
            make_updates = (1, 0, 0, 0, 0)
        elif kwargs["parm_name"] == "distance":
            make_updates = (0, 1, 1, 1, 1)
        elif kwargs["parm_name"] == "t":
            make_updates = (0, 1, 1, 1, 1)
        elif kwargs["parm_name"] == "r":
            make_updates = (0, 1, 1, 1, 1)
        elif kwargs["parm_name"] == "p":
            make_updates = (0, 1, 1, 1, 1)
        elif kwargs["parm_name"] == "pr":
            make_updates = (0, 1, 1, 1, 1)
        elif kwargs["parm_name"] == "true_pivot":
            make_updates = (0, 1, 1, 1, 1)
        if make_updates[0]:
            self.update_drawable(("axis"))
        if make_updates[1]:
            self.interpret_true_pivot()
        if make_updates[2]:
            self.update_cam_parms()
        if make_updates[3]:
            self.update_drawable(("pivot"))
        if make_updates[4]:
            self.update_drawable(("ray"))

def make_menu(template):
    menu        = hou.ViewerStateMenu("im_view_menu", "IM View Menu")
    axis_menu   = hou.ViewerStateMenu("axes", "Axes")
    view_menu   = hou.ViewerStateMenu("view", "View")
    layout_menu = hou.ViewerStateMenu("layout_menu", "Layout")
    print_menu  = hou.ViewerStateMenu("print", "Print")

    menu.addActionItem("pivot_to_camera",   "Pivot to Camera")
    menu.addActionItem("pivot_to_centroid", "Pivot to Centroid")
    menu.addActionItem("pivot_to_origin",   "Pivot to Origin")
    menu.addSeparator()
    menu.addActionItem("frame_viewports",   "Frame Viewports")
    menu.addActionItem("reset_view",        "Reset View")
    menu.addToggleItem("toggle_bbox",       "Bounding Box", 0)
    menu.addSeparator()
    axis_menu.addActionItem("show_all_axes", "Show All")
    axis_menu.addActionItem("hide_all_axes", "Hide All")
    axis_menu.addSeparator()
    axis_menu.addToggleItem("x_axis", "X Axis", 1)
    axis_menu.addToggleItem("y_axis", "Y Axis", 1)
    axis_menu.addToggleItem("z_axis", "Z Axis", 1)
    menu.addMenu(axis_menu)
    view_menu.addActionItem("refit_ui", "Refit UI")
    view_menu.addSeparator()
    view_menu.addActionItem("top",    "Top")
    view_menu.addActionItem("bottom", "Bottom")
    view_menu.addActionItem("left",   "Left")
    view_menu.addActionItem("right",  "Right")
    view_menu.addActionItem("front",  "Front")
    view_menu.addActionItem("back",   "Back")
    menu.addMenu(view_menu)
    layout_menu.addRadioStrip("layout",     "Layout",      "spreadsheet")
    layout_menu.addRadioStripItem("layout", "spreadsheet", "Spreadsheet")
    layout_menu.addRadioStripItem("layout", "split",       "Split")
    layout_menu.addRadioStripItem("layout", "full",        "Full")
    menu.addMenu(layout_menu)
    menu.addSeparator()
    print_menu.addActionItem("print_cam_vals", "Cam Vals")
    print_menu.addActionItem("print_kwargs",   "Kwargs")
    print_menu.addActionItem("print_centroid", "Centroid")
    menu.addMenu(print_menu)
    template.bindMenu(menu)

def make_parameters(template):
    template.bindParameter(hou.parmTemplateType.Separator, "sep0",                                           toolbox=False)
    template.bindParameter(hou.parmTemplateType.Int,       "axis_scale",  "Axis Scale",    default_value=4,  toolbox=False)
    template.bindParameter(hou.parmTemplateType.Int,       "r_scale",     "R Scale",       default_value=15, toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int,       "t_scale",     "T Scale",       default_value=1,  toolbox=True)
    template.bindParameter(hou.parmTemplateType.Int,       "zoom_scale",  "Z Scale",       default_value=2,  toolbox=True)
    template.bindParameter(hou.parmTemplateType.Separator, "sep1",                                           toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,     "distance",    "Distance",      default_value=10.0)
    template.bindParameter(hou.parmTemplateType.Float,     "ortho_width", "FOV",           default_value=10.0)
    template.bindParameter(hou.parmTemplateType.Separator, "sep2",                                           toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,     "t",          "Translation",    num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,     "r",          "Rotation",       num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,     "p",          "Pivot",          num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,     "pr",         "Pivot Rotation", num_components=3, toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float,     "true_pivot", "True pivot",     num_components=3, toolbox=False)

def createViewerStateTemplate():
    template = hou.ViewerStateTemplate(\
      type_name="im_view",
      label="IM View",
      category=hou.sopNodeTypeCategory(),
      contexts=[hou.objNodeTypeCategory()])

    make_menu(template)
    make_parameters(template)

    template.bindIcon("DESKTOP_application_sierra")
    template.bindFactory(State)


    return template
