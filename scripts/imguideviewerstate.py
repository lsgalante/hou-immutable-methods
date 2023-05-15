"""
State:          Lucas::dev::imguide::1.0
State type:     lucas::dev::imguide::1.0
Description:    Lucas::dev::imguide::1.0
Author:         lucas
Date Created:   May 02, 2023 - 18:01:37
"""

# Usage: This sample draws highlights when hovering over geometry polygons.
# Make sure to add an input on the node, connect a polygon mesh geometry and
# hit enter in the viewer.

import hou
import viewerstate.utils as su
import toolutils as tu
import curveutils as cu

class State(object):

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer
        
        self.geometry = None
        
        self.face = hou.GeometryDrawable(
            self.scene_viewer, 
            hou.drawableGeometryType.Face, 
            "face",
            None,
            params = {
                "style" : hou.drawableGeometryFaceStyle.Plain,
                "color1" : (0.5, 0.5, 0.5, 0.5),
                "fade_factor" : 1.0
            }
        )

        self.outline = hou.GeometryDrawable(
            self.scene_viewer, 
            hou.drawableGeometryType.Line, 
            "outline",
            None,
            params = {
                "style" : hou.drawableGeometryLineStyle.Plain,
                "color1" : (0.0, 0.0, 0.0, 1.0),
                "fade_factor" : 1.0
            }
        )

    def onEnter(self, kwargs):

        node = kwargs["node"]
        self.geometry = node.geometry()
        self.face.show(True)
        self.outline.show(True)

    def onDraw(self, kwargs):

        geo = kwargs['node'].node('imguide1').geometry()
        self.face.setGeometry(geo)
        self.outline.setGeometry(geo)
        handle = kwargs['draw_handle']
        self.face.draw(handle)
        self.outline.draw(handle)

        viewdir = cu.getViewDirection(tu.sceneViewer())
        kwargs['node'].parm('to1').set(viewdir[0])
        kwargs['node'].parm('to2').set(viewdir[1])
        kwargs['node'].parm('to3').set(viewdir[2])

    def onDrawInterrupt(self, kwargs):

        geo = kwargs['node'].node('imguide1').geometry()
        self.face.setGeometry(geo)
        self.outline.setGeometry(geo)
        handle = kwargs['draw_handle']
        self.face.draw(handle)
        self.outline.draw(handle)

        viewdir = cu.getViewDirection(tu.sceneViewer())
        kwargs['node'].parm('to1').set(viewdir[0])
        kwargs['node'].parm('to2').set(viewdir[1])
        kwargs['node'].parm('to3').set(viewdir[2])

def createViewerStateTemplate():

    state_typename = kwargs["type"].definition().sections()["DefaultState"].contents()
    state_label = "Lucas::dev::imguide::1.0"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)

    return template