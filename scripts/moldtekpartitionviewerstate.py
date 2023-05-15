"""
State:          Lucas::dev::moldtekpartition::1.0
State type:     lucas::dev::moldtekpartition::1.0
Description:    Lucas::dev::moldtekpartition::1.0
Author:         lucas
Date Created:   May 11, 2023 - 14:53:08
"""

# Usage: This sample draws highlights when hovering over geometry polygons.
# Make sure to add an input on the node, connect a polygon mesh geometry and
# hit enter in the viewer.

import hou
import viewerstate.utils as su

class State(object):
    MSG = "Move the mouse over the geometry."

    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer
        self.poly_id = -1
        self.geometry = None
        self.mouse_screen = hou.Vector2()

        # A drawable to display the mouse coordinates at the cursor 
        # position.
        # Use su.CursorLabel.setLabel to display a fix label.
        self.cursor = su.CursorLabel(scene_viewer, "cursor")
        
        # Drawable for drawing the polygon under the cursor.
        self.face = hou.GeometryDrawable(self.scene_viewer, 
            hou.drawableGeometryType.Face, 
            "face", 
            params = {
                "style": hou.drawableGeometryFaceStyle.Plain,
                "color1": (0.0,1.0,0.0,1.0) }
        )
                
    def show(self, visible):
        """ Display or hide drawables.
        """
        self.cursor.show(visible)
        self.face.show(visible)

    def onEnter(self, kwargs):
        """ Assign the geometry to drawabled
        """
        node = kwargs["node"]
        self.geometry = node.geometry()
        self.show(True)



        self.scene_viewer.setPromptMessage( State.MSG )

    def onResume(self, kwargs):
        self.show(True)
        self.scene_viewer.setPromptMessage( State.MSG )

    def onInterrupt(self,kwargs):
        self.show(False)

    def onMouseEvent(self, kwargs):
        """ Computes the cursor text position and drawable geometry
        """
        # set the cursor label

        node = kwargs["node"]

        geo = node.geometry()
        loci = geo.findPrimGroup("loci")
        
        if loci == None:
            print(geo.createPrimGroup("loci"))

        self.cursor.setParams(kwargs)

        # Set the drawable with the polygon under the cursor
        ui_event = kwargs["ui_event"]
        (origin, dir) = ui_event.ray()        
        gi = su.GeometryIntersector(self.geometry)
        gi.intersect(origin, dir, snapping=False)

        device = kwargs["ui_event"].device()
        # if device.isLeftButton():

        if gi.prim_num != -1 and gi.prim_num != self.poly_id:
            self.poly_id = gi.prim_num
    
            # Construct a new geometry
            poly_points = self.geometry.prim(self.poly_id).points()                                                                      
            poly_geo = hou.Geometry()
            poly = poly_geo.createPolygon()
            for pt in poly_points:
                point = poly_geo.createPoint()
                point.setPosition(pt.position())
                poly.addVertex(point)        

            # update the drawable                
            self.face.setGeometry(poly_geo)
            self.show(True)

                
        elif gi.prim_num == -1:
            # no polygon under the cursor
            self.poly_id = -1
            self.poly_geo = None            
            self.face.show(False)

    def onDraw( self, kwargs ):
        """ This callback is used for rendering the drawables
        """
        handle = kwargs["draw_handle"]

        self.face.draw(handle) 
        self.cursor.draw(handle)


def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = kwargs["type"].definition().sections()["DefaultState"].contents()
    state_label = "Lucas::dev::moldtekpartition::1.0"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon(kwargs["type"].icon())






    return template
