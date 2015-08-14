###############################################################################
#  Photo diode test script
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time

sys.path.append(tsCWD);

CCS.setThrowExceptions(True);

print "Attaching archon subsystem"
arcsub  = CCS.attachSubsystem("archonSim");

print "doing initialization at %f" % time.time()

arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/lcatr/TS3_JH_acq/site/archon641-merged2-singleshot.acf");
#arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/archon641-merged2-singleshot-itl.acf");
arcsub.synchCommand(20,"applyConfig");
arcsub.synchCommand(10,"powerOnCCD");

arcsub.synchCommand(10,"setParameter","Expo","1");
arcsub.synchCommand(10,"setParameter","ExpTime","500"); 

arcsub.synchCommand(10,"setFitsDirectory","/home/ts3prod/prod/BNL2/");

fitsfilename = "snap_${timestamp}.fits"

arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    
print "Ready to take image. time = %f" % time.time()
result = arcsub.synchCommand(200,"exposeAcquireAndSave");
fitsfilename = result.getResult();

print "snap: END"
