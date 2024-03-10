"""
State:          Voudini SOP - Scene Viewer
State type:     voudini_sop
Author:         Lucas G.
Date:           24
Description:    Control SOP scene viewer default camera with vim key bindings.
"""

import hou
import viewerstate.utils as su

# STATE CLASS
class State(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer        
        
        # TEXT DRAWABLE
        self.text_drawable = hou.TextDrawable( self.scene_viewer, 'text_drawable_name',
            params = {'margins': ( 10.0, 10.0 ), 'color1': hou.Color( 0.8, 0.8, 0.8 ) } )
        self.text_drawable.show( True )
        
        # GET CAM XFORM
        viewport = self.scene_viewer.curViewport()
        self.cam = viewport.defaultCamera()
        
        self.trans = [ 0, 0, 120 ]
        rot3 = self.cam.rotation()
        rot3.setToIdentity()
        self.rot4 = hou.Matrix4( rot3 )
        self.rotv = self.rot4.extractRotates()
        self.pivot =  [0, 0, 0 ]
        
        # SET CAM XFORM
        self.cam.setTranslation( self.trans )
        self.cam.setRotation( self.rot4.extractRotationMatrix3() )
        self.cam.setPivot( self.pivot )
        
    # ON ENTER
    def onEnter(self, kwargs):
        node = kwargs['node']
        state_parms = kwargs['state_parms']
        
    # ON KEY EVENT
    def onKeyEvent( self, kwargs ):
        ui_event = kwargs['ui_event']
        
        key_string = ui_event.device().keyString()
        key_value = ui_event.device().keyValue()
        
        self.key_pressed = ui_event.device().keyString()
        
        # ROTATION
        if self.key_pressed in ( 'h', 'j', 'k', 'l' ):
            self.rotv = self.rot4.extractRotates()
            a3 = hou.Vector3( 0, 0, 0 )

            if key_string == 'h':
                a3 = hou.Vector3( 0, 1, 0 )    
            elif key_string == 'j':
                a1 = hou.Vector3( 0, 1, 0 )
                a2 = hou.Vector3( 0, 0, 1 )
                a3 = a1.cross( a2 ).normalized() * -1
                # a3 += self.rotv.normalized()
            elif key_string == 'k':
                a1 = hou.Vector3( 0, 1, 0 )
                a2 = hou.Vector3( 0, 0, 1 )
                a3 = a1.cross( a2 ).normalized()
                # a3 += self.rotv.normalized()
            elif key_string == 'l':
                a3 = hou.Vector3( 0, -1, 0 )
                            
            self.rot4 = self.rot4 * hou.hmath.buildRotateAboutAxis( a3, 20 )
            self.cam.setRotation( self.rot4.extractRotationMatrix3() )
            
            return True
            
        # ZOOM OUT
        elif self.key_pressed in ( '-' ):
            ortho_w = self.cam.orthoWidth()
            print(ortho_w)
            self.cam.setOrthoWidth( ortho_w + 10 )
            return True
        
        # ZOOM IN
        elif self.key_pressed in ( '=' ):
            ortho_w = self.cam.orthoWidth()
            self.cam.setOrthoWidth( ortho_w - 10 )
            return True
        
        self.key_pressed = None
        
        # return False if the event is not consumed
        return False
                   
    # ON DRAW
    def onDraw( self, kwargs ):
        # draw the text in the viewport lower left (default origin)
        handle = kwargs['draw_handle']
        state_parms = kwargs['state_parms']

        params = {
            'text': 'ass',
            # 'scale' : hou.Vector3( 1.0. 1.0, 1.0 ),
            "color1" : hou.Color( 0.8, 0.8, 0.8 ) }

        self.text_drawable.draw( handle, params )

# STATE TEMPLATE
def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = "Voudini_SOP"
    state_label = "Voudini SOP"
    state_cat = hou.sopNodeTypeCategory()

    ##
    # BIND STATE TEMPLATE
    ##
    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon("DESKTOP_application_sierra")
        
    return template

