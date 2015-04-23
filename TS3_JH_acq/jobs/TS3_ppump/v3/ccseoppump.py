###############################################################################
# ppump
#    script for doing pocket pumping acq
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
    print "attaching Bias subsystem"
    biassub = CCS.attachSubsystem("ts/Bias");
    print "attaching PD subsystem"
    pdsub   = CCS.attachSubsystem("ts/PhotoDiode");
    print "attaching Cryo subsystem"
    cryosub = CCS.attachSubsystem("ts/Cryo");
    print "attaching Vac subsystem"
    vacsub  = CCS.attachSubsystem("ts/VacuumGauge");
    print "attaching Lamp subsystem"
    lampsub = CCS.attachSubsystem("ts/Lamp");
    print "attaching Mono subsystem"
    monosub = CCS.attachSubsystem("ts/Monochromator");
#    monosub.synchCommand(10,"setHandshake",0);
        
    print "Attaching archon subsystem"
    arcsub  = CCS.attachSubsystem("archon");
    
    cdir = tsCWD
    
    time.sleep(3.)

# Initialization
    print "doing initialization"
    
    result = arcsub.synchCommand(20,"setConfigFromFile",acffile);
    reply = result.getResult();
    result = arcsub.synchCommand(25,"applyConfig");
    reply = result.getResult();
    arcsub.synchCommand(10,"powerOnCCD");
    
    arcsub.synchCommand(10,"setParameter","Expo","1");
    arcsub.synchCommand(10,"setParameter","Light","0");
    
# move to TS acquisition state
    print "setting acquisition state"
    result = tssub.synchCommand(60,"setTSTEST");
    rply = result.getResult();
    
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
    result = tssub.synchCommand(120,"goTestStand");
    rply = result.getResult();
    
    wl     = float(eolib.getCfgVal(acqcfgfile, 'PPUMP_WL', default = "550.0"))
    pcount = float(eolib.getCfgVal(acqcfgfile, 'PPUMP_BCOUNT', default = "25"))
    imcount = 2
    
#number of PLCs between readings
    nplc = 1
    
    seq = 0  # image pair number in sequence
    
    monosub.synchCommand(30,"setFilter",1);
    
# go through config file looking for 'ppump' instructions, take the flats
    print "Scanning config file for PPUMP specifications";
    ccd = CCDID
    
    print "Working on CCD %s" % ccd
    
    
    fp = open(acqcfgfile,"r");
    fpfiles = open("%s/acqfilelist" % cdir,"w");
    
    for line in fp:
        tokens = str.split(line)
        if ((len(tokens) > 0) and (tokens[0] == 'ppump')):
    
            wl      = float(tokens[1])
            exptime = float(tokens[2])
            nshifts  = float(tokens[3])
    
            print "starting acquisition step for lambda = %8.2f with exptime %8.2f s" % (wl, exptime)
    
            print "setup for dark exposure"
            arcsub.synchCommand(10,"setParameter","Light","0");
            print "set number of pocket pumps to %d" % nshifts
            arcsub.synchCommand(10,"setParameter","Npump",str(nshifts));
            print "set pocket depth"
            arcsub.synchCommand(10,"setParameter","Pdepth","1");
            print "set wavelength to %f" % wl
            monosub.synchCommand(30,"setWave",wl);
    
# pump with some darks then do a light exposure
# 2sec for the bias
            print "take some bias images with exptime = 0"
            arcsub.synchCommand(10,"setParameter","ExpTime","0"); 
            arcsub.synchCommand(10,"setParameter","Light","0");

            print "setting location of bias fits directory"
            arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

            for i in range(pcount):
# start acquisition
                timestamp = time.time()
                fitsfilename = "%s_ppump_bias_%3.3d_${TIMESTAMP}.fits" % (ccd,seq)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    
                print "Ready to take bias image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()
                time.sleep(0.2)

# take light exposures
            arcsub.synchCommand(10,"setParameter","Light","1");
            arcsub.synchCommand(10,"setParameter","ExpTime",str(int(exptime)));
            print "setting location of fits exposure directory"
            arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));
    
# prepare to readout diodes
            nreads = exptime*60/nplc + 200
            if (nreads > 3000):
                nreads = 3000
                nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

            for i in range(imcount):

# adjust timeout because we will be waiting for the data to become ready
                mywait = nplc/60.*nreads*1.10 ;
                print "Setting timeout to %f s" % mywait
                pdsub.synchCommand(1000,"setTimeout",mywait);

                print "call accumBuffer to start PD recording at %f" % time.time()
                pdresult =  pdsub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);

                print "recording should now be in progress and the time is %f" % time.time()

# start acquisition
                timestamp = time.time()
    
                fitsfilename = "%s_trap_ppump_%3.3d_%3.3d_ppump%d_${TIMESTAMP}.fits" % (ccd,int(wl),seq,i+1)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

# make sure to get some readings before the state of the shutter changes       
                time.sleep(0.2);
    
                print "Ready to take image. time = %f" % time.time()
                result = arcsub.synchCommand(2000,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()
    
                print "done with exposure # %d" % i
                print "getting photodiode readings"
    
                pdfilename = "pd-values_%d-for-seq-%d-exp-%d.txt" % (timestamp,seq,i+1)
# the primary purpose of this is to guarantee that the accumBuffer method has completed
                print "starting the wait for an accumBuffer done status message at %f" % time.time()
                tottime = pdresult.get();

# make sure the sample of the photo diode is complete
                time.sleep(1.)
    
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
                        
    tssub.synchCommand(60,"setTSIdle");

except Exception, ex:                                                     

    raise Exception("There was an exception in the acquisition producer script. The message is\n (%s)\nPlease retry the step or contact an expert," % ex)         


print "PPUMP: END"
