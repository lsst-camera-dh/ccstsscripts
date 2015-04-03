def fe55(serno, lab, datadir='.'):
    lab['logger'].log("FE55 : START")
    lab['logger'].log("FE55 : Data directory : %s" % datadir)

    # enable the Fe55 arm                                                                                                                                     
    lab['monochromator'].setFilter(1)
    lab['monochromator'].closeShutter()
    lab['shutterMux'].setChannel(lab['shutterMux'].XED_SHUTTER)
    clearCCD(lab,datadir=datadir)  # in case the arm moved or something                                                                                       

    bcount  = int(eolib.getCfgVal(lab['config'], 'FE55_BCOUNT', default='25'))
    fname = lab['camera'].bias_stack("%s_fe55_bias" % serno, bcount,
                              path=datadir, test='FE55', img='BIAS')

    junkFile(lab,datadir=datadir)  # due to something odd about Reflex program at BNL                                                                         

    # Go through config file looking for 'fe55' instructions                                                                                                  
    dcount  = int(eolib.getCfgVal(lab['config'], 'FE55_DCOUNT', default='5'))
    with open(lab['config']) as fp:
        for line in fp:
            tokens = str.split(line)
            if ((len(tokens) > 0) and (tokens[0] == 'fe55')):
                exptime = float(tokens[1])
                imcount = int(tokens[2])
                fe55set(serno, lab, exptime, dcount, imcount, datadir=datadir)
    lab['logger'].log("FE55 : END")
    # disable the Fe55 arm (and enable the monochromator shutter)                                                                                             
    lab['shutterMux'].setChannel(lab['shutterMux'].MONO_SHUTTER)
    return
