# pyright: reportMissingImports=false

import hou
import pprint
import viewerstate.utils as su

class State(object):
    SETTING_HUD = {
        "title": "View",
        "rows": [
            {"id"   : "state_mode"       , "label" : "State Mode"  , "key"   : "M"},
            {"id"   : "state_mode_graph" , "type"  : "choicegraph" , "count" : 4  },
            {"type" : "divider"                                                   },
            {"id"   : "xform_mode"       , "label" : "Xform mode"                 },
            {"id"   : "xform_mode_graph" , "type"  : "choicegraph" , "count" : 2  },
            {"id"   : "zoom_mode"        , "label" : "Zoom mode"                  },
            {"id"   : "zoom_mode_graph"  , "type"  : "choicegraph" , "count" : 3  },
            {"id"   : "proj"             , "label" : "Projection"  , "count" : 2  },
            {"id"   : "proj_graph"       , "type"  : "choicegraph" , "count" : 2  },
            {"id"   : "target"           , "label" : "Target"                     },
            {"id"   : "target_graph"     , "type"  : "choicegraph" , "count" : 2  },
            {"id"   : "viewport"         , "label" : "Viewport"                   },
            {"id"   : "viewport_graph"   , "type"  : "choicegraph" , "count" : 4  },
            {"id"   : "layout"           , "label" : "Layout"                     },
            {"id"   : "layout_graph"     , "type"  : "choicegraph" , "count" : 2  },
        ]
    }

    VAL_HUD = {
        "title": "Values",
        "rows": [
            {"id"   : "state_mode"       , "label" : "Input mode"  , "key"   : "M"            },
            {"id"   : "state_mode_graph" , "type"  : "choicegraph" , "count" : 4, "value" : 2 },
            {"type" : "divider"                                                               },
            {"id"   : "axis_size"        , "label" : "Axis Size"                              },
            {"id"   : "ri"               , "label" : "Rotation Interval"                      },
            {"id"   : "ti"               , "label" : "Translation Interval"                   },
            {"id"   : "di"               , "label" : "Distance Interval"                      },
            {"id"   : "owi"              , "label" : "Ortho Width Interval"                   },
            {"id"   : "ci"               , "label" : "Clip Interval"                          }
        ]
    }

    FOCUS_HUD = {
        "title": "Focus",
        "rows": [
            {"id"   : "state_mode"       , "label" : "Input Mode"  , "key"   : "M"             },
            {"id"   : "state_mode_graph" , "type"  : "choicegraph" , "count" : 4 , "value" : 3 },
            {"type" : "divider"                                                                },
            {"id"   : "attribute"        , "label" : "Attribute"   , "value" : "partition"     },
            {"id"   : "focus"            , "label" : "Focus"       , "value" : 0               },
            {"id"   : "focus_graph"      , "type"  : "choicegraph" , "count" : 10              }
        ]
    }

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.viewer     = scene_viewer
        self.reset      = 1
        self.axes       = [1, 1, 1]

        self.view_arr       = ("persp", "top", "bottom", "front", "back", "right", "left")
        self.state_mode_arr = ("view", "settings", "values")
        self.state_mode     = "view"

        self.focus_dict = {
            "attribute": "partition",
            "focus"    : 0,
            "sel_arr"  : ("attribute", "focus"),
            "sel"      : "attribute"
        }

        self.setting_dict = {
            "setting_arr"    : ("xform_mode"      , "zoom_mode", "proj", "target", "viewport", "layout"),
            "setting"        : "xform_mode"       ,
            "xform_mode_arr" : ("rotate"          , "translate"),
            "xform_mode"     : "rotate"           ,
            "zoom_mode_arr"  : ("orthowidth"      , "dist", "clip"),
            "zoom_mode"      : "orthowidth"       ,
            "proj_arr"       : ("ortho"           , "persp"),
            "proj"           : "ortho"            ,
            "target_arr"     : ("cam"             , "pivot"),
            "target"         : "cam"              ,
            "viewport_arr"   : ()                 ,
            "viewport"       : ""                 ,
            "layout_arr"     : ("quadbottomsplit" , "single"),
            "layout"         : "quadbottomsplit"
        }

        self.startup_dict = {
            "view_arr": ("retain", "reset"),
            "view"    : "reset"
        }

        self.delta_dict = {
            "axis_size" : 4,
            "ri"        : 7.5,
            "ti"        : 1,
            "owi"       : 1,
            "di"        : 1,
            "ci"        : 2
        }

        self.val_dict = {
            "val_arr"   : ("axis_size", "ri", "ti", "di", "owi", "ci"),
            "val"       : "axis_size",
            "axis_size" : self.units["axis_size"],
            "ri"        : self.units["ri"],
            "ti"        : self.units["ti"],
            "owi"       : self.units["owi"],
            "di"        : self.units["di"],
            "ci"        : self.units["ci"]
        }

        # Drawables

        self.axs_drawable = hou.GeometryDrawable(scene_viewer=scene_viewer, geo_type=hou.drawableGeometryType.Line,
            name="axs_drawable", params={"color1": hou.Vector4((1, 1, 1, 0.3))})
        self.box_drawable = hou.GeometryDrawable(scene_viewer=scene_viewer, geo_type=hou.drawableGeometryType.Line,
            name="box_drawable", params={"color1": hou.Vector4((1, 1, 1, 0.3))})
        self.pvt_drawable = hou.GeometryDrawable(scene_viewer=scene_viewer, geo_type=hou.drawableGeometryType.Line,
            name="pvt_drawable")
        self.ray_drawable = hou.GeometryDrawable(scene_viewer=scene_viewer, geo_type=hou.drawableGeometryType.Line,
            name="ray_drawable", params={"color1": hou.Vector4((1, 0.8, 1, 0.5))})
        self.txt_drawable = hou.TextDrawable(scene_viewer=scene_viewer,
            name="txt_drawable", label="test")
        self.axs_drawable.show(True)
        self.box_drawable.show(False)
        self.pvt_drawable.show(True)
        self.ray_drawable.show(True)
    ##
    ##

    def cam_from_state(self):
        self.viewer_log("cam_from_state", "important")
        x=1

    def cam_init(self):
        self.viewer_log("cam_init", "important")
        viewport = self.viewer.curViewport()
        # Check if im_cam exists and if not, make it.
        child_arr = [ node.name() for node in hou.node("/obj").children() ]
        if "im_cam" not in child_arr:
            cam = hou.node("/obj").createNode("cam")
            cam.setName("im_cam")
        # Define variables
        translation = [0, 0, 0]
        rotation    = [0, 0, 0]
        pivot       = [0, 0, 0]
        orthowidth  = 1
        # Check is default cam or not
        cam = viewport.camera()
        if cam == None:
            default_cam = viewport.defaultCamera()
            translation = default_cam.translation()
            rotation    = default_cam.rotation()
            pivot       = default_cam.pivot()
            orthowidth  = default_cam.orthoWidth()
        else:
            translation = cam.parmTuple("t").eval()
            rotation    = cam.parmTuple("r").eval()
            pivot       = cam.parmTuple("p").eval()
            orthowidth  = cam.parm("orthowidth").eval()

        self.cam = hou.node("/obj/im_cam")
        self.viewport.setCamera(self.cam)
        self.viewport.lockCameraToView(True)

    def cam_rotate(self, key):
        self.viewer_log("cam_rotate", "important")
        r  = list(self.state_parms["r"]["value"])
        ri = self.vals["ri"]
        if   key == "h": r[1] = (r[1] + ri) % 360
        elif key == "j": r[0] = (r[0] - ri) % 360
        elif key == "k": r[0] = (r[0] + ri) % 360
        elif key == "l": r[1] = (r[1] - ri) % 360
        self.state_parms["r"]["value"] = r

    def cam_to_state(self):
        self.viewer_log("cam_to_state", "important")
        self.state_parms["t"]["value"]          = list( self.cam.evalParmTuple("t")  )
        self.state_parms["p"]["value"]          = list( self.cam.evalParmTuple("p")  )
        self.state_parms["r"]["value"]          = list( self.cam.evalParmTuple("r")  )
        self.state_parms["pr"]["value"]         = list( self.cam.evalParmTuple("pr") )
        self.state_parms["orthowidth"]["value"] = self.cam.evalParm("orthowidth")

    def cam_translate(self, key):
        self.viewer_log("cam_translate", "important")
        # true_pvt = list(self.state_parms["true_pvt"]["value"])
        self.get_view_dir()
        p  = list(self.state_parms["p"]["value"])
        ti = self.val_dict["ti"]
        if   key == "h": p[0] = p[0] - ti
        elif key == "j": p[1] = p[1] - ti
        elif key == "k": p[1] = p[1] + ti
        elif key == "l": p[0] = p[0] + ti
        self.state_parms["p"]["value"] = p

    def cam_update(self):
        self.viewer_log("cam_update", "important")
        # Convert true pivot
        true_pvt = 1
        if true_pvt:
            true_pvt = self.state_parms["true_pvt"]["value"]
            dist     = self.state_parms["dist"]["value"]
            self.state_parms["t"]["value"][0] = true_pvt[0]
            self.state_parms["t"]["value"][1] = true_pvt[1]
            self.state_parms["t"]["value"][2] = dist
            self.state_parms["p"]["value"][0] = 0
            self.state_parms["p"]["value"][1] = 0
            self.state_parms["p"]["value"][2] = true_pvt[2] - dist
        # Transfer state parameters to camera
        self.cam.parmTuple("r").set(self.state_parms["r"]["value"])
        self.cam.parmTuple("t").set(self.state_parms["t"]["value"])
        self.cam.parmTuple("p").set(self.state_parms["p"]["value"])
        self.cam.parmTuple("pr").set(self.state_parms["pr"]["value"])
        self.cam.parm("orthowidth").set(self.state_parms["orthowidth"]["value"])

    def cam_xform(self, key):
        self.viewer_log("cam_xform", "important")
        type = self.viewport.type()
        if self.viewer.curViewport().type() == hou.geometryViewportType.Perspective: # pyright: ignore
            if key in ("Shift+h", "Shift+j", "Shift+k", "Shift+l"):
                if   self.setting_dict["xform_mode"] == "rotate"   : self.cam_translate(key[-1])
                elif self.setting_dict["xform_mode"] == "translate": self.cam_rotate(key[-1])
            elif key in ("h", "j", "k", "l"):
                if   self.setting_dict["xform_mode"] == "rotate"   : self.cam_rotate(key)
                elif self.setting_dict["xform_mode"] == "translate": self.cam_translate(key)
            self.cam_update()
            self.drawable_update_pvt()
            self.drawable_update_ray()
        elif type == hou.geometryViewportType.Top    : self.cam_xform_flat( key, "top"   )
        elif type == hou.geometryViewportType.Bottom : self.cam_xform_flat( key, "bottom")
        elif type == hou.geometryViewportType.Front  : self.cam_xform_flat( key, "front" )
        elif type == hou.geometryViewportType.Back   : self.cam_xform_flat( key, "back"  )
        elif type == hou.geometryViewportType.Right  : self.cam_xform_flat( key, "right" )
        elif type == hou.geometryViewportType.Left   : self.cam_xform_flat( key, "left"  )

    def cam_xform_flat(self, key, view_type):
        self.viewer_log("cam_xform_flat", "important")
        viewport_name = self.setting_dict["viewport"]
        viewport_arr  = self.viewer.viewports()
        name_arr      = [ x.name() for x in viewport_arr ]
        idx           = name_arr.index(viewport_name)
        viewport      = viewport_arr[idx]
        idx_arr = [0, 0]
        if   view_type == "top"    : idx_arr = [0, 2]
        elif view_type == "bottom" : idx_arr = [2, 0]
        elif view_type == "front"  : idx_arr = [0, 1]
        elif view_type == "back"   : idx_arr = [1, 0]
        elif view_type == "right"  : idx_arr = [2, 1]
        elif view_type == "left"   : idx_arr = [1, 2]

        cam = viewport.defaultCamera() # pyright: ignore
        t  = list( cam.translation() )
        ti = self.vals["ti"]
        if   key == "h" : t[idx_arr[0]] += ti
        elif key == "j" : t[idx_arr[1]] += ti
        elif key == "k" : t[idx_arr[1]] -= ti
        elif key == "l" : t[idx_arr[0]] -= ti
        cam.setTranslation(t)

    def cam_zoom(self, key):
        self.viewer_log("cam_zoom", "important")
        proj     = self.settings["proj"]
        ow_delta = self.vals["ow_delta"]
        d_delta  = self.vals["d_delta"]
        if proj == "persp":
            #if   key == "Shift+-":
            #elif key == "Shift+=":
            if   key == "=": self.state_parms["dist"]["value"] -= d_delta
            elif key == "-": self.state_parms["dist"]["value"] += d_delta

        elif proj == "ortho":
            zoom_mode = self.setting_dict["zoom_mode"]
            if zoom_mode == "orthowidth":
                #if   key == "Shift+-":
                #elif key == "Shift+=":
                if   key == "-": self.state_parms["orthowidth"]["value"] += ow_delta
                elif key == "=": self.state_parms["orthowidth"]["value"] -= ow_delta

            elif zoom_mode == "dist":
                #if   key == "Shift+-":
                #elif key == "Shift+=":
                if   key == "=": self.state_parms["dist"]["value"] += d_delta
                elif key == "-": self.state_parms["dist"]["value"] -= d_delta

            elif zoom_mode == "clip":
                return

        self.cam_update()
        self.drawable_update_pvt()
        self.drawable_update_ray()

    def change_focus(self, key):
        self.viewer_log("change_focus", "important")
        if   key == "j": self.focus_dict["sel"] = self.list_next(self.focus_dict["sel_arr"], self.focus_dict["sel"])
        elif key == "k": self.focus_dict["sel"] = self.list_prev(self.focus_dict["sel_arr"], self.focus_dict["sel"]) 
        elif key in ("h", "l"):
            attr = self.focus["attr"]
            attr = hou.ui.readInput("Attribute", buttons=("OK", "Cancel"), initial_contents=attr)
            if attr[0] == 0: self.focus_dict["attr"] = attr[1]
        self.update_hud("focus")

    def change_setting(self, key):
        self.viewer_log("change_setting", "important")
        # Hilite Setting
        if   key == "j" : self.setting_dict["setting"] = self.list_prev(self.setting_dict["setting_arr"], self.setting_dict["setting"])
        elif key == "k" : self.setting_dict["setting"] = self.list_next(self.setting_dict["setting_arr"], self.setting_dict["setting"])
        # Modify Setting
        state_arr       = self.setting_dict[setting + "_arr"]
        state           = self.setting_dict[setting]
        if   key == "h" : self.setting_dict[setting] = self.list_next(state_arr, state)
        elif key == "l" : self.setting_dict[setting] = self.list_prev(state_arr, state)
        # Post-process
        if   self.setting_dict["setting"] == "proj"   : self.update_proj()
        elif self.setting_dict["setting"] == "layout" : self.update_layout()
        self.update_hud("setting_dict")

    def change_val(self, key):
        self.viewer_log("change_val", "important")
        val       = self.val_dict["val"]
        val_arr   = self.val_dict["val_arr"]
        if   key == "j": self.val_dict["val"] = self.list_prev(val_arr, val)
        elif key == "k": self.val_dict["val"] = self.list_next(val_arr, val)
        elif key == "h": self.val_dict[val]  -= self.unit_dict[val]
        elif key == "l": self.val_dict[val]  += self.unit_dict[val]
        self.update_hud("val_dict")

    def drawable_toggle_axs(self, kwargs, action):
        self.viewer_log("drawable_toggle_axes", "important")
        if   action == "show_all_axes" : self.axes = [1, 1, 1]
        elif action == "hide_all_axes" : self.axes = [0, 0, 0]
        elif action == "x_axis"        : self.axes[0] = kwargs["x_axis"]
        elif action == "y_axis"        : self.axes[1] = kwargs["y_axis"]
        elif action == "z_axis"        : self.axes[2] = kwargs["z_axis"]
        self.drawable_update_axs()
        self.viewer_log("Axis state: " + str(self.axs), "important")

    def drawable_toggle_bbx(self, kwargs, action):
        self.viewer_log("drawable_toggle_bbx", "important")
        enabled = kwargs["toggle_bbx"]
        self.drawable_update_bbx()

    def drawable_update_axs(self):
        self.viewer_log("drawable_update_axs", "important")
        axs_size = self.val_dict["axs_size"]
        geo = hou.Geometry()
        geo.addAttrib(hou.attribType.Point, "Cd", (1, 1, 1))
        for idx in (0, 1, 2):
            if self.axes[idx]:
                p0      = [0, 0, 0]
                p1      = [0, 0, 0]
                p0[idx] = -axs_size
                p1[idx] = axs_size
                pts     = geo.createPoints((p0, p1))
                cd      = [0, 0, 0]
                cd[idx] = 1
                pts[0].setAttribValue("Cd", cd)
                pts[1].setAttribValue("Cd", cd)
                prim = geo.createPolygon(is_closed=False)
                prim.addVertex(pts[0])
                prim.addVertex(pts[1])
        self.axs_drawable.setGeometry(geo)
        self.axs_drawable.setParams({"fade_factor": 0.0})

    def drawable_update_bbx(self):
        self.viewer_log("drawable_update_bbx", "important")
        geo = self.get_geo()
        bbx = geo.boundingBox()
        p0 = (bbx[0], bbx[1], bbx[2])
        p1 = (bbx[0], bbx[1], bbx[5])
        p2 = (bbx[3], bbx[1], bbx[5])
        p3 = (bbx[3], bbx[1], bbx[2])
        p4 = (bbx[0], bbx[4], bbx[2])
        p5 = (bbx[0], bbx[4], bbx[5])
        p6 = (bbx[3], bbx[4], bbx[5])
        p7 = (bbx[3], bbx[4], bbx[2])
        print(bbox)

    def drawable_update_pvt(self):
        self.viewer_log("drawable_update_pvt", "important")
        r           = list( self.state_parms["r"]["value"] )
        t           = list( self.state_parms["t"]["value"] )
        p           = list( self.state_parms["p"]["value"] )
        orthowidth  = self.state_parms["orthowidth"]["value"]
        s           = orthowidth * 0.0075
        pos         = hou.Vector3(p) + hou.Vector3(t)
        geo         = hou.Geometry()
        circle_verb = hou.sopNodeTypeCategory().nodeVerb("circle")
        circle_verb.setParms({"type": 1, "r": r, "t": pos, "scale": s})
        circle_verb.execute(geo, [])
        self.drawable_pvt.setGeometry(geo)
        self.drawable_pvt.setParams({
            "color1": hou.Vector4(0.0, 0.0, 1, 1),
            "fade_factor": 1.0
        })

    def drawable_update_ray(self):
        self.viewer_log("drawable_update_ray", "important")
        t        = self.state_parms["t"]["value"]
        r        = self.state_parms["r"]["value"]
        p        = self.state_parms["p"]["value"]
        true_pvt = self.state_parms["true_pvt"]["value"]
        r        = hou.hmath.buildRotate(r)
        cam_pos  = hou.Vector3(0, 0, self.get_len()) * r
        cam_pos += hou.Vector3(true_pvt[0], true_pvt[1], true_pvt[2])
        pvt_pos  = hou.Vector3(t) + hou.Vector3(p)
        geo      = hou.Geometry()
        pts      = geo.createPoints((cam_pos, pvt_pos))
        prim     = geo.createPolygon()
        prim.addVertex(pts[0])
        prim.addVertex(pts[1])
        self.drawable_ray.setGeometry(geo)

    def frame_viewports(self):
        self.viewer_log("frame_viewports", "important")
        [ viewport.frameAll() for viewport in self.viewer.viewports() ]
        self.cam_to_state()
        self.drawable_update_pvt()

    def get_centroid(self):
        self.viewer_log("get_centroid", "important")
        geo = self.get_geo()
        result_geo = hou.Geometry()
        centroid_verb = hou.sopNodeTypeCategory().nodeVerb("extractcentroid")
        centroid_verb.setParms({"partitiontype": 2})
        centroid_verb.execute(result_geo, [geo])
        pt = result_geo.point(0)
        centroid = pt.position()
        return centroid

    def get_dist(self):
        self.viewer_log("get_dist", "important")
        dist = self.state_parms["dist"]["value"]
        return dist

    def get_extrema(self):
        self.viewer_log("get_extrema", "important")
        geo = self.get_geo()
        bbx = geo.boundingBox()

    def get_geo(self):
        self.viewer_log("get_geo", "important")
        display_node = self.viewer.pwd().displayNode()
        geo = display_node.geometry()
        return geo

    def get_len(self):
        self.viewer_log("get_len", "important")
        t = self.state_parms["t"]["value"]
        p = self.state_parms["p"]["value"]
        len = t[2]
        return len

    def get_view_dir(self):
        self.viewer_log("get_view_dir", "important")
        true_pvt = self.state_parms["true_pvt"]["value"]
        t = self.state_parms["t"]["value"]
        self.viewer_log(hou.Vector3(true_pvt) - hou.Vector3(t), "normal")
        return

    def get_view_xform(self):
        self.viewer_log("get_view_xform", "important")
        r = self.state_parms["r"]["value"]
        return r

    def init_drawable(self):
        self.drawable_update_axis()

    def init_hud(self):
        self.viewer_log("init_hud", "important")
        self.viewer.hudInfo(template=self.SETTING_HUD)
        sd = self.setting_dict
        updates = {
            "state_mode"   : {"value" : self.state_mode                             },
            "state_mode_g" : {"value" : self.state_mode_arr.index(self.state_mode)  },
            "xform_mode"   : {"value" : sd["xform_mode"]                            },
            "xform_mode_g" : {"value" : sd["xform_mode_arr"].index(sd["xform_mode"])},
            "zoom_mode"    : {"value" : sd["zoom_mode"]                             },
            "zoom_mode_g"  : {"value" : sd["zoom_mode_arr"].index(sd["zoom_mode"])  },
            "proj"         : {"value" : sd["proj"]                                  },
            "proj_g"       : {"value" : sd["proj_arr"].index(sd["proj"])            },
            "target"       : {"value" : sd["target"]                                },
            "target_g"     : {"value" : sd["target_arr"].index(sd["target"])        },
            "viewport"     : {"value" : sd["viewport"]                              },
            "viewport_g"   : {"value" : sd["viewport_arr"].index(sd["viewport"])    },
            "layout"       : {"value" : sd["layout"]                                },
            "layout_g"     : {"value" : sd["layout_arr"].index(sd["layout"])        }
        }
        self.viewer.hudInfo(hud_values=updates)

    def init_layout(self):
        self.viewer_log("init_layout", "important")
        layout = self.viewer.viewportLayout()
        if   layout == hou.geometryViewportLayout.Single          : self.setting_dict["layout"] = "single"
        elif layout == hou.geometryViewportLayout.QuadBottomSplit : self.setting_dict["layout"] = "quadbottomsplit"

    def init_parms(self):
        self.viewer_log("init_parms", "important")
        self.state_parms["t"]["value"]          = list( self.cam.evalParmTuple("t") )
        self.state_parms["p"]["value"]          = list( self.cam.evalParmTuple("p") )
        self.state_parms["r"]["value"]          = list( self.cam.evalParmTuple("r") )
        self.state_parms["pr"]["value"]         = list( self.cam.evalParmTuple("pr") )
        self.state_parms["orthowidth"]["value"] = self.cam.evalParm("orthoWidth")

    def init_viewport_arr(self):
        self.viewer_log("init_viewport_arr", "important")
        self.setting_dict["viewport_arr"] = [ viewport.name() for viewport in self.viewer.viewports() ]
        self.setting_dict["viewport"]     = self.setting_dict["viewport_arr"][0]

    def list_next(self, list, sel):
        idx = list.index(sel)
        idx = (idx + 1) % len(list)
        return idx

    def list_prev(self, list, sel):
        idx = list.index(sel)
        idx = (idx - 1) % len(list)
        return idx

    def move_pvt(self):
        self.tviewer_log("move_pvt", "important")
        sp     = self.state_parms
        target = self.setting_dict["target"]
        if target == "cam":
            t = sp["t"]["value"]
            sp["true_pvt"]["value"] = list(t)
        elif target == "centroid":
            centroid = self.get_centroid()
            sp["true_pvt"]["value"] = list(centroid)
        elif target == "origin":
            sp["t"]["value"]          = [ 0, 0, self.get_dist() ]
            sp["r"]["value"]          = [ 45, 45, 0 ]
            sp["p"]["value"]          = [ 0, 0, -self.get_dist() ]
            sp["pr"]["value"]         = [ 0, 0, 0 ]
            sp["true_pvt"]["value"]   = [ 0, 0, 0 ]
            sp["orthowidth"]["value"] = 1 0
        elif target == "ray":
            x=1
        self.cam_update()
        self.update_drawable_pvt()
        self.update_drawable_ray()

    def next_state_mode(self):
        self.viewer_log("next_state_mode", "important")
        next = self.list_next(self.state_mode_arr, self.state_mode)
        self.state_mode = next
        self.update_hud(next)

    def print(self, key):
        self.viewer_log("print", "important")
        if key == "cam_vals":
            t = self.state_parms["t"]["value"]
            r = self.state_parms["r"]["value"]
            p = self.state_parms["p"]["value"]
            pr = self.state_parms["pr"]["value"]
            self.viewer_log("r:\n", r, "t:\n", t, "p:\n", p, "pr:\n", pr, "normal")
        elif key == "centroid":
            self.viewer_log(self.get_centroid(), "normal")
        elif key == "hud_state":
            x=1
        elif key == "viewport":
            self.viewer_log(self.settings["viewport"], "normal")

    def print_kwargs(self, kwargs):
        self.viewer_log("print_kwargs", "important")
        self.viewer_log_separator()
        ui_event = str(kwargs["ui_event"])
        ui_event = ui_event.replace("\\n", "\n")
        del kwargs["ui_event"]
        self.viewer_log_separator()
        self.viewer_log(ui_event, "normal")

    def view_reset(self):
        self.viewer_log("view_reset", "important")
        dist = self.get_dist()
        sp  = self.state_parms
        sp["t"]["value"]          = [ 0, 0, dist ]
        sp["r"]["value"]          = [ 45, 45, 0 ]
        sp["p"]["value"]          = [ 0, 0, -dist ]
        sp["pr"]["value"]         = [ 0, 0, 0 ]
        sp["true_pvt"]["value"]   = [ 0, 0, 0 ]
        sp["orthowidth"]["value"] = 1 0
        self.cam_update()
        self.drawable_update_pvt()
        self.drawable_update_ray()

    def view_set(self,  view):
        self.viewer_log("view_set", "important")
        viewport = self.viewer.viewports()[-1]
        if view == "persp":
            self.cam_init()
        if view == "top":
            viewport.changeType(hou.geometryViewportType.Top)

    def viewport_refit(self):
        self.viewer_log("viewport_refit", "important")
        self.cam.parm("resx").set(1000)
        self.cam.parm("resy").set(1000)
        size  = self.viewport.size()
        ratio = size[2] / size[3]
        self.cam.parm("aspect").set(ratio)

    def viewport_rotate(self):
        self.viewer_log("viewport_rotate", "important")
        viewport_arr = self.viewer.viewports()
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
        # self.viewer_log(v_name_arr, "normal")
        # self.viewer_log(v_type_arr, "normal")

    def viewer_log(self, message, level):
        if   level == "normal"    : self.log(message)
        elif level == "important" : self.log(message, severity=hou.severityType.ImportantMessage)

    def viewer_log_separator(self):
        self.viewer_log("-------------------------", "normal")

    def update_hud(self, hud):
        self.viewer_log("update_hud", "important")
        sd = self.setting_dict
        vd = self.val_dict
        ##
        if hud == "settings":
            self.viewer.hudInfo(template=self.SETTING_HUD)
            updates = {
                "state_mode"   : { "value" : self.state_mode                             },
                "state_mode_g" : { "value" : self.state_mode_arr.index(self.state_mode)  },
                "xform_mode"   : { "value" : sd["xform_mode"]                            },
                "xform_mode_g" : { "value" : sd["xform_mode_arr"].index(sd["xform_mode"])},
                "zoom_mode"    : { "value" : sd["zoom_mode"]                             },
                "zoom_mode_g"  : { "value" : sd["zoom_mode_arr"].index(sd["zoom_mode"])  },
                "proj"         : { "value" : sd["proj"]                                  },
                "proj_g"       : { "value" : sd["proj_arr"].index(sd["proj"])            },
                "target"       : { "value" : sd["target"]                                },
                "target_g"     : { "value" : sd["target_arr"].index(sd["target"])        },
                "viewport"     : { "value" : sd["viewport"]                              },
                "viewport_g"   : { "value" : sd["viewport_arr"].index(sd["viewport"])    },
                "layout"       : { "value" : sd["layout"]                                },
                "layout_g"     : { "value" : sd["layout_arr"].index(sd["layout"])        }
            }
            if self.state_mode == "settings":
                setting = sd["setting"]
                updates[setting]["value"] = "[" + updates[setting]["value"] + "]"
            self.viewer.hudInfo(hud_values=updates)
        ##
        elif hud == "val_dict":
            self.viewer.hudInfo(template=self.VAL_HUD)
            updates = {
                "state_mode"       : {"value" : "Value"               },
                "state_mode_graph" : {"value" : 2                     },
                "axis_size"        : {"value" : str( vd["axis_size"]) },
                "r_delta"          : {"value" : str( vd["r_delta"])   },
                "t_delta"          : {"value" : str( vd["t_delta"])   },
                "ow_delta"         : {"value" : str( vd["ow_delta"])  },
                "d_delta"          : {"value" : str( vd["d_delta"])   },
                "c_delta"          : {"value" : str( vd["c_delta"])   }
            }
            updates[self.vals["val"]]["value"] = "[" + updates[self.vals["val"]]["value"] + "]"
            self.viewer.hudInfo(hud_values=updates)
        ##
        elif hud == "focus":
            self.viewer.hudInfo(template=self.FOCUS_HUD)
            updates = {
                "attr"    : {"value" : self.focus_dict["attribute"]},
                "focus"   : {"value" : str(0)},
                "focus_g" : {"value" : 0},
            }
            sel = self.focus["sel"]
            updates[sel]["value"] = "[" + updates[sel]["value"] + "]"
            self.viewer.hudInfo(hud_values=updates)

    def update_layout(self):
        self.viewer_log("update_layout", "important")
        layout = self.setting_dict["layout"]
        if   layout == "quadbottomsplit" : self.viewer.setViewportLayout( hou.geometryViewportLayout.QuadBottomSplit )
        elif layout == "single"          : self.viewer.setViewportLayout( hou.geometryViewportLayout.Single          )

    def update_proj(self):
        self.viewer_log("update_proj", "important")
        proj = self.settings["proj"]
        if   proj == "ortho" : self.cam.parm("projection").set("ortho")
        elif proj == "persp" : self.cam.parm("projection").set("perspective")
        self.frame_viewports()

    def update_viewport_arr(self):
        self.viewer_log("update_viewport_arr", "important")
        viewport_arr = list( self.viewer.viewports() )
        viewport_arr.reverse()
        self.settings["viewport_arr"] = [ viewport.name() for viewport in viewport_arr ]

    def update_xform(self):
        self.viewer_log("update_xform", "important")

    ##
    ##

    def onDraw(self, kwargs):
        dh = kwargs["draw_handle"]
        s  = self.
        s.axs_drawable.draw( dh, {} )
        s.pvt_drawable.draw( dh, {} )
        s.ray_drawable.draw( dh, {} )
        s.txt_drawable.draw( dh, {} )

    def onGenerate(self, kwargs):
        self.viewer_log_separator()
        self.viewer_log("onGenerate", "important")
        # Integrate with node graph
        kwargs["state_flags"]["exit_on_node_select"] = False
        # Init vars
        self.viewport    = self.viewer.selectedViewport()
        self.state_parms = kwargs["state_parms"]
        # Call functions
        self.cam_init()
        self.init_parms()
        self.init_viewport_arr()
        self.init_layout()
        self.init_hud()
        self.init_drawable()
        self.view_refit()

    def onKeyEvent(self, kwargs):
        self.viewer_log_separator()
        self.viewer_log("onKeyEvent", "important")
        sm = self.state_mode
        key = kwargs["ui_event"].device().keyString()
        if key == "m":
            self.next_state_mode()
            self.view_refit()
            return True
        elif key[-1] in ("h", "j", "k", "l"):
            if   sm == "view"     : self.dispatch_xform(key)
            elif sm == "settings" : self.change_setting(key)
            elif sm == "values"   : self.change_val(key)
            elif sm == "focus"    : self.change_focus(key)
            return True
        elif key[-1] in ("-", "="):
            self.cam_zoom(key)
            return True
        else:
            return False

    def onMenuAction(self, kwargs):
        self.viewer_log_separator()
        self.viewer_log("onMenuAction", "important")
        action = kwargs["menu_item"]
        if   action == "pvt_to_ray"         : self.move_pvt("ray")
        elif action == "pvt_to_camera"      : self.move_pvt("camera")
        elif action == "pvt_to_centroid"    : self.move_pvt("centroid")
        elif action == "pvt_to_origin"      : self.move_pvt("origin")
        elif action == "frame_viewports"    : self.frame_viewports()
        elif action == "reset_view"         : self.reset_view()
        elif action == "toggle_bbx"         : self.toggle_bbx(kwargs, action)
        # Axes menu
        elif action in ["show_all_axes", "hide_all_axes", "x_axis", "y_axis", "z_axis"]:
                                              self.toggle_axes(kwargs, action)
        elif action == "frame_viewports"    : self.frame_viewports()
        elif action == "reset_view"         : self.reset_view()
        elif action == "view_refit"         : self.refit_ui()
        # View Menu
        elif action == "rotate_viewports"   :self.rotate_viewports()
        # Test menu
        elif action == "cam_to_state"       : self.cam_to_state()
        elif action == "update_viewport_arr": self.update_viewport_arr()
        # Print menu
        elif action == "print_cam_vals"     : self.print("cam_vals")
        elif action == "print_centroid"     : self.print("centroid")
        elif action == "print_kwargs"       : self.print_kwargs(kwargs)
        elif action == "print_viewport"     : self.print("viewport")

        # def onMouseEvent(self, kwargs):
        #     node = kwargs["node"]
        #     ui_event = kwargs["ui_event"]
        #     scrx = ui_event.device().mouseX()
        #     scry = ui_event.device().mouseY()

        #     if ui_event.reason() == hou.uiEventReason.Picked\
        #         or ui_event.reason() == hou.uiEventReason.Start:
        #         origin, dir = ui_event.ray()
        #         prim = self.viewport.queryPrimAtPixel(None, round(scrx), round(scry))
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

    def onParmChangeEvent(self, kwargs):
        updates = (0, 0, 0, 0, 0)
        pn = kwargs["parm_name"]
        if   pn == "axis_size" : updates = (1, 0, 0, 0, 0)
        elif pn == "dist"      : updates = (0, 1, 1, 1, 1)
        elif pn == "t"         : updates = (0, 1, 1, 1, 1)
        elif pn == "r"         : updates = (0, 1, 1, 1, 1)
        elif pn == "p"         : updates = (0, 1, 1, 1, 1)
        elif pn == "pr"        : updates = (0, 1, 1, 1, 1)
        elif pn == "true_pvt"  : updates = (0, 1, 1, 1, 1)

        if updates[0]: self.drawable_update_axs()
        if updates[1]: self.cam_update()
        if updates[2]: self.cam_update()
        if updates[3]: self.drawable_update_pvt()
        if updates[4]: self.drawable_update_pvt()

