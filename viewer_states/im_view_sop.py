import hou
import viewerstate.utils as su

from importlib import reload
import im_view_common

def createViewerStateTemplate():
    reload(im_view_common)
    state_name = "im_view_sop"
    state_label = "IM View SOP"

    template = hou.ViewerStateTemplate(
      state_name, state_label, hou.sopNodeTypeCategory())

    # CONTEXT MENU
    menu = hou.ViewerStateMenu('im_viewer_menu', 'IM Viewer')
    menu.addActionItem('reset', 'Reset')
    menu.addActionItem('set_home', 'Set Home')
    menu.addActionItem('set_frame', 'Set Frame')
    menu.addActionItem('set_pivot', 'Set Pivot')
    menu.addActionItem('print_cam_vals', 'Print Cam Vals')
    template.bindMenu(menu)

    # BIND IT
    template.bindFactory(im_view_common.State)
    template.bindIcon("DESKTOP_application_sierra")

    # HANDLE
    template.bindHandleStatic(
      "xform", "start_handle",
      [("startx", "tx"), ("starty", "ty"), ("startz", "tz")]
    )
        
    return template

