# pyright: reportMissingImports=false
import hou
import pprint
import time
import viewerstate.utils as su

class State(object):
    HUD_NAV = {
        "title": "nav",
        "rows": [
            {"id":   "mode",         "label": "mode",        "key": "M"},
            {"id":   "mode_g",       "type":  "choicegraph", "count": 4},
            {"type": "divider"},
            {"id":   "xform_mode",   "label": "xform_mode"},
            {"id":   "xform_mode_g", "type":  "choicegraph", "count": 2},
            {"id":   "zoom_mode",    "label": "zoom_mode"},
            {"id":   "zoom_mode_g",  "type":  "choicegraph", "count": 3},
            {"id":   "proj",         "label": "projection",  "count": 2},
            {"id":   "proj_g",       "type":  "choicegraph", "count": 2},
            {"id":   "target",       "label": "target"},
            {"id":   "target_g",     "type":  "choicegraph", "count": 2},
            {"id":   "viewport",     "label": "viewport"},
            {"id":   "viewport_g",   "type":  "choicegraph", "count": 4},
            {"id":   "layout",       "label": "layout"},
            {"id":   "layout_g",     "type":  "choicegraph", "count": 2},
        ]
    }
    HUD_DELTA = {
        "title": "delta",
        "rows": [
            {"id":   "mode",      "label": "Input mode" , "key":   "M"},
            {"id":   "mode_g",    "type" : "choicegraph", "count": 4, "value": 2},
            {"type": "divider"},
            {"id":   "axis_size", "label": "axis_size"},
            {"id":   "rot",       "label": "rot_delta"},
            {"id":   "tr",        "label": "tr_delta"},
            {"id":   "dist",      "label": "dist_delta"},
            {"id":   "ow",        "label": "ortho_width_delta"},
            {"id":   "clip",      "label": "clip_delta"}
        ]
    }
    HUD_FOCUS = {
        "title": "focus",
        "rows": [
            {"id":   "mode",      "label": "mode",        "key":   "M"},
            {"id":   "mode_g",    "type":  "choicegraph", "count": 4 , "value": 3},
            {"type": "divider"},
            {"id":   "attribute", "label": "attribute",   "value": "partition"},
            {"id":   "focus",     "label": "focus",       "value": 0},
            {"id":   "focus_g",   "type":  "choicegraph", "count": 10}
        ]
    }

    def __init__(s, state_name, scene_viewer):
        s.state_name = state_name
        s.viewer =     scene_viewer
        s.reset =      1
        s.axes =       [1, 1, 1]
        s.view_arr =   ("persp", "top", "bottom", "front", "back", "right", "left")
        s.mode_arr =   ("nav", "ctrl", "delta")
        s.mode =       "nav"

        s.focus_dict={
            "attribute": "partition",
            "focus":     0,
            "sel_arr":   ("attribute", "focus"),
            "sel":       "attribute"
        }
        s.nav_dict={
            "ctrl_arr":       ("xform_mode", "zoom_mode", "proj", "target", "viewport", "layout"),
            "ctrl":           "xform_mode",
            "xform_mode_arr": ("rotate", "translate"),
            "xform_mode":     "rotate",
            "zoom_mode_arr":  ("ow", "dist", "clip"),
            "zoom_mode":      "ow",
            "proj_arr":       ("ortho", "persp"),
            "proj":           "ortho",
            "target_arr":     ("cam", "pivot"),
            "target":         "cam",
            "layout_arr":     ("quadbottomsplit", "single"),
            "layout":         "quadbottomsplit",
            "viewport_arr":   (),
            "viewport":       "" 
        }
        s.startup_dict={
            "cam_reset": 1,
            "proj_arr":  ("ortho", "persp"),
            "proj":      "ortho"
        }
        s.unit_dict={
            "axis_size": 4,
            "rot":       7.5,
            "tr":        1,
            "ow":        1,
            "dist":      1,
            "clip":      2
        }
        s.delta_dict={
            "val_arr":   ("axis_size", "rot", "tr", "dist", "ow", "clip"),
            "val":       "axis_size",
            "axis_size": s.unit_dict["axis_size"],
            "rot":       s.unit_dict["rot"],
            "tr":        s.unit_dict["tr"],
            "ow":        s.unit_dict["ow"],
            "dist":      s.unit_dict["dist"],
            "clip":      s.unit_dict["clip"]
        }
        # Drawables
        dgt = hou.drawableGeometryType
        s.drawable_axis = hou.GeometryDrawable(scene_viewer=scene_viewer, geo_type=dgt.Line,
            name="drawable_axis", params={"color1": hou.Vector4((1, 1, 1, 0.3))})
        s.drawable_bbox = hou.GeometryDrawable( scene_viewer=scene_viewer, geo_type=dgt.Line,
            name="drawable_bbox", params={"color1": hou.Vector4((1, 1, 1, 0.3))})
        s.drawable_pvt = hou.GeometryDrawable(scene_viewer=scene_viewer, geo_type=dgt.Line,
            name="drawable_pvt")
        s.drawable_ray = hou.GeometryDrawable(scene_viewer=scene_viewer, geo_type=dgt.Line,
            name="drawable_ray", params={"color1": hou.Vector4((1, 0.8, 1, 0.5))})
        s.drawable_txt = hou.TextDrawable( scene_viewer=scene_viewer,
            name="drawable_txt", label="test")
        s.drawable_axis.show(True)
        s.drawable_bbox.show(False)
        s.drawable_pvt.show(True)
        s.drawable_ray.show(True)
    ##
    ##

    def cam_fit_aspect(s):
        cam = s.cam
        s.viewer_log("cam_fit_aspect", "important")
        size =  s.viewport.size()
        cam.parm("resx").set(1000)
        cam.parm("resy").set(1000)
        ratio = size[2] / size[3]
        cam.parm("aspect").set(ratio)

    def cam_from_state(s):
        s.viewer_log("cam_from_state", "important")
        x=1

    def cam_get_dir(s):
        s.viewer_log("cam_get_dir", "important")
        sp =      s.state_parms
        tru_pvt = sp["tru_pvt"]["value"]
        tr =      sp["tr"]["value"]
        s.viewer_log(hou.Vector3(tru_pvt) - hou.Vector3(tr), "normal")
        return

    def cam_get_dist(s):
        s.viewer_log("cam_get_dist", "important")
        dist = s.state_parms["dist"]["value"]
        return dist

    def cam_get_len(s):
        s.viewer_log("cam_get_len", "important")
        sp =  s.state_parms
        tr =  sp["tr"]["value"]
        pvt = sp["pvt"]["value"]
        len = tr[2]
        return len

    def cam_get_xform(s):
        sp = s.state_parms
        self.viewer_log("cam_get_xform", "important")
        r = sp["r"]["value"]
        return r

    def cam_init(s):
        s.viewer_log("cam_init", "important")
        viewport = s.viewer.curViewport()
        # Check if keycam exists and if not, make it.
        child_arr = [ node.name() for node in hou.node("/obj").children() ]
        if "keycam" not in child_arr:
            cam = hou.node("/obj").createNode("cam")
            cam.setName("keycam")
        # Define variables
        tr =  [0, 0, 0]
        rot = [0, 0, 0]
        pvt = [0, 0, 0]
        ow =  1
        # Check is default cam or not
        cam = viewport.camera()
        if cam == None:
            default_cam = viewport.defaultCamera()
            tr =  default_cam.translation()
            rot = default_cam.rotation()
            pvt = default_cam.pivot()
            ow =  default_cam.orthoWidth()
        else:
            tr =  cam.evalParmTuple("t")
            rot = cam.evalParmTuple("r")
            pvt = cam.evalParmTuple("p")
            ow =  cam.evalParm("orthowidth")
        s.cam = hou.node("/obj/keycam")
        s.viewport.setCamera(s.cam)
        s.viewport.lockCameraToView(True)

    def cam_move_pvt(s):
        s.viewer_log("cam_move_pvt", "important")
        sp =     s.state_parms
        target = s.nav_dict["target"]
        if target == "cam":
            tr = sp["tr"]["value"]
            sp["tru_pvt"]["value"] = list(tr)
        elif target == "centroid":
            centroid = s.geo_get_centroid()
        elif target == "origin":
            sp["tr"]["value"] =      [0, 0, s.cam_get_dist()]
            sp["rot"]["value"] =     [45, 45, 0]
            sp["pvt"]["value"] =     [0, 0, -s.cam_get_dist()]
            sp["pvt_rot"]["value"] = [0, 0, 0]
            sp["tru_pvt"]["value"] = [0, 0, 0]
            sp["ow"]["value"] =      10
        elif target == "ray":
            x=1
        s.cam_update()
        s.drawable_update_pvt()
        s.drawable_update_ray()

    def cam_next_proj(s):
        s.viewer_log("cam_next_proj", "important")
        cam = s.cam
        proj_parm = cam.parm("projection")
        proj = proj_parm.evalAsString() 
        if   proj == "ortho":       proj_parm.set("perspective")
        elif proj == "perspective": proj_parm.set("ortho")

    def cam_proj_update(s):
        s.viewer_log("cam_proj_update", "important")
        cam = s.cam
        nd = s.nav_dict
        proj = nd["proj"]
        proj_parm = cam.parm("projection")
        if   proj == "ortho": proj_parm.set("ortho")
        elif proj == "persp": proj_parm.set("perspective")
        s.geo_frame()

    def cam_reset(s):
        s.viewer_log("cam_reset", "important")
        dist = s.cam_get_dist()
        sp =   s.state_parms
        sp["tr"]["value"] =      [0, 0, dist]
        sp["rot"]["value"] =     [315, 45, 0]
        sp["pvt"]["value"] =     [0, 0, -dist]
        sp["pvt_rot"]["value"] = [0, 0, 0]
        sp["tru_pvt"]["value"] = [0, 0, 0]
        sp["ow"]["value"] =      10
        s.cam_update()
        s.drawable_update_pvt()
        s.drawable_update_ray()

    def cam_rotate(s, key):
        s.viewer_log("cam_rotate", "important")
        dd =        s.delta_dict
        sp =        s.state_parms
        rot =       list(sp["rot"]["value"])
        rot_delta = dd["rot"]
        if   key == "h": rot[1] = (rot[1] + rot_delta) % 360
        elif key == "j": rot[0] = (rot[0] - rot_delta) % 360
        elif key == "k": rot[0] = (rot[0] + rot_delta) % 360
        elif key == "l": rot[1] = (rot[1] - rot_delta) % 360
        sp["rot"]["value"] = rot

    def cam_to_state(s):
        s.viewer_log("cam_to_state", "important")
        cam = s.cam
        sp = s.state_parms
        sp["tr"]["value"] =      list(cam.evalParmTuple("t"))
        sp["pvt"]["value"] =     list(cam.evalParmTuple("p"))
        sp["rot"]["value"] =     list(cam.evalParmTuple("r"))
        sp["pvt_rot"]["value"] = list(cam.evalParmTuple("pr"))
        sp["ow"]["value"] =      cam.evalParm("orthowidth")

    def cam_translate(s, key):
        s.viewer_log("cam_translate", "important")
        dd = s.delta_dict
        sp = s.state_parms
        # tru_pvt = list(sp["tru_pvt"]["value"])
        s.cam_get_dir()
        pvt =      list(sp["pvt"]["value"])
        tr_delta = dd["tr"]
        if   key == "h": pvt[0] = pvt[0] - tr_delta
        elif key == "j": pvt[1] = pvt[1] - tr_delta
        elif key == "k": pvt[1] = pvt[1] + tr_delta
        elif key == "l": pvt[0] = pvt[0] + tr_delta
        sp["pvt"]["value"] = pvt

    def cam_update(s):
        s.viewer_log("cam_update", "important")
        cam = s.cam
        sp = s.state_parms
        # Convert tru_pivot
        tru_pvt = 1
        if tru_pvt:
            tru_pvt =               sp["tru_pvt"]["value"]
            dist =                  sp["dist"]["value"]
            sp["tr"]["value"][0] =  tru_pvt[0]
            sp["tr"]["value"][1] =  tru_pvt[1]
            sp["tr"]["value"][2] =  dist
            sp["pvt"]["value"][0] = 0
            sp["pvt"]["value"][1] = 0
            sp["pvt"]["value"][2] = tru_pvt[2] - dist
        # Transfer state parameters to camera
        cam.parmTuple("r").set(sp["rot"]["value"])
        cam.parmTuple("t").set(sp["tr"]["value"])
        cam.parmTuple("p").set(sp["pvt"]["value"])
        cam.parmTuple("pr").set(sp["pvt_rot"]["value"])
        cam.parm("orthowidth").set(sp["ow"]["value"])

    def cam_xform(s, key):
        s.viewer_log("cam_xform", "important")
        nd = s.nav_dict
        type = s.viewport.type()
        gvt = hou.geometryViewportType
        if s.viewer.curViewport().type() == gvt.Perspective: # pyright: ignore
            if key in ("Shift+h", "Shift+j", "Shift+k", "Shift+l"):
                if   nd["xform_mode"] == "rotate":    s.cam_translate(key[-1])
                elif nd["xform_mode"] == "translate": s.cam_rotate(key[-1])
            elif key in ("h", "j", "k", "l"):
                if   nd["xform_mode"] == "rotate":    s.cam_rotate(key)
                elif nd["xform_mode"] == "translate": s.cam_translate(key)
            s.cam_update()
            s.drawable_update_pvt()
            s.drawable_update_ray()
        elif type == gvt.Top:    s.cam_xform_flat(key, "top")
        elif type == gvt.Bottom: s.cam_xform_flat(key, "bottom")
        elif type == gvt.Front:  s.cam_xform_flat(key, "front")
        elif type == gvt.Back:   s.cam_xform_flat(key, "back")
        elif type == gvt.Right:  s.cam_xform_flat(key, "right")
        elif type == gvt.Left:   s.cam_xform_flat(key, "left")

    def cam_xform_flat(s, key, view_type):
        s.viewer_log("cam_xform_flat", "important")
        nd = s.nav_dict
        viewport_name = nd["viewport"]
        viewport_arr =  s.viewer.viewports()
        name_arr =      [ x.name() for x in viewport_arr ]
        idx =           name_arr.index(viewport_name)
        viewport =      viewport_arr[idx]
        idx_arr =       [0, 0]
        if   view_type == "top":    idx_arr = [0, 2]
        elif view_type == "bottom": idx_arr = [2, 0]
        elif view_type == "front":  idx_arr = [0, 1]
        elif view_type == "back":   idx_arr = [1, 0]
        elif view_type == "right":  idx_arr = [2, 1]
        elif view_type == "left":   idx_arr = [1, 2]
        cam = viewport.defaultCamera() # pyright: ignore
        t =  list( cam.translation() )
        ti = s.val_dict["tr"]
        if   key == "h": t[idx_arr[0]] += ti
        elif key == "j": t[idx_arr[1]] += ti
        elif key == "k": t[idx_arr[1]] -= ti
        elif key == "l": t[idx_arr[0]] -= ti
        cam.setTranslation(t)

    def cam_xform_update(s):
        s.viewer_log("cam_xform_update", "important")

    def cam_zoom(s, key):
        s.viewer_log("cam_zoom", "important")
        dd =         s.delta_dict
        nd =         s.nav_dict
        sp =         s.state_parms
        proj =       nd["proj"]
        ow_delta =   dd["ow"]
        dist_delta = dd["dist"]
        if nd["proj"] == "persp":
            #if   key == "Shift+-":
            #elif key == "Shift+=":
            if   key == "=": sp["dist"]["value"] -= dist_delta
            elif key == "-": sp["dist"]["value"] += dist_delta
        elif nd["proj"] == "ortho":
            if nd["zoom_mode"] == "ow":
                #if   key == "Shift+-":
                #elif key == "Shift+=":
                if   key == "-": sp["ow"]["value"] += ow_delta
                elif key == "=": sp["ow"]["value"] -= ow_delta
            elif nd["zoom_mode"] == "dist":
                #if   key == "Shift+-":
                #elif key == "Shift+=":
                if   key == "=": sp["dist"]["value"] += dist_delta
                elif key == "-": sp["dist"]["value"] -= dist_delta
            elif nd["zoom_mode"] == "clip":
                return
        s.cam_update()
        s.drawable_update_pvt()
        s.drawable_update_ray()

    def drawable_init(s):
        s.drawable_update_axis()

    def drawable_toggle_axis(s, kwargs, action):
        s.viewer_log("drawable_toggle_axes", "important")
        if   action == "show_all_axes": s.axes = [1, 1, 1]
        elif action == "hide_all_axes": s.axes = [0, 0, 0]
        elif action == "x_axis":        s.axes[0] = kwargs["x_axis"]
        elif action == "y_axis":        s.axes[1] = kwargs["y_axis"]
        elif action == "z_axis":        s.axes[2] = kwargs["z_axis"]
        s.drawable_update_axis()
        s.viewer_log("Axis state: " + str(s.axis), "important")

    def drawable_toggle_bbx(s, kwargs, action):
        s.viewer_log("drawable_toggle_bbx", "important")
        enabled = kwargs["toggle_bbx"]
        s.drawable_update_bbx()

    def drawable_update_axis(s):
        s.viewer_log("drawable_update_axis", "important")
        axis_size = s.delta_dict["axis_size"]
        geo = hou.Geometry()
        geo.addAttrib(hou.attribType.Point, "Cd", (1, 1, 1))
        for idx in (0, 1, 2):
            if s.axes[idx]:
                p0 =      [0, 0, 0]
                p1 =      [0, 0, 0]
                p0[idx] = -axis_size
                p1[idx] = axis_size
                pts =     geo.createPoints((p0, p1))
                cd =      [0, 0, 0]
                cd[idx] = 1
                pts[0].setAttribValue("Cd", cd)
                pts[1].setAttribValue("Cd", cd)
                prim = geo.createPolygon(is_closed=False)
                prim.addVertex(pts[0])
                prim.addVertex(pts[1])
        s.drawable_axis.setGeometry(geo)
        s.drawable_axis.setParams({"fade_factor": 0.0})

    def drawable_update_bbox(self):
        s.viewer_log("drawable_update_bbox", "important")
        geo = s.get_get()
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

    def drawable_update_pvt(s):
        s.viewer_log("drawable_update_pvt", "important")
        sp =          s.state_parms
        rot =         list(sp["rot"]["value"])
        tr =          list(sp["tr"]["value"])
        pvt =         list(sp["pvt"]["value"])
        ow =          sp["ow"]["value"]
        scale =       ow * 0.0075
        P =           hou.Vector3(pvt) + hou.Vector3(tr)
        geo =         hou.Geometry()
        circle_verb = hou.sopNodeTypeCategory().nodeVerb("circle")
        circle_verb.setParms({"type": 1, "r": rot, "t": P, "scale": scale})
        circle_verb.execute(geo, [])
        s.drawable_pvt.setGeometry(geo)
        s.drawable_pvt.setParams({
            "color1": hou.Vector4(0.0, 0.0, 1, 1),
            "fade_factor": 1.0
        })

    def drawable_update_ray(s):
        s.viewer_log("drawable_update_ray", "important")
        sp = s.state_parms
        tr =       sp["tr"]["value"]
        rot =      sp["rot"]["value"]
        pvt =      sp["pvt"]["value"]
        tru_pvt =  sp["tru_pvt"]["value"]
        rot =      hou.hmath.buildRotate(rot)
        cam_P =    hou.Vector3(0, 0, s.cam_get_len()) * rot
        cam_P +=   hou.Vector3(tru_pvt[0], tru_pvt[1], tru_pvt[2])
        pvt_P =    hou.Vector3(tr) + hou.Vector3(pvt)
        geo =      hou.Geometry()
        pts =      geo.createPoints((cam_P, pvt_P))
        prim =     geo.createPolygon()
        prim.addVertex(pts[0])
        prim.addVertex(pts[1])
        s.drawable_ray.setGeometry(geo)

    def geo_frame(s):
        s.viewer_log("geo_frame", "important")
        [ viewport.frameAll() for viewport in s.viewer.viewports() ]
        s.cam_to_state()
        s.drawable_update_pvt()

    def geo_get_centroid(s):
        s.viewer_log("geo_get_centroid", "important")
        geo = s.geo_get()
        result_geo = hou.Geometry()
        centroid_verb = hou.sopNodeTypeCategory().nodeVerb("extractcentroid")
        centroid_verb.setParms({"partitiontype": 2})
        centroid_verb.execute(result_geo, [geo])
        pt = result_geo.point(0)
        centroid = pt.position()
        return centroid

    def geo_get_extrema(s):
        s.viewer_log("geo_get_extrema", "important")
        geo = s.geo_get()
        bbx = geo.boundingBox()

    def geo_get(s):
        s.viewer_log("geo_get", "important")
        display_node = s.viewer.pwd().displayNode()
        geo = display_node.geometry()
        return geo

    def hud_change_focus(s, key):
        s.viewer_log("hud_change_focus", "important")
        fd = s.focus_dict
        if   key == "j": fd["sel"] = s.list_next(fd["sel_arr"], fd["sel"])
        elif key == "k": fd["sel"] = s.list_prev(fd["sel_arr"], fd["sel"]) 
        elif key in ("h", "l"):
            attr = s.focus["attr"]
            attr = hou.ui.readInput("Attribute", buttons=("OK", "Cancel"), initial_contents=attr)
            if attr[0] == 0: fd["attr"] = attr[1]
        s.hud_update("focus")

    def hud_change_ctrl(s, key):
        s.viewer_log("hud_change_ctrl", "important")
        nd = s.nav_dict
        ctrl =      nd["ctrl"]
        ctrl_arr =  nd["ctrl_arr"]
        val =       nd[ctrl]
        val_arr =   nd[ctrl + "_arr"]
        # Hilite Ctrl
        if key == "j":
            idx = ctrl_arr.index(ctrl)
            idx += 1
            idx %= len(ctrl_arr)
            nd["ctrl"] = ctrl_arr[idx]
        elif key == "k":
            idx = ctrl_arr.index(ctrl)
            idx -= 1
            idx %= len(ctrl_arr)
            nd["ctrl"] = ctrl_arr[idx]
        # Change Ctrl Value
        elif key == "h":
            idx = val_arr.index(val)
            idx -= 1
            idx %= len(val_arr)
            nd[ctrl] = val_arr[idx]
        elif key == "l":
            idx = val_arr.index(val)
            idx += 1
            idx %= len(val_arr)
            nd[ctrl] = val_arr[idx]
        # Post-process
        if   nd["ctrl"] == "proj":   s.cam_proj_update()
        elif nd["ctrl"] == "layout": s.viewport_layout_set()
        s.hud_update(s.mode)

    def hud_change_val(s, key):
        s.viewer_log("hud_change_val", "important")
        dd =      s.delta_dict
        ud =      s.unit_dict
        val =     vd["val"]
        val_arr = vd["val_arr"]
        if   key == "h": dd[val] -=  ud[val]
        elif key == "j": vd["val"] = s.list_prev(val_arr, val)
        elif key == "k": vd["val"] = s.list_next(val_arr, val)
        elif key == "l": vd[val] +=  dd[val]
        s.hud_update("val_dict")

    def hud_init(s):
        s.viewer_log("hud_init", "important")
        s.viewer.hudInfo(template=s.HUD_NAV)
        nd = s.nav_dict
        updates = {
            "mode":         {"value": s.mode},
            "mode_g":       {"value": s.mode_arr.index(s.mode)},
            "xform_mode":   {"value": nd["xform_mode"]},
            "xform_mode_g": {"value": nd["xform_mode_arr"].index(nd["xform_mode"])},
            "zoom_mode":    {"value": nd["zoom_mode"]},
            "zoom_mode_g":  {"value": nd["zoom_mode_arr"].index(nd["zoom_mode"])},
            "proj":         {"value": nd["proj"]},
            "proj_g":       {"value": nd["proj_arr"].index(nd["proj"])},
            "target":       {"value": nd["target"]},
            "target_g":     {"value": nd["target_arr"].index(nd["target"])},
            "viewport":     {"value": nd["viewport"]},
            "viewport_g":   {"value": nd["viewport_arr"].index(nd["viewport"])},
            "layout":       {"value": nd["layout"]},
            "layout_g":     {"value": nd["layout_arr"].index(nd["layout"])}
        }
        s.viewer.hudInfo(hud_values=updates)

    def hud_next_mode(s):
        s.viewer_log("hud_next_mode", "important")
        ma =     s.mode_arr
        idx =    ma.index(s.mode)
        idx +=   1
        idx %=   len(ma)
        next =   s.mode_arr[idx]
        s.mode = next
        s.hud_update(next)

    def hud_prev_mode(s):
        s.viewer_log("hud_prev_mode", "important")
        ma =     s.mode_arr
        idx =    ma.index(s.mode)
        idx -=   1
        idx %=   len(ma)
        prev =   s.mode_arr[idx]
        s.mode = prev
        s.hud_update(prev)

    def hud_update(s, hud):
        s.viewer_log("hud_update", "important")
        nd = s.nav_dict
        dd = s.delta_dict
        fd = s.focus_dict
        if hud == "nav":
            s.viewer.hudInfo(template=s.HUD_NAV)
            updates={
                "mode":         {"value": s.mode},
                "mode_g":       {"value": s.mode_arr.index(s.mode)},
                "xform_mode":   {"value": nd["xform_mode"]},
                "xform_mode_g": {"value": nd["xform_mode_arr"].index(nd["xform_mode"])},
                "zoom_mode":    {"value": nd["zoom_mode"]},
                "zoom_mode_g":  {"value": nd["zoom_mode_arr"].index(nd["zoom_mode"])},
                "proj":         {"value": nd["proj"]},
                "proj_g":       {"value": nd["proj_arr"].index(nd["proj"])},
                "target":       {"value": nd["target"]},
                "target_g":     {"value": nd["target_arr"].index(nd["target"])},
                "viewport":     {"value": nd["viewport"]},
                "viewport_g":   {"value": nd["viewport_arr"].index(nd["viewport"])},
                "layout":       {"value": nd["layout"]},
                "layout_g":     {"value": nd["layout_arr"].index(nd["layout"])}
            }
            s.viewer.hudInfo(hud_values=updates)

        elif hud == "ctrl":
            s.viewer.hudInfo(template=s.HUD_NAV)
            updates={
                "mode":         {"value": s.mode},
                "mode_g":       {"value": s.mode_arr.index(s.mode)},
                "xform_mode":   {"value": nd["xform_mode"]},
                "xform_mode_g": {"value": nd["xform_mode_arr"].index(nd["xform_mode"])},
                "zoom_mode":    {"value": nd["zoom_mode"]},
                "zoom_mode_g":  {"value": nd["zoom_mode_arr"].index(nd["zoom_mode"])},
                "proj":         {"value": nd["proj"]},
                "proj_g":       {"value": nd["proj_arr"].index(nd["proj"])},
                "target":       {"value": nd["target"]},
                "target_g":     {"value": nd["target_arr"].index(nd["target"])},
                "viewport":     {"value": nd["viewport"]},
                "viewport_g":   {"value": nd["viewport_arr"].index(nd["viewport"])},
                "layout":       {"value": nd["layout"]},
                "layout_g":     {"value": nd["layout_arr"].index(nd["layout"])}
            }
            ctrl = nd["ctrl"]
            updates[ctrl]["value"] = "[" + updates[ctrl]["value"] + "]"
            s.viewer.hudInfo(hud_values=updates)

        elif hud == "delta":
            s.viewer.hudInfo(template=s.HUD_DELTA)
            updates={
                "mode":      {"value": "delta"},
                "mode_g":    {"value": 2},
                "axis_size": {"value": str(dd["axis_size"])},
                "rot":       {"value": str(dd["rot"])},
                "tr":        {"value": str(dd["tr"])},
                "ow":        {"value": str(dd["ow"])},
                "dist":      {"value": str(dd["dist"])},
                "clip":      {"value": str(dd["clip"])}
            }
            updates[dd["val"]]["value"] = "[" + updates[dd["val"]]["value"] + "]"
            s.viewer.hudInfo(hud_values=updates)

        elif hud == "focus":
            s.viewer.hudInfo(template=s.HUD_FOCUS)
            updates={
                "attr":    {"value": fd["attribute"]},
                "focus":   {"value": str(0)},
                "focus_g": {"value": 0},
            }
            sel = s.focus["sel"]
            updates[sel]["value"] = "[" + updates[sel]["value"] + "]"
            s.viewer.hudInfo(hud_values=updates)

    def init_parms(s):
        s.viewer_log("init_parms", "important")
        cam = s.cam
        sp = s.state_parms
        sp["tr"]["value"] =      list(cam.evalParmTuple("t"))
        sp["pvt"]["value"] =     list(cam.evalParmTuple("p"))
        sp["rot"]["value"] =     list(cam.evalParmTuple("r"))
        sp["pvt_rot"]["value"] = list(cam.evalParmTuple("pr"))
        sp["ow"]["value"] =      cam.evalParm("orthowidth")

    def init_viewport_arr(s):
        s.viewer_log("init_viewport_arr", "important")
        nd = s.nav_dict
        nd["viewport_arr"] = [ viewport.name() for viewport in s.viewer.viewports() ]
        nd["viewport"] = nd["viewport_arr"][0]

    def list_next(s, list, sel):
        idx = list.index(sel)
        idx = (idx + 1) % len(list)
        return idx

    def list_prev(s, list, sel):
        idx = list.index(sel)
        idx = (idx - 1) % len(list)
        return idx

    def print(s, key):
        s.viewer_log("print", "important")
        sp = s.state_parms
        if key == "cam_vals":
            t = sp["t"]["value"]
            r = sp["r"]["value"]
            p = sp["p"]["value"]
            p = sp["pr"]["value"]
            s.viewer_log("r:\n", r, "t:\n", t, "p:\n", p, "pr:\n", pr, "normal")
        elif key == "centroid":
            s.viewer_log(s.geo_get_centroid(), "normal")
        elif key == "hud_state":
            x=1
        elif key == "viewport":
            s.viewer_log(s.nav_dict["viewport"], "normal")

    def print_kwargs(s, kwargs):
        s.viewer_log("print_kwargs", "important")
        s.viewer_log_separator()
        ui_event = str(kwargs["ui_event"])
        ui_event = ui_event.replace("\\n", "\n")
        del kwargs["ui_event"]
        s.viewer_log_separator()
        s.viewer_log(ui_event, "normal")

    def viewport_arr_update(s):
        s.viewer_log("viewport_arr_update", "important")
        viewport_arr = list(s.viewer.viewports())
        viewport_arr.reverse()
        s.nav_dict["viewport_arr"] = [ viewport.name() for viewport in viewport_arr ]

    def viewport_layout_init(s):
        s.viewer_log("viewport_layout_init", "important")
        gvl = hou.geometryViewportLayout
        nd = s.nav_dict
        layout = s.viewer.viewportLayout()
        if   layout == gvl.Single         : nd["layout"] = "single"
        elif layout == gvl.QuadBottomSplit: nd["layout"] = "quadbottomsplit"

    def viewport_layout_set(s):
        s.viewer_log("viewport_layout_set", "important")
        gvl = hou.geometryViewportLayout
        layout = s.nav_dict["layout"]
        if   layout == "quadbottomsplit": s.viewer.setViewportLayout(gvl.QuadBottomSplit)
        elif layout == "single"         : s.viewer.setViewportLayout(gvl.Single)
        s.cam_fit_aspect()

    def viewport_rotate(s):
        s.viewer_log("viewport_rotate", "important")
        viewport_arr = s.viewer.viewports()
        viewport_arr[2].changeName('pass')
        # v_name_arr = [v.name() for v in v_arr]
        # v_type_arr = [v.type() for v in v_arr]
        # v_name_arr = v_name_arr[1:] + [v_name_arr[0]]
        # v_type_arr = v_type_arr[1:] + [v_type_arr[0]]
        # for i, v in enumerate(v_arr):
            # v.changeName("v" * i)
        # for i, v in enumerate(v_arr):
            # v.changeName(v_name_arr[i])
            # v.changeType(v_type_arr[i])
        # s.viewer_log(v_name_arr, "normal")
        # s.viewer_log(v_type_arr, "normal")

    def viewport_type_set(s, view):
        s.viewer_log("viewport_type_set", "important")
        viewport = s.viewer.viewports()[-1]
        if view == "persp":
            s.cam_init()
        if view == "top":
            viewport.changeType(hou.geometryViewportType.Top)

    def viewer_log(s, message, level):
        if   level == "normal"   : s.log(message)
        elif level == "important": s.log(message, severity=hou.severityType.ImportantMessage)

    def viewer_log_separator(s):
        s.viewer_log("-------------------------", "normal")
    ##
    ##

    def onDraw(s, kwargs):
        dh = kwargs["draw_handle"]
        s.drawable_axis.draw(dh, {})
        s.drawable_pvt.draw(dh, {})
        s.drawable_ray.draw(dh, {})
        s.drawable_txt.draw(dh, {})

    def onGenerate(s, kwargs):
        s.viewer_log_separator()
        s.viewer_log("onGenerate", "important")
        # Integrate with node graph
        kwargs["state_flags"]["exit_on_node_select"] = False
        # Init vars
        s.viewport    = s.viewer.selectedViewport()
        s.state_parms = kwargs["state_parms"]
        # Call functions
        s.cam_init()
        s.init_parms()
        s.init_viewport_arr()
        s.viewport_layout_init()
        s.hud_init()
        s.drawable_init()
        s.cam_fit_aspect()
        nd = s.startup_dict
        if nd["cam_reset"]:
            s.cam_reset()

    def onKeyEvent(s, kwargs):
        s.viewer_log_separator()
        s.viewer_log("onKeyEvent", "important")
        m = s.mode
        key = kwargs["ui_event"].device().keyString()
        if key == "Shift+m":
            s.hud_prev_mode()
            return True
        elif key[-1] in ("h", "j", "k", "l"):
            if   m == "nav":   s.cam_xform(key)
            elif m == "ctrl":  s.hud_change_ctrl(key)
            elif m == "delta": s.hud_change_delta(key)
            elif m == "focus": s.hud_change_focus(key)
            return True
        elif key == "m":
            s.hud_next_mode()
            return True
        elif key == "o":
            s.cam_next_proj()    
            return True
        elif key[-1] in ("-", "="):
            s.cam_zoom(key)
            return True
        else:
            return False

    def onMenuAction(s, kwargs):
        s.viewer_log_separator()
        s.viewer_log("onMenuAction", "important")
        action = kwargs["menu_item"]
        if   action == "pvt_to_ray":      s.cam_move_pvt("ray")
        elif action == "pvt_to_camera":   s.cam_move_pvt("camera")
        elif action == "pvt_to_centroid": s.cam_move_pvt("centroid")
        elif action == "pvt_to_origin":   s.cam_move_pvt("origin")
        elif action == "geo_frame":       s.geo_frame()
        elif action == "cam_reset":       s.cam_reset()
        elif action == "cam_fit_aspect":  s.cam_fit_aspect()
        elif action == "toggle_bbx":      s.toggle_bbox(kwargs, action)
        # Axes menu
        elif action in ["show_all_axes", "hide_all_axes", "x_axis", "y_axis", "z_axis"]:
            x=1
        # View Menu
        elif action == "rotate_viewports":    s.rotate_viewports()
        # Test menu
        elif action == "cam_to_state":        s.cam_to_state()
        elif action == "viewport_arr_update": s.viewport_arr_update()
        # Print menu
        elif action == "print_cam_vals":      s.print("cam_vals")
        elif action == "print_centroid":      s.print("centroid")
        elif action == "print_kwargs":        s.print_kwargs(kwargs)
        elif action == "print_viewport":      s.print("viewport")
        # def onMouseEvent(s, kwargs):
        #     node = kwargs["node"]
        #     ui_event = kwargs["ui_event"]
        #     scrx = ui_event.device().mouseX()
        #     scry = ui_event.device().mouseY()
        #     if ui_event.reason() == hou.uiEventReason.Picked\
        #         or ui_event.reason() == hou.uiEventReason.Start:
        #         origin, dir = ui_event.ray()
        #         prim = s.viewport.queryPrimAtPixel(None, round(scrx), round(scry))
        #         if prim == None:
        #             return
        #         else:
        #             val = prim.attribValue("sprue")
        #             if val == 0:
        #                 stash1 = node.node("stash1")
        #                 stash1.parm("stashinput").pressButton()
        #             else:
        #                 node.node("switch2").parm("input").set(1)
        #                 node.node("stash1").parm("stashinput").pressButton()
        #                 node.node("switch2").parm("input").set(0)

    def onParmChangeEvent(s, kwargs):
        updates = (0, 0, 0, 0, 0)
        pn = kwargs["parm_name"]
        if   pn == "axis_size": updates = (1, 0, 0, 0, 0)
        elif pn == "dist":      updates = (0, 1, 1, 1, 1)
        elif pn == "tr":        updates = (0, 1, 1, 1, 1)
        elif pn == "rot":       updates = (0, 1, 1, 1, 1)
        elif pn == "pvt":       updates = (0, 1, 1, 1, 1)
        elif pn == "pvt_rot":   updates = (0, 1, 1, 1, 1)
        elif pn == "tru_pvt":  updates = (0, 1, 1, 1, 1)
        if updates[0]: s.drawable_update_axis()
        if updates[1]: s.cam_update()
        if updates[2]: s.cam_update()
        if updates[3]: s.drawable_update_pvt()
        if updates[4]: s.drawable_update_pvt()

