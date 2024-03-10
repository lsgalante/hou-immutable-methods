import hou

def toggle_voudini():

    viewer = hou.ui.paneTabOfType( hou.paneTabType.SceneViewer )
    if viewer != None:
        node = viewer.pwd()
        node_type = node.type()
        node_type_name = node_type.name()

        if node_type_name == 'obj':
            viewport = viewer.curViewport()
            viewport.changeType( hou.geometryViewportType.Perspective )
            cam = viewport.defaultCamera()
            cam.setPerspective( False )
            viewer.setCurrentState( 'Voudini_OBJ' )

        elif node_type_name == 'geo':
            viewport = viewer.curViewport()
            viewport.changeType( hou.geometryViewportType.Perspective )
            cam = viewport.defaultCamera()
            cam.setPerspective( False )
            viewer.setCurrentState( 'Voudini_SOP' )

        else:
            print( 'Voudini currently needs a SOP or OBJ type scene viewer.' )

    else:
        print('No available scene viewer.')
        return
