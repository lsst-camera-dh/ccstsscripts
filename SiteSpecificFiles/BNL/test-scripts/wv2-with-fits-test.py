###############################################################################
#  Photo diode test script
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time

sys.path.append(tsCWD);
#import eolib
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
monosub.synchCommand(10,"setHandshake",0);

print "Attaching archon subsystem"
arcsub  = CCS.attachSubsystem("archon");

serno = 1   # in the future this will be passed in

filter = 3

#cdir = tsCWD

# Initialization
print "doing initialization at %f" % time.time()

arcsub.synchCommand(10,"setConfigFromFile",acffile);
arcsub.synchCommand(20,"applyConfig");
arcsub.synchCommand(10,"powerOnCCD");

arcsub.synchCommand(10,"setParameter","Expo","1");
arcsub.synchCommand(10,"setParameter","ExpTime","500"); 

biassub.synchCommand(10,"setcurrentrange",0.0002)

monosub.synchCommand(10,"setFilter",filter);

arcsub.synchCommand(10,"setFitsDirectory","/home/ts3prod/prod/BNL2/wvfits-new-filter%d" % filter);

fp = open("/home/ts3prod/prod/BNL2/results-wv-with-fits-new-filter%d-test2.dat" % filter,"w");

for wl in range(200,1100,2):
    print "starting acquisition step for lambda = %8.2f" % wl
    result = monosub.synchCommand(30,"setWave",wl);
#    result = biassub.synchCommand(10,"readcurrent");
    result = pdsub.synchCommand(10,"readCurrent");
    current = result.getResult()
    current = current * -1.0
    result = monosub.synchCommand(30,"getWave");
    rwl = result.getResult()
    fitsfilename = "wv-test-new-filter%d-%d_${timestamp}.fits" % (filter,wl)

#    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    
#    print "Ready to take image. time = %f" % time.time()
#    result = arcsub.synchCommand(200,"exposeAcquireAndSave");
#    fitsfilename = result.getResult();
    
    print "wavelength,returned wl,current= %f %f %11.3e" % (wl,rwl,current)
    fp.write(`rwl`+" "+`current`+"\n");
    fp.flush()
    time.sleep(0.5);

fp.close();

print "wv-test: END"
