def dark(serno, lab, datadir='.'):
    lab['logger'].log("DARK : START" )
    lab['logger'].log("DARK : Data directory : %s" % datadir)

    lab['monochromator'].setFilter(1)
    lab['monochromator'].closeShutter()
    bcount  = int(eolib.getCfgVal(lab['config'], 'DARK_BCOUNT', default='25'))
    fname = lab['camera'].bias_stack("%s_dark_bias" % serno, bcount,
                              path=datadir, test='DARK', img='BIAS')

    delay  = int(eolib.getCfgVal(lab['config'], 'DARK_DELAY', default='0'))

    junkFile(lab,datadir=datadir)  # due to something odd about Reflex program at BNL                                                                         

    # Go through config file looking for 'dark' instructions                                                                                                  
    with open(lab['config']) as fp:
        for line in fp:
            tokens = str.split(line)
            if ((len(tokens) > 0) and (tokens[0] == 'dark')):
                exptime = float(tokens[1])
                imcount = int(tokens[2])
                lab['camera'].dark_stack("%s_dark_dark_%06.2f" % (serno, exptime), exptime,
                           imcount, path=datadir, test='DARK', img='DARK', delay=delay)
    lab['logger'].log("DARK : END" )

    return
