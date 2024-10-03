import hou

def reload_viewport_color_schemes():
    hou.ui.reloadViewportColorSchemes()

def toggle_im_view():
    viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
    if viewer != None:
        node = viewer.pwd()
        viewer_type = node.childTypeCategory().name()

        if viewer_type == "Object" or viewer_type == "Sop":
            viewer.setCurrentState("im_view")
        else:
            print("Only Sop or Object contexts are available.")

    else:
        print("No available scene viewer.")
        return

def reload_im_view():
    hou.ui.reloadViewerState("im_view")

def update_main_menu():
    hou.ui.updateMainMenuBar()

def restart_to_this_file():
    x=1

def open_color_chooser():
    hou.ui.selectColor()