def make_menu(template):
    menu = hou.ViewerStateMenu("keycam_menu", "keycam_menu")
    menu.addActionItem("pvt_to_ray",          "pvt_to_ray")
    menu.addActionItem("pvt_to_cam",          "pvt_to_cam")
    menu.addActionItem("pvt_to_centroid",     "pvt_to_centroid")
    menu.addActionItem("pvt_to_origin",       "pvt_to_origin")
    menu.addSeparator()
    menu.addActionItem("cam_reset",           "cam_reset")
    menu.addActionItem("cam_fit_aspect",      "cam_fit_aspect")
    menu.addActionItem("geo_frame",           "geo_frame")
    menu.addActionItem("rotate_viewports",    "rotate_viewports")
    menu.addSeparator()
    menu.addActionItem("show_all_axes",       "show_all_axes")
    menu.addActionItem("hide_all_axes",       "hide_all_axes")
    menu.addToggleItem("x_axis",              "x_axis", 1)
    menu.addToggleItem("y_axis",              "y_axis", 1)
    menu.addToggleItem("z_axis",              "z_axis", 1)
    menu.addToggleItem("toggle_bbox",         "toggle_bbox", 0)
    menu.addSeparator()
    menu.addActionItem("print_cam_vals",      "print_cam_vals")
    menu.addActionItem("print_kwargs",        "print_kwargs")
    menu.addActionItem("print_centroid",      "print_centroid")
    menu.addActionItem("print_viewport",      "print_viewport")
    menu.addSeparator()
    menu.addActionItem("cam_to_state",        "cam_to_state")
    menu.addActionItem("viewport_arr_update", "viewport_arr_update")
    template.bindMenu(menu)

