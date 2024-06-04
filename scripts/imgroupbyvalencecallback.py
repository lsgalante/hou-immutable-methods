def rulecallback( kwargs ):
    node = kwargs[ 'node' ]

    ruleparm = node.parm( 'rule' )
    memoryparm = node.parm( 'memory' )

    rule = ruleparm.eval( )
    memory = memoryparm.eval( )
    newmemory = rule

    if rule == 5:
        if memory == 1:
            ruleparm.set( 4 )
            memoryparm.set( 4 )
        if memory == 4:
            ruleparm.set( 1 )
            memoryparm.set( 1 )
        return

    if rule == 7:
        if memory == 3:
            ruleparm.set( 6 )
            memoryparm.set( 6 )
        if memory == 6:
            ruleparm.set( 3 )
            memoryparm.set( 3 )
        return

    memoryparm.set( rule )