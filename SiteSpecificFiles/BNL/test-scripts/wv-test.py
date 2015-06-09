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

result = biassub.synchCommand(10,"setcurrentrange",0.0002)

fp = open("/home/ts3prod/prod/BNL2/results-wv-test.dat","w");

for wl in range(100,600,10):
    print "starting acquisition step for lambda = %8.2f" % wl
    result = monosub.synchCommand(30,"setWave",wl);
    result = biassub.synchCommand(10,"readcurrent");
    current = result.getResult()
    current = current * -1.0
    print "lambda,current= %f %11.3e" % (wl,current)
    fp.write(`wl`+" "+`current`+"\n");
    time.sleep(0.5);

fp.close();

print "wv-test: END"