def make_menu(template):
    menu = hou.ViewerStateMenu("im_view_menu", "IM View Menu")

    menu.addActionItem("pvt_to_ray"          , "Pivot to Ray")
    menu.addActionItem("pvt_to_cam"          , "Pivot to Camera")
    menu.addActionItem("pvt_to_centroid"     , "Pivot to Centroid")
    menu.addActionItem("pvt_to_origin"       , "Pivot to Origin")
    menu.addSeparator()
    menu.addActionItem("reset_view"          , "Reset View")
    menu.addActionItem("view_refit"          , "view_refit")
    menu.addActionItem("frame_viewports"     , "Frame Viewports")
    menu.addActionItem("rotate_viewports"    , "Rotate Viewports")
    menu.addSeparator()
    menu.addActionItem("show_all_axes"       , "Show All Axes")
    menu.addActionItem("hide_all_axes"       , "Hide All Axes")
    menu.addToggleItem("x_axis"              , "X Axis", 1)
    menu.addToggleItem("y_axis"              , "Y Axis", 1)
    menu.addToggleItem("z_axis"              , "Z Axis", 1)
    menu.addToggleItem("toggle_bbx"          , "Bounding Box", 0)
    menu.addSeparator()
    menu.addActionItem("print_cam_vals"      , "Print Cam Vals")
    menu.addActionItem("print_kwargs"        , "Print Kwargs")
    menu.addActionItem("print_centroid"      , "Print Centroid")
    menu.addActionItem("print_viewport"      , "Print Viewport")
    menu.addSeparator()
    menu.addActionItem("cam_to_state"        , "cam_to_state")
    menu.addActionItem("update_viewport_arr" , "update_viewport_arr")
    template.bindMenu(menu)

def make_parameters(template):
    template.bindParameter(hou.parmTemplateType.Separator , "sep0"       , toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float     , "dist"       , "Distance"       , default_value=10.0)
    template.bindParameter(hou.parmTemplateType.Float     , "orthowidth" , "FOV"            , default_value=10.0)
    template.bindParameter(hou.parmTemplateType.Separator , "sep1"       , toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float     , "t"          , "Translation"    , num_components=3 , toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float     , "r"          , "Rotation"       , num_components=3 , toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float     , "p"          , "Pivot"          , num_components=3 , toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float     , "pr"         , "Pivot Rotation" , num_components=3 , toolbox=False)
    template.bindParameter(hou.parmTemplateType.Separator , "sep2"       , toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float     , "up"         , "Up"             , num_components=3 , toolbox=False)
    template.bindParameter(hou.parmTemplateType.Float     , "true_pvt"   , "True pivot"     , num_components=3 , toolbox=False)

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
