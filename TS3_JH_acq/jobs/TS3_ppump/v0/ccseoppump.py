###############################################################################
# ppump
# Acquire ppump images
#
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys

sys.path.append(tsCWD);
import eolib

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
result = arcsub.synchCommand(10,"applyParams");

# move to TS acquisition state
print "setting acquisition state"
tssub.synchCommand(10,"settstest");


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
tssub.synchCommand(120,"goteststand");

# go through config file looking for 'ppump' instructions, take the ppumps
seq = 0  # image pair number in sequence

lo_lim = float(eolib.getCfgVal(acqcfgfile, 'FLAT_LOLIM', default='1.0'))
hi_lim = float(eolib.getCfgVal(acqcfgfile, 'FLAT_HILIM', default='120.0'))
wl = float(eolib.getCfgVal(acqcfgfile, 'PPUMP_WL', default = "550.0"))
result = monosub.synchCommand(30,"setWave",wl);

result = monosub.synchCommand(10,"setFilter",5); // open position

print "starting acquisition, status"
result = arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

print "Scanning config file for FLAT specifications";
fp = open(acqcfgfile,"r");
for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'ppump')):
        target = float(tokens[1])
        exptime = eolib.expCheck(calfile, lab, target, wl, hi_lim, lo_lim, test='SFLAT', use_nd=True)
        result = arcsub.synchCommand(10,"setParameter","ExpTime",exptime);
        result = arcsub.synchCommand(30,"applyParams");

        imcount = float(tokens[2])
        shifts = float(tokens[3])
        ppump_file = float(tokens[4])
        print "PPUMP: Acquiring PPUMP data with %6.2fs exposure time" % exptime
        print "PPUMP: %3u shifts per frame." % shifts
        print "PPUMP: Timing file = %s" % ppump_file
        
        seq = 0 

        print "image pair number is %d" % seq

        for i in range(imcount):
            print "starting acquisition step for lambda = %8.2f" % wl



# prepare to readout diodes
            result = pdsub.synchCommand(10,"accumBuffer",60*exptime+20,1);


# start acquisition
# get bias
            result = arcsub.synchCommand(10,"setFitsFilename","%s" % (biasfile));
            result = arcsub.synchCommand(20,"exposeAcquireAndSave");
# get ppump image
            result = arcsub.synchCommand(10,"setFitsFilename","%s" % (fitsfile));
            result = arcsub.synchCommand(20,"exposeAcquireAndSave");
            
            print "status after acquire"
            print "done with exposure # %d" % i
            print "getting photodiode readings"
            result = pdsub.synchCommand(120,"readBuffer");
            readings=result.getResult();
            print "photo diode readings = "
            print ["%9.2e" % i for i in readings]
fp.close();

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

print "PPUMP: END"
