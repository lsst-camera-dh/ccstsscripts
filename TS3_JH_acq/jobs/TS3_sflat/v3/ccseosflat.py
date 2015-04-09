###############################################################################
# sflat
# Acquire sflat image pairs
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

# ramp the bias
    print "go teststand go"
    tssub.synchCommand(120,"goTestStand");
    
    seq = 0  # image pair number in sequence
    
    lo_lim = float(eolib.getCfgVal(acqcfgfile, 'SFLAT_LOLIM', default='1.0'))
    hi_lim = float(eolib.getCfgVal(acqcfgfile, 'SFLAT_HILIM', default='120.0'))
    imcount = float(eolib.getCfgVal(acqcfgfile, 'SFLAT_BCOUNT', default = "5"))
    bcount = 1
    
#number of PLCs between readings
    nplc = 1
    
    ccd = CCDID    
    print "Working on CCD %s" % ccd
    
# go through config file looking for 'sflat' instructions
    print "Scanning config file for SFLAT specifications";
    fp = open(acqcfgfile,"r");
    fpfiles = open("%s/acqfilelist" % cdir,"w");
    
    for line in fp:
        tokens = str.split(line)
        if ((len(tokens) > 0) and (tokens[0] == 'sflat')):
            wl = int(tokens[1])
            target = int(tokens[2])
            exptime = eolib.expCheck(calfile, labname, target, wl, hi_lim, lo_lim, test='FLAT', use_nd=False)
    
            imcount = int(tokens[3])
    
# take bias images
# 2sec for the bias
            arcsub.synchCommand(10,"setParameter","ExpTime","0"); 
            result = arcsub.synchCommand(10,"setParameter","Light","0");

            print "setting location of bias fits directory"
            arcsub.synchCommand(10,"setFitsDirectory","%s/bias" % (cdir));

            for i in range(bcount):
                timestamp = time.time()
                fitsfilename = "%s_sflat_bias_%3.3d_${TIMESTAMP}.fits" % (ccd,seq)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    
                print "Ready to take bias image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()
                time.sleep(0.2)
    
# take light exposures
            result = arcsub.synchCommand(10,"setParameter","Light","1");
            result = arcsub.synchCommand(10,"setParameter","ExpTime",str(int(exptime*1000)));
            print "setting location of fits exposure directory"
            arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));
    
            for i in range(imcount):
                print "starting acquisition step for lambda = %8.2f" % wl
    
                result = monosub.synchCommand(30,"setWave",wl);
    
                result = monosub.synchCommand(10,"setFilter",1); # open position
    
# prepare to readout diodes                                                                              
                nreads = exptime*60/nplc + 200
                if (nreads > 3000):
                    nreads = 3000
                    nplc = exptime*60/(nreads-200)
                    print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

                print "call accumBuffer to start PD recording at %f" % time.time()
                pdresult =  pdsub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);


                result = pdsub.asynchCommand("accumBuffer",int(nreads),nplc,True);
                print "recording should now be in progress and the time is %f" % time.time()
# start acquisition

                timestamp = time.time()
                fitsfilename = "%s_sflat_%3.3d_%3.3d_sflat%d_${TIMESTAMP}.fits" % (ccd,int(wl),seq,i+1)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    

# make sure to get some readings before the state of the shutter changes       
                time.sleep(0.2);
    
    
                print "Ready to take image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()
    
# make sure the sample of the photo diode is complete                                                    
                time.sleep(1.)
    
                print "done with exposure # %d" % i
                print "getting photodiode readings"
    
                pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i+1)
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

print "SFLAT: END"
