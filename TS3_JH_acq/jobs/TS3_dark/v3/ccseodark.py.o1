###############################################################################
# dark
# Acquire dark image pairs
#
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time

sys.path.append(libdir);
#import eolib

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
    pdsub.synchCommand(10,"reset");
    
    arcsub.synchCommand(10,"setConfigFromFile",acffile);
    arcsub.synchCommand(20,"applyConfig");
    
    arcsub.synchCommand(10,"powerOnCCD");
    
    arcsub.synchCommand(10,"setParameter","Expo","1");
    arcsub.synchCommand(10,"setParameter","Light","0");
    
# move to TS acquisition state
    print "setting acquisition state"
    result = tssub.synchCommand(10,"setTSTEST");
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

    
    # go through config file looking for 'dark' instructions, take the darks
    
    arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));
    
#number of PLCs between readings
    nplc = 1.0
    
    ccd = CCDID
    print "Working on CCD %s" % ccd

    seq = 0
    
    print "Scanning config file for DARK specifications";
    fp = open(acqcfgfile,"r");
    fpfiles = open("%s/acqfilelist" % cdir,"w");
    
    for line in fp:
        tokens = str.split(line)
        if ((len(tokens) > 0) and (tokens[0] == 'dark')):
            exptime = float(tokens[1])
            imcount = int(tokens[2])
    
            arcsub.synchCommand(10,"setParameter","ExpTime",str(int(exptime*1000)));
    
# prepare to readout diodes
            nreads = exptime*60/nplc + 200
            if (nreads > 3000):
                nreads = 3000
                nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

            for i in range(imcount):

                print "call accumBuffer to start PD recording at %f" % time.time()
                pdresult =  pdsub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);

                print "recording should now be in progress and the time is %f" % time.time()

# start acquisition

                timestamp = time.time()

                fitsfilename = "%s_dark_dark%d_${TIMESTAMP}.fits" % (ccd,i+1)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    
                print "Ready to take image. time = %f" % time.time()
                result = arcsub.synchCommand(2000,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()
    
                print "done with exposure # %d" % i
                print "getting photodiode readings at time = %f" % time.time();

                pdfilename = "pd-values_%d-for-seq-%d-exp-%d.txt" % (int(timestamp),seq,i+1)

# the primary purpose of this is to guarantee that the accumBuffer method has completed
                print "starting the wait for an accumBuffer done status message at %f" % time.time()
                tottime = pdresult.get();

# make sure the sample of the photo diode is complete
                time.sleep(5.)
    
# adjust timeout because we will be waiting for the data to become ready
                mywait = nplc/60.*nreads*1.10 ;
                print "Setting timeout to %f s" % mywait
                pdsub.synchCommand(1000,"setTimeout",mywait);

                print "executing readBuffer, cdir=%s , pdfilename = %s" % (cdir,pdfilename)
                result = pdsub.synchCommand(900,"readBuffer","%s/%s" % (cdir,pdfilename));
                buff = result.getResult()
                print "Finished getting readings at %f" % time.time()

# reset timeout to something reasonable for a regular command
                pdsub.synchCommand(1000,"setTimeout",10.);

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


print "DARK: END"
