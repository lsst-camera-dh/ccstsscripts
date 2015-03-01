def qe(serno, lab, datadir='.'):
    lab['logger'].log("LAMBDA: START")
    lab['logger'].log("LAMBDA: Data directory : %s" % datadir)

    lo_lim = float(eolib.getCfgVal(lab['config'], 'LAMBDA_LOLIM', default='1.0'))
    hi_lim = float(eolib.getCfgVal(lab['config'], 'LAMBDA_HILIM', default='120.0'))

    bcount = int(eolib.getCfgVal(lab['config'], 'LAMBDA_BCOUNT', default='25'))
    fname = lab['camera'].bias_stack("%s_lambda_bias" % serno, bcount,
                              path=datadir, test='LAMBDA', img='BIAS')
    bias = ht.fitsAverage(fname)

    junkFile(lab,datadir=datadir)  # due to something odd about Reflex program at BNL                                                                         

    imcount = int(eolib.getCfgVal(lab['config'], 'LAMBDA_IMCOUNT', default='1'))
    # go through config file looking for 'lambda' instructions, and take qes                                                                                
    with open(lab['config']) as fp:
        for line in fp:
            tokens = str.split(line)
            if ((len(tokens) > 0) and (tokens[0] == 'lambda')):
                wl = int(tokens[1])
                target = float(tokens[2])
                lab['monochromator'].setWavelength(wl)
                exptime = eolib.expCheck(lab, target, wl, hi_lim, lo_lim,
                                         test='LAMBDA', use_nd=False)
                lab['logger'].log("LAMBDA: %04dnm  %8.2f e-/pix   %6.2f sec"
                           % (wl, target, exptime))
                for i in range(imcount):
                    if (imcount == 1):
                        fname = "%s_lambda_%04d_qe" % (serno, int(wl))
                    else:
                        fname = "%s_lambda_%04d_qe_%03u" % (serno, int(wl), i)
                    fname = lab['camera'].exp_acq(fname, exptime, path=datadir,
                                           test='LAMBDA', img='FLAT')
                    avg = ht.fitsAverage(fname)
                    lab['logger'].log("DATA : Average signal = %8.2f DN" % (avg - bias))
    lab['logger'].log("LAMBDA: END")
    return

