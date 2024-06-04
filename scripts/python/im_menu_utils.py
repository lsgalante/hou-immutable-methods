import hou

def rename_pane_tab():

    tab = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    print(tab)
    name = tab.name()
    new_name = hou.ui.readInput(
      message='Rename current tab ' + name,
      buttons=('Ok', 'Cancel'),
      default_choice=1,
      close_choice=1)
    if new_name[0] == 1:
        return
    else:
        tab.setName(new_name[1])


def toggle_im_view():
    viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
    if viewer != None:
        node = viewer.pwd()
        viewer_type = node.childTypeCategory().name()

        if viewer_type == 'Object':
            viewer.setCurrentState('im_view_obj')

        elif viewer_type == 'Sop':
            viewer.setCurrentState('im_view_sop')

        else:
            print('IM View currently needs a SOP or OBJ type scene viewer.')

    else:
        print('No available scene viewer.')
        return
