def lab_callback( kwargs ):
    
    node = kwargs[ 'node' ]
    l_parm = node.parm( 'lab_l' )
    a_parm = node.parm( 'lab_a' )
    b_parm = node.parm( 'lab_b' )

    l = l_parm.evalAsFloat( )
    a = a_parm.evalAsFloat( )
    b = b_parm.evalAsFloat( )

    lab = ( l, a, b )

    color = hou.Color((0, 0, 0))
    color.setLAB(lab)
    color = color.rgb()

    r_parm = node.parm ( 'colorr' )
    g_parm = node.parm ( 'colorg' )
    b_parm = node.parm ( 'colorb' )

    r_parm.set ( color[ 0 ] )
    g_parm.set ( color[ 1 ] )
    b_parm.set ( color[ 2 ] )