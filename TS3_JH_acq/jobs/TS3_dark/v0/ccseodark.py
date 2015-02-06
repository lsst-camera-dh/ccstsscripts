###############################################################################
# dark
# Acquire dark image pairs
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

cdir = tsCWD

# Initialization
print "doing initialization"

result = arcsub.synchCommand(10,"setConfigFromFile",acffile);
result = arcsub.synchCommand(20,"applyConfig");

result = arcsub.synchCommand(10,"powerOnCCD");

result = arcsub.synchCommand(10,"setParameter","Expo","1");
result = arcsub.synchCommand(10,"setParameter","Light","0");
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

# go through config file looking for 'dark' instructions, take the darks

result = arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));
result = arcsub.synchCommand(10,"setFitsFilename","%s" % (fitsfile));

print "Scanning config file for DARK specifications";
fp = open(acqcfgfile,"r");
for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'dark')):
        exptime = float(tokens[1])
        imcount = int(tokens[2])

        result = arcsub.synchCommand(10,"setParameter","ExpTime",exptime);
        result = arcsub.synchCommand(30,"applyParams");


        for i in range(imcount):
            print "starting acquisition step for lambda = %8.2f" % wl


# start acquisition
            result = arcsub.synchCommand(20,"exposeAcquireAndSave");
            print "print controller status just after acquire and save"

            result = arcsub.synchCommand(45,"printControllerStatus");

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

print "DARK: END"
