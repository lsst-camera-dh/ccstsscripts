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
arcsub  = CCS.attachSubsystem("archon");

print "doing initialization at %f" % time.time()

arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/archon641-merged2-singleshot-e2v.acf");
#arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/CCD250_20140217_1H30.acf");
#arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/archon641-merged2-singleshot-itl.acf");
result = arcsub.synchCommand(20,"applyConfig");
rply=result.getResult()
result = arcsub.synchCommand(10,"powerOnCCD");
rply=result.getResult()

#arcsub.synchCommand(10,"setAcqParam","Nexpo");
arcsub.synchCommand(10,"setParameter","Expo","1");
arcsub.synchCommand(10,"setParameter","ExpTime","3000"); 

arcsub.synchCommand(10,"setParameter","Light","1");


arcsub.synchCommand(10,"setFitsDirectory","/home/ts3prod/prod/BNL2/");


time.sleep(5)
print "Ready to take image. time = %f" % time.time()
for i in range(5) :
    fitsfilename = "snap_${timestamp}-firstset-%d.fits" % i
    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    result = arcsub.synchCommand(200,"exposeAcquireAndSave");
    rply=result.getResult()

fitsfilename = "snap_${timestamp}-bias.fits"
arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
arcsub.synchCommand(10,"setParameter","ExpTime","1000"); 
result = arcsub.synchCommand(200,"exposeAcquireAndSave");
rply=result.getResult()

arcsub.synchCommand(10,"setParameter","ExpTime","3000"); 
for i in range(2) :
    fitsfilename = "snap_${timestamp}-secondset-%d.fits" % i
    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    result = arcsub.synchCommand(200,"exposeAcquireAndSave");
    rply=result.getResult()

fitsfilename = result.getResult();

print "snap: END"
