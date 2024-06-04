import hou
import viewerstate.utils as su

from importlib import reload
import im_view_common

def createViewerStateTemplate():
    reload(im_view_common)
    state_name = "im_view_obj"
    state_label = "IM View OBJ"

    template = hou.ViewerStateTemplate(
      state_name, state_label, hou.objNodeTypeCategory())


    # CONTEXT MENU
    menu = hou.ViewerStateMenu('im_viewer_menu', 'IM Viewer')
    menu.addActionItem('reset', 'Reset')
    menu.addActionItem('set_home', 'Set Home')
    menu.addActionItem('set_frame', 'Set Frame')
    menu.addActionItem('set_pivot', 'Set Pivot')
    menu.addActionItem('grid', 'Grid')
    menu.addActionItem('print_cam_vals', 'Print Cam Vals')
    template.bindMenu(menu)

    template.bindFactory(im_view_common.State)
    template.bindIcon("DESKTOP_application_sierra")
        
    return template

