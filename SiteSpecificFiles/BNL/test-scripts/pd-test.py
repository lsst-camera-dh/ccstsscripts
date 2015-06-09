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

cdir = tsCWD

# Initialization
print "doing initialization at %f" % time.time()

arcsub.synchCommand(10,"setConfigFromFile",acffile);
arcsub.synchCommand(20,"applyConfig");
arcsub.synchCommand(10,"powerOnCCD");

arcsub.synchCommand(10,"setParameter","Expo","1");
arcsub.synchCommand(10,"setParameter","Light","1");

# move to TS acquisition state
#print "setting acquisition state"
#tssub.synchCommand(10,"settstest");

# turn lamp on
#lampsub.synchCommand(10,"setlamppowerenable",1==1);


# go through config file looking for 'flat' instructions, take the flats
seq = 0  # image pair number in sequence


print "Scanning config file for FLAT specifications";
fp = open(acqcfgfile,"r");
fpfiles = open("%s/acqfilelist" % cdir,"w");

# wavelength
wl = LAMBDA;
# exposure time
exptime = EXPTIME;
# number of PLCs between readings
nplc = NPLC;



arcsub.synchCommand(10,"setParameter","ExpTime",str(exptime*1000));

print "image pair number is %d" % seq

imcount = 1

for i in range(imcount):
    print "starting acquisition step for lambda = %8.2f" % wl
    monosub.synchCommand(30,"setWave",wl);

#tempqe            monosub.synchCommand(10,"setFilter",i+1);


    pdsub.synchCommand(10,"setcurrentrange",1.0e-6);
    biassub.synchCommand(10,"setcurrentrange",1.0e-6);

# prepare to readout diodes
    print "setting up buffer accumulation at %f" % time.time()
#    pdsub.synchCommand(10,"accumBuffer",1,nplc,True);
#    biassub.asynchCommand("accumBuffer",2048,nplc,False);
    biassub.asynchCommand("accumBuffer",3000,nplc,True);

# make sure to get some readings before the state of the shutter changes
    time.sleep(0.2);
    
#    print "print controller status at %f" % time.time()
#    arcsub.synchCommand(45,"printControllerStatus");
    
    print "set output directory at %f" % time.time()
    arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

    timestamp = time.time()
    fitsfilename = "ArchonImage-%d-for-seq-%d-exp-%d.fits" % (int(timestamp),seq,i)            
    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

# start acquisition
    print "Ready to take image. time = %f" % time.time()
    arcsub.synchCommand(200,"exposeAcquireAndSave");
    print "after click click at %f" % time.time()

#    print "print controller status just after acquire and save"
#    arcsub.synchCommand(45,"printControllerStatus");

    print "status after acquire"
    print "done with exposure # %d" % i
    print "getting photodiode readings at %f" % time.time()
    
    time.sleep(50.);
#    time.sleep(2.);
    
    pbfilename = "bias-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)    
    biassub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pbfilename));

# just temporary to try to resolve a problem
    pdsub.synchCommand(10,"accumBuffer",1,nplc,True);

    pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)    
    pdsub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pdfilename));
    print "Finished getting readings at %f" % time.time()

    fpfiles.write("%s %s %s %f\n" % (fitsfilename,pdfilename,pbfilename,timestamp))

    seq = seq + 1     

fpfiles.close();
fp.close();


fp = open("%s/status.out" % (cdir),"w");


# move TS to idle state
                    
#tssub.synchCommand(10,"setTSIdle");

print "pd-test: END"