def make_parameters(template):
    t = template
    ptt = hou.parmTemplateType
    t.bindParameter(ptt.Float,     "axis_size", "axis_size", default_value=2.0, toolbox=False)
    t.bindParameter(ptt.Separator, "sep0",      toolbox=False)
    t.bindParameter(ptt.Float,     "dist",      "dist",      default_value=10.0)
    t.bindParameter(ptt.Float,     "ow",        "ow",        default_value=10.0)
    t.bindParameter(ptt.Separator, "sep1",      toolbox=False)
    t.bindParameter(ptt.Float,     "tr",        "tr",        num_components=3,  toolbox=False)
    t.bindParameter(ptt.Float,     "rot",       "rot",       num_components=3,  toolbox=False)
    t.bindParameter(ptt.Float,     "pvt",       "pvt",       num_components=3,  toolbox=False)
    t.bindParameter(ptt.Float,     "pvt_rot",   "pvt_rot",   num_components=3,  toolbox=False)
    t.bindParameter(ptt.Separator, "sep2",      toolbox=False)
    t.bindParameter(ptt.Float,     "up",        "up",        num_components=3,  toolbox=False)
    t.bindParameter(ptt.Float,     "tru_pvt",   "tru_pvt",   num_components=3,  toolbox=False)

def createViewerStateTemplate():
    template = hou.ViewerStateTemplate(\
      type_name="keycam",
      label="keycam",
      category=hou.sopNodeTypeCategory(),
      contexts=[hou.objNodeTypeCategory()])
    make_menu(template)
    make_parameters(template)
    template.bindIcon("DESKTOP_application_sierra")
    template.bindFactory(State)
    return template
