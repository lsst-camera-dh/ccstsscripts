def fluxCal(lab, new=False, gain=5.0):
    camera = lab['camera']

    gain = float(gain)

    caldir  = eolib.getCfgVal(lab['config'],'BASE_DIR')+'/system'
    fluxcaldir = caldir+'/fluxcal'
    if not (os.path.isdir(fluxcaldir)):
        os.makedirs(fluxcaldir)
    datadir = fluxcaldir+'/data'
    if not (os.path.isdir(datadir)):
        os.makedirs(datadir)
    fitsfiles= glob.glob(datadir+'/*.fits')
    for i in range(len(fitsfiles)):
        os.remove(fitsfiles[i])

    targflux = float(eolib.getCfgVal(lab['config'], 'FLUXCAL_TARGET', default='5000'))
    exp_hilim = float(eolib.getCfgVal(lab['config'], 'FLUXCAL_HILIM', default='60'))
    exp_lolim = float(eolib.getCfgVal(lab['config'], 'FLUXCAL_LOLIM', default='2.0'))

    lab['logger'].log("FLUXCAL: START")
    lab['logger'].log("FLUXCAL: Calibration directory : %s" % fluxcaldir)

    # find the most recent calibration file and use that as source               
    files = sorted(glob.glob(fluxcaldir+'/fluxcal*.txt'))
    if (len(files) != 0):
        print "Number of fluxcal files =", len(files)
        lastcal = files[len(files)-1]
    else:
        lastcal = 'None'
    lab['logger'].log("FLUXCAL: Last calibration file = %s" % lastcal)

    # create a new calibration file and copy header into it                                                                                                   
    newfile = fluxcaldir+"/fluxcal_"+eolib.tstamp()+".txt"
    lab['logger'].log("FLUXCAL: New calibration file = %s" % newfile)

    f = open(newfile, 'w')
    f.write("######################################################################\n")
    f.write("# Flux calibration file: %s\n" % os.path.split(newfile)[1])
    f.write("# Date: %s\n" % time.strftime("%Y%m%d"))
    f.write("# Time: %s\n" % time.strftime("%H:%M:%S"))
    f.write("# Target flux = %8.2f\n" % targflux)
    f.write("# System Gain = %8.2f e-/DN\n" % gain)
    f.write("# Exposure Limits = %8.2f   %8.2f\n" % (exp_lolim, exp_hilim))
    f.write("# Lamp Manufacturer = %s\n" % lab['lamp'].getInfo()[0])
    f.write("# Lamp Model = %s\n" % lab['lamp'].getInfo()[1])
    f.write("# Lamp bulb hours = %s\n" % lab['lamp'].getHours())
    f.write("# Last calibration file: %s\n" % os.path.split(lastcal)[1])
    f.write("######################################################################\n")
    f.close()
    fname = "fluxcal_bias"
    fname = camera.bias_acq(fname, path=datadir, test='FLUXCAL', img='BIAS')
    junkFile(lab,datadir=datadir)  # due to something odd about Reflex program at BNL                                                                         
    bias = ht.fitsAverage(fname)  # in DN                                                                                                                     
    junkFile(lab,datadir=datadir)  # due to something odd about Reflex program at BNL                                                                         

    if ((lastcal == 'None') or (new == True)):
        f = open(newfile, 'a')
        f.write("{:<10}{:^4}{:^12}".format('command','wl','flux'))
        f.write("{:^12}{:^7}\n".format('signal','exptime'))
        f.write("{:<10}{:>4}{:>12}".format('-------','----','----------'))
        f.write("{:>12}{:>9}\n".format('----------','-------'))
        f.close()
        wl = 320
        while (wl <= 1100):
            lab['monochromator'].setWavelength(wl)
            exptime = 2.0
            fname = "fluxcal_%04d" % wl
            fname = camera.exp_acq(fname, exptime, path=datadir, test='FLUXCAL', img='FLAT')
            avg = ht.fitsAverage(fname)      # in DN                                                                                                          
            signal = (avg-bias)*gain         # in electrons                                                                                                   
            flux = max(signal/exptime, 1.0)  # in electrons/second (can't be < 0 !)                                                                           
            f = open(newfile, 'a')
            f.write("{:<10}{:>4d}{:>12.2f}{:>12.2f}{:>9.2f}\n".format('fluxcal',wl,flux,signal,exptime))
            f.close()
            wl = wl + 5
    else:
        f = open(newfile, 'a')
        f.write("{:<10}{:^4}{:^12}{:^12}".format('command','wl','flux','signal'))
        f.write("{:^9}{:^12}{:>10}\n".format('exptime','previous','% change'))
        f.write("{:<10}{:^4}{:>12}{:>12}".format('-------','----','----------','----------'))
        f.write("{:>9}{:>12}{:>10}\n".format('-------','----------','--------'))
        f.close()
        with open(lastcal) as fp:
            for line in fp:
                tokens = str.split(line)
                if ((len(tokens) > 0) and (tokens[0] == 'fluxcal')):
                    wl = int(tokens[1])
                    oldflux = max (float(tokens[2]), 1) # better not be zero or negative                                                                      
                    lab['monochromator'].setWavelength(wl)
                    exptime = min(max(float(targflux)/oldflux, exp_lolim), exp_hilim)
                    fname = "fluxcal_%04d" % wl
                    fname = camera.exp_acq(fname, exptime, path=datadir, test='FLUXCAL', img='FLAT')
                    avg = ht.fitsAverage(fname)      # in DN                                                                                                  
                    signal = (avg-bias)*gain         # in electrons                                                                                           
                    flux = signal/exptime            # in electrons/second                                                                                    
                    if (flux <= 0.0):
                        flux = oldflux    # that's ridiculous, use the old value                                                                              
                    change = ((flux-oldflux)/oldflux) * 100   # percent change since last time                                                                
                    # write the result into the calibration file                                                                         f = open(newfile, 'a')
                    f.write("{:<10}{:>4}{:>12.2f}{:>12.2f}".format('fluxcal',wl,flux,signal))
                    f.write("{:>9.2f}{:>12.2f}{:>10.2f}\n".format(exptime,oldflux,change))
                    f.close()
    lab['logger'].log("FLUXCAL: END")
    return

