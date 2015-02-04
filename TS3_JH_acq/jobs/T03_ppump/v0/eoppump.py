def ppump(serno, lab, datadir='.', verbose=True):
    lab['logger'].log("PPUMP: START")
    lab['logger'].log("PPUMP: Data directory : %s" % datadir)

    ppump_time  = str.upper(eolib.getCfgVal(lab['config'], 'TIM_FILE'))

    # get wavelength from config file, default to 550nm, then set monochromator                                                                               
    wl = float(eolib.getCfgVal(lab['config'], 'PPUMP_WL', default='550'))
    lab['monochromator'].setWavelength(float(wl))

    # get bias count from config file, default to 25, take bias frames                                                                                        
    bcount  = int(eolib.getCfgVal(lab['config'], 'PPUMP_BCOUNT', default='25'))
    fname = lab['camera'].bias_stack("%s_ppump_bias" % serno, bcount,
                              path=datadir, test='PPUMP', img='BIAS')

    junkFile(lab,datadir=datadir)  # due to something odd about Reflex program at BNL                                                                         

    # Go through config file looking for 'ppump' instructions                                                                                                 
    # and take the pocket pumped images, ppumps, and biases                                                                                                    
    with open(lab['config']) as fp:
        for line in fp:
            tokens = str.split(line)
            if ((len(tokens) > 0) and (tokens[0] == 'ppump')):
                target = float(tokens[1])
                exptime = eolib.expCheck(lab, target, wl, hi_lim, lo_lim,
                                         test='SFLAT', use_nd=True)
                imcount = int(tokens[2])
                shifts  = int(tokens[3])
                ppump_file = tokens[4]
                lab['logger'].log("PPUMP: Acquiring PPUMP data with %6.2fs exposure time" % exptime)
                lab['logger'].log("PPUMP: %3u shifts per frame." % shifts )
                lab['logger'].log("PPUMP: Timing file = %s" % ppump_file)
                # set controller for correct number of shifts                                                                                                 
                # ccdctrl.ppshifts(shifts)       # how?                                                                                                       
                seq = 0
                for i in range(imcount):
                    # acquire a bias                                                                                                                          
                    #fname = "%s_ppump_%06.2f_%03u_bias" % (serno, exptime, seq)                                                                              
                    #eolib.bias_acq(fname)                                                                                                                    
                    # acquire a ppump                                                                                                                          
                    # ccdctrl.timing(ppump_time)       # load timing file: how?                                                                                
                    fname = "%s_ppump_%06.2f_%03u_ppump" % (serno, exptime, seq)
                    fname = lab['camera'].exp_acq(fname, exptime, path=datadir,
                                           test='PPUMP', img='FLAT')
                    # acquire a ppump image                                                                                                                   
                    # load pocket pumping timing file                                                                                                         
                    # ccdctrl.timing(ppump_file)       # load timing file: how?                                                                               
                    # set controller for correct number of shifts                                                                                             
                    # ccdctrl.ppshifts(shifts)         # how?                                                                                                 
                    fname = "%s_ppump_%06.2f_%03u_pump" % (serno, exptime, seq)
                    fname = lab['camera'].exp_acq(fname, exptime, path=datadir,
                                           test='PPUMP', img='PPUMP')
                    seq = seq + 1
    lab['logger'].log("PPUMP: END")
    return
