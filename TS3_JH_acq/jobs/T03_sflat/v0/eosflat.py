def sflat(serno, lab, datadir='.'):
    lab['logger'].log("SFLAT : START")
    lab['logger'].log("SFLAT : Data directory : %s" % datadir)

    lo_lim = float(eolib.getCfgVal(lab['config'], 'SFLAT_LOLIM', default='1.0'))
    hi_lim = float(eolib.getCfgVal(lab['config'], 'SFLAT_HILIM', default='120.0'))

    bcount = int(eolib.getCfgVal(lab['config'], 'SFLAT_BCOUNT', default='25'))
    fname = lab['camera'].bias_stack("%s_sflat_bias" % serno, bcount,
                              path=datadir, test='SFLAT', img='BIAS')
    bias = ht.fitsAverage(fname)
    lab['logger'].log("DATA : Bias level = %8.2f DN" % bias)

    junkFile(lab,datadir=datadir)  # due to something odd about Reflex program at BNL                                                                         

    # go through config file looking for 'sflat' instructions, acquire the sflats                                                                              
    with open(lab['config']) as fp:
        for line in fp:
            tokens = str.split(line)
            if ((len(tokens) > 0) and (tokens[0] == 'sflat')):
                wl = int(tokens[1])
                target = int(tokens[2])
                lab['monochromator'].setWavelength(wl)
                exptime = eolib.expCheck(lab, target, wl, hi_lim, lo_lim,
                                         test='SFLAT', use_nd=True)
                imcount = int(tokens[3])
                lab['logger'].log("SFLAT : %04dnm  %8.2f e-/pix   %6.2f sec  %d "
                                  % (wl, target, exptime, imcount))
                fname = "%s_sflat_%04d_%06d" % (serno, int(wl), int(target))
                fname= lab['camera'].exp_stack(fname, exptime, imcount,
                                               path=datadir, test='SFLAT', img='FLAT')
                avg = ht.fitsAverage(fname)
                lab['logger'].log("DATA : Average signal = %8.2f DN" % (avg - bias))
    return

