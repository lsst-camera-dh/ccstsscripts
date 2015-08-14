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
print "doing initialization"

result = arcsub.synchCommand(10,"setConfigFromFile",acffile);
result = arcsub.synchCommand(20,"applyConfig");

result = arcsub.synchCommand(10,"powerOnCCD");

result = arcsub.synchCommand(10,"setParameter","Expo","1");
result = arcsub.synchCommand(10,"setParameter","Light","1");
#result = arcsub.synchCommand(10,"applyParams");

# move to TS acquisition state
print "setting acquisition state"
tssub.synchCommand(10,"settstest");

# turn lamp on
#result = lampsub.synchCommand(10,"setlamppowerenable",1==1);

#check state of ts devices
print "wait for ts state to become ready";
tsstate = 0
while True:
    print "checking";
    result = tssub.synchCommand(10,"istsready");
    tsstate = result.getResult();
    tsstate=1;
    if tsstate!=0 :
        break
#put in acquisition state
#temp tssub.synchCommand(120,"goteststand");

# go through config file looking for 'flat' instructions, take the flats
seq = 0  # image pair number in sequence

lo_lim = float(eolib.getCfgVal(acqcfgfile, 'FLAT_LOLIM', default='1.0'))
hi_lim = float(eolib.getCfgVal(acqcfgfile, 'FLAT_HILIM', default='120.0'))
wl = float(eolib.getCfgVal(acqcfgfile, 'FLAT_WL', default = "550.0"))

#number of PLCs between readings
nplc = 0.1

print "Scanning config file for FLAT specifications";
fp = open(acqcfgfile,"r");
fpfiles = open("%s/acqfilelist" % cdir,"w");

for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'flat')):
        target = float(tokens[1])
        print "target wl = ";
        print target;

        exptime = eolib.expCheck(calfile, lab, target, wl, hi_lim, lo_lim, test='FLAT', use_nd=False)

        result = arcsub.synchCommand(10,"setParameter","ExpTime",exptime);
        result = arcsub.synchCommand(30,"applyParams");

#        avg = ht.fitsAverage(fname)
#        print "DATA : Average signal = %8.2f DN" % (avg - bias);

        print "image pair number is %d" % seq

        for i in range(imcount):
            print "starting acquisition step for lambda = %8.2f" % wl
#tempqe            result = monosub.synchCommand(30,"setWave",wl);

#tempqe            result = monosub.synchCommand(10,"setFilter",i+1);

# prepare to readout diodes
#            result = pdsub.synchCommand(10,"accumBuffer",200,nplc);
#            result = biassub.synchCommand(10,"accumBuffer",200,nplc);
            result = biassub.synchCommand(100,"accumBuffer",2048,nplc,False);
            result = pdsub.synchCommand(100,"accumBuffer",2048,nplc,False);
# make sure to get some readings before the state of the shutter changes                               
            time.sleep(0.2);

            print "print controller status"
            result = arcsub.synchCommand(45,"printControllerStatus");

            print "starting acquisition, status"
            result = arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));
            timestamp = int(time.time())
            fitsfilename = "ArchonImage-%d-for-seq-%d-exp-%d.fits" % (int(timestamp),seq,i)            
            result = arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

# start acquisition
            result = arcsub.synchCommand(200,"exposeAcquireAndSave");
            print "print controller status just after acquire and save"

            result = arcsub.synchCommand(45,"printControllerStatus");

            print "status after acquire"
            print "done with exposure # %d" % i
            print "getting photodiode readings"

            time.sleep(60.);
            pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)    
            result = pdsub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pdfilename));
            time.sleep(2.);

            pbfilename = "bias-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)    
            result = biassub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pbfilename));

#            readings=result.getResult();
#            for ipd in range(20) :
#                print "Time = %9.2e and measurement = %9.2e" % (readings[1][ipd],readings[0][ipd])
#            print "photo diode readings = "
#            print ["%9.2e" % pdval for pdval in readings]
#            pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)    
#            fpd = open("%s/%s" % (cdir,pdfilename),"w");                        
#            for pdval in readings:
#                fpd.write(`pdval`+"\n");
#            fpd.close();

#            result = biassub.synchCommand(120,"readBuffer");
#            readings=result.getResult();
#            print "bias device readings = "
#            print ["%9.2e" % bsval for bsval in readings]
#            pbfilename = "bias-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)    
#            fpb = open("%s/%s" % (cdir,pbfilename),"w");                        
##            fpb = open("%s/bias-values-for-seq-%d-exp-%d" % (cdir,seq,i),"w");
#            for bsval in readings:
#                fpb.write(`bsval`+"\n");
#            fpb.close();

            fpfiles.write("%s %s %s %d\n" % (fitsfilename,pdfilename,pbfilename,nplc))

        seq = seq + 1     

fpfiles.close();
fp.close();

#   avg = ht.fitsAverage(fname)
#   print "DATA : Average signal = %8.2f DN" % (avg - bias)

fp = open("%s/status.out" % (cdir),"w");

istate=0;
result = tssub.synchCommandLine(10,"getstate");
istate=result.getResult();
fp.write(`istate`+"\n");
result = biassub.synchCommand(10,"readvoltage");
volts=result.getResult();
fp.write(`volts`+"\n");
result = biassub.synchCommand(10,"readcurrent");
curr=result.getResult();
fp.write(`curr`+"\n");
result = vacsub.synchCommand(10,"readpressure");
vac=result.getResult();
fp.write(`vac`+"\n");
result = cryosub.synchCommand(10,"getTemp","A");
temp=result.getResult();
fp.write(`temp`+"\n");

result = tssub.synchCommandLine(10,"printFullState");
print result.getResult();
fp.close();

# move TS to idle state
                    
tssub.synchCommand(10,"setTSIdle");

print "FLAT: END"
