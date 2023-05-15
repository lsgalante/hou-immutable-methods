def handles( kwargs ):

    node = kwargs[ 'node' ]
    handles_parm = node.parm( 'handles' )
    n_handles = handles_parm.evalAsInt( )
    
    ramp_parm = node.parm( 'ramp' )

    l = node.parm( 'l' ).eval( )
    a = node.parm( 'a' ).eval( )
    b = node.parm( 'b' ).eval( )

    l_change = node.parm( 'l_change' ).eval( )
    a_change = node.parm( 'a_change' ).eval( )
    b_change = node.parm( 'b_change' ).eval( )
    
    basis = ( )
    keys = ( )
    values = ( )
    
    for x in range( n_handles ):

        basis += ( hou.rampBasis.Linear, )

        key = 1 / ( n_handles - 1 ) * x
        keys += ( key, )

        l_multi = ( ( ( key - 0 ) * ( 100 - 0 ) ) / ( 1 - 0 ) ) + 0
        lab_l = ( 1 - l_change ) * l + l_change * ( key * l_multi )

        a_multi = ( ( ( key - 0 ) * ( 127 - -128 ) ) / ( 1 - 0 ) ) + -128
        lab_a = ( 1 - a_change ) * a + a_change * ( key * a_multi )

        b_multi = ( ( ( key - 0 ) * ( 127 - -128 ) ) / ( 1 - 0 ) ) + -128
        lab_b = ( 1 - b_change ) * b + b_change * ( key * b_multi )
        
        lab = ( lab_l, lab_a, lab_b )

        color = hou.Color( ( 0, 0, 0 ) )
        color.setLAB( lab )
        rgb = color.rgb( )
        values += ( ( rgb ), )

    newramp = hou.Ramp ( basis, keys, values )
    ramp_parm.set ( newramp )