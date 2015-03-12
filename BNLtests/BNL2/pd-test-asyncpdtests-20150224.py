###############################################################################
#  Photo diode test script
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time

sys.path.append(tsCWD);
import eolib
#import hdrtools as ht

CCS.setThrowExceptions(False);

#attach CCS subsystem Devices for scripting
print "Attaching teststand subsystems"
tssub  = CCS.attachSubsystem("ts");
biassub = CCS.attachSubsystem("ts/Bias");
pdsub = CCS.attachSubsystem("ts/PhotoDiode");
cryosub = CCS.attachSubsystem("ts/Cryo");
vacsub  = CCS.attachSubsystem("ts/VacuumGauge");
lampsub = CCS.attachSubsystem("ts/Lamp");
monosub = CCS.attachSubsystem("ts/Monochromator");
    
print "Attaching archon subsystem"
arcsub  = CCS.attachSubsystem("archon");

serno = 1   # in the future this will be passed in
imcount = 2         

cdir = tsCWD

# Initialization
print "doing initialization at %f" % time.time()

result = arcsub.synchCommand(10,"setConfigFromFile",acffile);
result = arcsub.synchCommand(20,"applyConfig");

result = arcsub.synchCommand(10,"powerOnCCD");

result = arcsub.synchCommand(10,"setParameter","Expo","1");
result = arcsub.synchCommand(10,"setParameter","Light","1");
#result = arcsub.synchCommand(10,"applyParams");

# move to TS acquisition state
#print "setting acquisition state"
#tssub.synchCommand(10,"settstest");

# turn lamp on
#result = lampsub.synchCommand(10,"setlamppowerenable",1==1);

#check state of ts devices
#print "wait for ts state to become ready";
#tsstate = 0
#while True:
#    print "checking";
#    result = tssub.synchCommand(10,"istsready");
#    tsstate = result.getResult();
#    tsstate=1;
#    if tsstate!=0 :
#        break
#put in acquisition state
#temp tssub.synchCommand(120,"goteststand");

# go through config file looking for 'flat' instructions, take the flats
seq = 0  # image pair number in sequence

#lo_lim = float(eolib.getCfgVal(acqcfgfile, 'FLAT_LOLIM', default='1.0'))
#hi_lim = float(eolib.getCfgVal(acqcfgfile, 'FLAT_HILIM', default='120.0'))
#wl = float(eolib.getCfgVal(acqcfgfile, 'FLAT_WL', default = "550.0"))

#number of PLCs between readings
nplc = 0.1

print "Scanning config file for FLAT specifications";
fp = open(acqcfgfile,"r");
fpfiles = open("%s/acqfilelist" % cdir,"w");

wl = LAMBDA;
exptime = EXPTIME;
nplc = NPLC;

print "applying parameters at %f " % time.time()

result = arcsub.synchCommand(10,"setParameter","ExpTime",exptime);
result = arcsub.synchCommand(30,"applyParams");



print "image pair number is %d" % seq

imcount = 1

for i in range(imcount):
    print "starting acquisition step for lambda = %8.2f" % wl
#tempqe            result = monosub.synchCommand(30,"setWave",wl);

#tempqe            result = monosub.synchCommand(10,"setFilter",i+1);

# prepare to readout diodes
#    result = biassub.synchCommand(10,"accumBuffer",1,nplc);
#    result = pdsub.asynchCommand("accumBuffer",100,nplc);

    print "setting up buffer accumulation at %f" % time.time()
    result = pdsub.synchCommand(10,"accumBuffer",1,nplc);
    result = biassub.asynchCommand("accumBuffer",1000,nplc);
#    time.sleep(1.);
    
    print "print controller status at %f" % time.time()
    result = arcsub.synchCommand(45,"printControllerStatus");
    
    print "set output directory at %f" % time.time()
    result = arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

    timestamp = time.time()
    fitsfilename = "ArchonImage-%d-for-seq-%d-exp-%d.fits" % (int(timestamp),seq,i)            
    result = arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

# start acquisition
    print "Ready to take image. time = %f" % time.time()
    result = arcsub.synchCommand(60,"exposeAcquireAndSave");
    result = arcsub.synchCommand(60,"exposeAcquireAndSave");
    result = arcsub.synchCommand(60,"exposeAcquireAndSave");
    print "after click click at %f" % time.time()
    print "print controller status just after acquire and save"

    result = arcsub.synchCommand(45,"printControllerStatus");

    print "status after acquire"
    print "done with exposure # %d" % i
    print "getting photodiode readings at %f" % time.time()
    
    time.sleep(20.);
    pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)    
    result = pdsub.synchCommand(120,"readBuffer","%s/%s" % (cdir,pdfilename));
#    time.sleep(2.);
    
    pbfilename = "bias-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)    
    result = biassub.synchCommand(120,"readBuffer","%s/%s" % (cdir,pbfilename));


    fpfiles.write("%s %s %s %d\n" % (fitsfilename,pdfilename,pbfilename,timestamp))

    seq = seq + 1     

fpfiles.close();
fp.close();


fp = open("%s/status.out" % (cdir),"w");


# move TS to idle state
                    
#tssub.synchCommand(10,"setTSIdle");

print "pd-test: END"
