###############################################################################
# qe
# Acquire qe images
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
    monosub.synchCommand(10,"setHandshake",0);
    
    print "Attaching archon subsystem"
    arcsub  = CCS.attachSubsystem("archon");


    cdir = tsCWD

# Initialization
    print "doing initialization"
    print "resetting PD device"
    pdsub.synchCommand(20,"reset")
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
    print "go teststand go"
    tssub.synchCommand(120,"goTestStand");

    lo_lim = float(eolib.getCfgVal(acqcfgfile, 'LAMBDA_LOLIM', default='1.0'))
    hi_lim = float(eolib.getCfgVal(acqcfgfile, 'LAMBDA_HILIM', default='120.0'))
    bcount = int(eolib.getCfgVal(acqcfgfile, 'LAMBDA_BCOUNT', default='1'))
    imcount = int(eolib.getCfgVal(acqcfgfile, 'LAMBDA_IMCOUNT', default='1'))

    serno = 1   # in the future this will be passed in
    imcount = 2         

    seq = 0

#number of PLCs between readings                                                  
    nplc = 1

    ccd = CCDID

    print "setting location of fits directory"
    arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

    print "set filter position"
    monosub.synchCommand(10,"setFilter",1); # open position

# go through config file looking for 'qe' instructions, take the qes
    print "Scanning config file for LAMBDA specifications";
    fp = open(acqcfgfile,"r");
    fpfiles = open("%s/acqfilelist" % cdir,"w");

    for line in fp:
        tokens = str.split(line)
        if ((len(tokens) > 0) and (tokens[0] == 'lambda')):
            wl = int(tokens[1])
            target = float(tokens[1])
            print "target wl = %f" % target;

            exptime = eolib.expCheck(calfile, labname, target, wl, hi_lim, lo_lim, test='LAMBDA', use_nd=False)


# take bias images

#   2sec for the bias
            arcsub.synchCommand(10,"setParameter","ExpTime","2000"); 
            arcsub.synchCommand(10,"setParameter","Light","0");

            for i in range(bcount):
                timestamp = time.time()
                fitsfilename = "%s_qe_bias_%3.3d_${timestamp}.fits" % (ccd,seq)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

                print "Ready to take bias image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()
                time.sleep(2.)


# take light exposures
            arcsub.synchCommand(10,"setParameter","Light","1");
            arcsub.synchCommand(10,"setParameter","ExpTime",str(int(exptime*1000)));

# prepare to readout diodes
            nreads = exptime*60/nplc + 200
            if (nreads > 3000):
                nreads = 3000
                nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

            for i in range(imcount):
                print "starting acquisition step for lambda = %8.2f" % wl

                monosub.synchCommand(30,"setWave",wl);

                print "call accumBuffer to start PD recording at %f" % time.time()
                pdresult =  pdsub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);

                print "recording should now be in progress and the time is %f" % time.time()
# start acquisition

                timestamp = time.time()
                fitsfilename = "%s_qe_%3.3d_qe%d_${timestamp}.fits" % (ccd,seq,i+1)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

                print "Ready to take image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()

# make sure the sample of the photo diode is complete

                time.sleep(5.)

                print "done with exposure # %d" % i
                print "getting photodiode readings at time = %f" % time.time();

                pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (int(timestamp),seq,i+1)
# the primary purpose of this is to guarantee that the accumBuffer method has completed
                print "starting the wait for an accumBuffer done status message at %f" % time.time()
                tottime = pdresult.get();
#                msg = CCS.waitForStatusBusMessage(lambda msg : msg.source == "ts/PhotoDiode", 200000)
                print "executing readBuffer, cdir=%s , pdfilename = %s" % (cdir,pdfilename)
                result = pdsub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pdfilename));
                buff = result.getResult()
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
    print "There was an exception in the acquisition at time %f" % time.time()


print "QE: END"
