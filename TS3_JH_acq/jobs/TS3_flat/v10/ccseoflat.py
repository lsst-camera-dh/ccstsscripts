###############################################################################
# flat
# Acquire flat image pairs for linearity and gain measurement.
# For each 'flat' command a pair of flat field images are acquired
#
# In the configuration file the format for a flat command is
# flat   signal  
# where signal is the desired acquired signal level in e-/pixel
#
# FLAT_WL is used to determine what wavelength will be used for illumination
#
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time

sys.path.append(libdir);
import eolib

CCS.setThrowExceptions(True);

try:
#attach CCS subsystem Devices for scripting
    print "Attaching teststand subsystems"
    tssub  = CCS.attachSubsystem("ts");
    biassub = CCS.attachSubsystem("ts/Bias");
    pdsub   = CCS.attachSubsystem("ts/PhotoDiode");
    cryosub = CCS.attachSubsystem("ts/Cryo");
    vacsub  = CCS.attachSubsystem("ts/VacuumGauge");
    lampsub = CCS.attachSubsystem("ts/Lamp");
    monosub = CCS.attachSubsystem("ts/Monochromator");

    print "Attaching archon subsystem"
    arcsub  = CCS.attachSubsystem("archon");

    serno = 1   # in the future this will be passed in

    cdir = tsCWD

# Initialization
    print "doing initialization"
    print "resetting PD device"
    pdsub.synchCommand(20,"reset")
    print "initializing archon controller with file %s" % acffile
    arcsub.synchCommand(10,"setConfigFromFile",acffile);
    arcsub.synchCommand(20,"applyConfig");
    arcsub.synchCommand(10,"powerOnCCD");
    
    arcsub.synchCommand(10,"setParameter","Expo","1");
    
# move to TS acquisition state
    print "setting acquisition state"
    tssub.synchCommand(10,"setTSTEST");

#check state of ts devices
    print "wait for ts state to become ready";
    tsstate = 0
    starttim = time.time()
    while True:
        print "checking for test stand to be ready for acq";
        result = tssub.synchCommand(10,"isTestStandReady");
        tsstate = result.getResult();
    # the following line is just for test situations so that there would be no waiting
        tsstate=1;
        if ((time.time()-starttim)>240):
            print "Something is wrong ... we will never make it to a runnable state"
            exit
        if tsstate!=0 :
            break
        time.sleep(5.)
#put in acquisition state
    print "We are ready to go! Ramping the BP bias voltage now."
    tssub.synchCommand(120,"goTestStand");

    print "Now collect some parameters from the config file"
    lo_lim = float(eolib.getCfgVal(acqcfgfile, 'FLAT_LOLIM', default='1.0'))
    hi_lim = float(eolib.getCfgVal(acqcfgfile, 'FLAT_HILIM', default='120.0'))
    imcount = float(eolib.getCfgVal(acqcfgfile, 'FLAT_BCOUNT', default = "2"))
    wl     = float(eolib.getCfgVal(acqcfgfile, 'FLAT_WL', default = "550.0"))

#number of PLCs between readings
    nplc = 1

    print "set the fits directory"
    arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

    seq = 0  # image pair number in sequence

#    monosub.synchCommand(10,"setFilter",5);

# go through config file looking for 'flat' instructions, take the flats
    print "Scanning config file for FLAT specifications";
    ccd = CCDID

    print "Working on CCD %s" % ccd

    fp = open(acqcfgfile,"r");
    fpfiles = open("%s/acqfilelist" % cdir,"w");

    for line in fp:
        tokens = str.split(line)
        if ((len(tokens) > 0) and (tokens[0] == 'flat')):

            target = float(tokens[1])

            print "target wl = %d" % (target);

            exptime = eolib.expCheck(calfile, labname, target, wl, hi_lim, lo_lim, test='FLAT', use_nd=False)

# 2sec for the bias
            arcsub.synchCommand(10,"setParameter","ExpTime","2000"); 

            print "starting acquisition step for lambda = %8.2f with exptime %8.2f s" % (wl, exptime)
 
            print "setting the monochromator wavelength"
#            if (exptime > lo_lim):
#                monosub.synchCommand(30,"setWave",wl);

# take bias images
            print "set controller for bias exposure"
#            arcsub.synchCommand(10,"setParameter","Light","0");
            print "start bias exposure loop"
            bcount = 1
            for i in range(bcount):
                timestamp = time.time()
# 113-03_flat_000_flat1_20140709201020.fits
# 113-03_flat_bias_000_20140709200311.fits
                print "set fits filename"
                fitsfilename = "%s_flat_bias_%3.3d_${timestamp}.fits" % (ccd,seq)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

                print "Ready to take image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()
                time.sleep(2.)

# take light exposures
#            arcsub.synchCommand(10,"setParameter","Light","1");
            arcsub.synchCommand(10,"setParameter","ExpTime",str(exptime*1000));
 
            for i in range(imcount):

# prepare to readout diodes
                nreads = exptime*60/nplc + 200
                if (nreads > 3000):
                    nreads = 3000
                    nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

                print "nreads set to %d and nplc set to %f" % (int(nreads),float(nplc))
                pdresult = pdsub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);
                timestamp = time.time()

# make sure to get some readings before the state of the shutter changes       
                time.sleep(0.2);

# start acquisition
#                arcsub.synchCommand(45,"printControllerStatus");
                print "set fits filename"

                fitsfilename = "%s_flat_%3.3d_flat%d_${timestamp}.fits" % (ccd,seq,i+1)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

                print "Ready to take image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()

# make sure the sample of the photo diode is complete
                time.sleep(5.)

                print "done with exposure # %d" % i
                print "getting photodiode readings"

                pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (int(timestamp),seq,i+1)
#                tottime = pdresult.getResult(); # the primary purpose of this is to guarantee that the accumBuffer method has completed
                print "executing readBuffer"
                pdsub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pdfilename));
                print "Finished getting readings at %f" % time.time()


                fpfiles.write("%s %s/%s %f\n" % (fitsfilename,cdir,pdfilename,timestamp))

            seq = seq + 1

    fpfiles.close();
    fp.close();

    fp = open("%s/status.out" % (cdir),"w");

    istate=0;
    result = tssub.synchCommandLine(10,"getstate");
    istate=result.getResult();
    fp.write(`istate`+"\n");
    
    fp.close();

# move TS to idle state
                    
    tssub.synchCommand(10,"setTSIdle");

#except CcsException as ex:
except:

#    print "There was ean exception in the acquisition of type %s" % ex
    print "There was ean exception in the acquisition"

print "FLAT: END"
