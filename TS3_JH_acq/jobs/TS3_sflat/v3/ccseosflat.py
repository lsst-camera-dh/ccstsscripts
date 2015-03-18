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

CCS.setThrowExceptions(False);

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

cdir = tsCWD

# Initialization
print "doing initialization"

arcsub.synchCommand(10,"setConfigFromFile",acffile);
arcsub.synchCommand(20,"applyConfig");
arcsub.synchCommand(10,"powerOnCCD");

arcsub.synchCommand(10,"setParameter","Expo","1");

# move to TS acquisition state
print "setting acquisition state"
tssub.synchCommand(10,"settstest");


#check state of ts devices
print "wait for ts state to become ready";
tsstate = 0
starttim = time.time()
while True:
    print "checking for test stand to be ready for acq ";
    result = tssub.synchCommand(10,"istsready");
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
tssub.synchCommand(120,"goteststand");

seq = 0  # image pair number in sequence

lo_lim = float(eolib.getCfgVal(acqcfgfile, 'SFLAT_LOLIM', default='1.0'))
hi_lim = float(eolib.getCfgVal(acqcfgfile, 'SFLAT_HILIM', default='120.0'))
imcount = float(eolib.getCfgVal(acqcfgfile, 'SFLAT_BCOUNT', default = "5"))

#number of PLCs between readings
nplc = 1

print "starting acquisition, status"

arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

print "Scanning config file for SFLAT specifications";
ccd = CCDID

print "Working on CCD %s" % ccd

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
        arcsub.synchCommand(10,"setParameter","ExpTime","2000"); 
        result = arcsub.synchCommand(10,"setParameter","Light","0");
        bcount = 1
        for i in range(bcount):
            timestamp = time.time()
            fitsfilename = "%s_sflat_bias_%3.3d_${timestamp}.fits" % (ccd,seq)
            arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

            print "Ready to take image. time = %f" % time.time()
            result = arcsub.synchCommand(200,"exposeAcquireAndSave");
            fitsfilename = result.getResult();
            print "after click click at %f" % time.time()
            time.sleep(2.)

# take light exposures
        result = arcsub.synchCommand(10,"setParameter","Light","1");
        result = arcsub.synchCommand(10,"setParameter","ExpTime",exptime);

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

            result = pdsub.asynchCommand("accumBuffer",int(nreads),nplc,True);
            timestamp = time.time()

# make sure to get some readings before the state of the shutter changes       
            time.sleep(0.2);

# start acquisition                                                                                      
            result = arcsub.synchCommand(45,"printControllerStatus");

            fitsfilename = "%s_sflat_%3.3d_sflat%d_${timestamp}.fits" % (ccd,seq,i+1)
            arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

            print "Ready to take image. time = %f" % time.time()
            result = arcsub.synchCommand(200,"exposeAcquireAndSave");
            fitsfilename = result.getResult();
            print "after click click at %f" % time.time()

# make sure the sample of the photo diode is complete                                                    
            time.sleep(exptime+5.)

            print "done with exposure # %d" % i
            print "getting photodiode readings"

            pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i+1)
            result = pdsub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pdfilename));
            awaytowait=result.getResult();
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

print "SFLAT: END"
