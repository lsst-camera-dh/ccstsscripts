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

arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/bnl_STA_20150714.acf");
#arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/archon641-merged2-singleshot-itl.acf");
#arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/archon641-merged2-singleshot-e2v.acf");
#arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/CCD250_20140217_1H30.acf");
#arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/archon641-merged2-singleshot-itl.acf");
result = arcsub.synchCommand(20,"applyConfig");
rply=result.getResult()
result = arcsub.synchCommand(10,"powerOnCCD");
rply=result.getResult()

arcsub.synchCommand(10,"setDefaultCCDTypeName","ITL");
arcsub.synchCommand(10,"setAcqParam","Nexpo");
# test
print "testijng new command setAndApplyParamr"
arcsub.synchCommand(10,"setAndApplyParam","ExpTime","1000"); 
print "survived"

arcsub.synchCommand(10,"setParameter","Expo","1");
arcsub.synchCommand(10,"setParameter","ExpTime","3000"); 

arcsub.synchCommand(10,"setParameter","Light","1");


arcsub.synchCommand(10,"setFitsDirectory","/home/ts3prod/prod/BNL2/");


time.sleep(60.)
print "Ready to take image. time = %f" % time.time()
for i in range(4) :
    fitsfilename = "snap_${timestamp}-firstset-afterwait-%d.fits" % i
    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    result = arcsub.synchCommand(500,"exposeAcquireAndSave");
    rply=result.getResult()
    print "start waiting for end of exposure at %f" % time.time()
    result = arcsub.synchCommand(500,"waitForExpoEnd");
    reply = result.getResult();
    print "finished waiting for end of exposure at %f" % time.time()

for i in range(4) :
    arcsub.synchCommand(10,"setAndApplyParam","ExpTime",str(i*1000)); 
    fitsfilename = "snap_${timestamp}-secondset-afterexptime-%d.fits" % i
    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    result = arcsub.synchCommand(500,"exposeAcquireAndSave");
    rply=result.getResult()
    print "start waiting for end of exposure at %f" % time.time()
    result = arcsub.synchCommand(500,"waitForExpoEnd");
    reply = result.getResult();
    print "finished waiting for end of exposure at %f" % time.time()
    
for i in range(4) :
    fitsfilename = "snap_${timestamp}-thirdset-more-%d.fits" % i
    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
    result = arcsub.synchCommand(500,"exposeAcquireAndSave");
    rply=result.getResult()
    print "start waiting for end of exposure at %f" % time.time()
    result = arcsub.synchCommand(500,"waitForExpoEnd");
    reply = result.getResult();
    print "finished waiting for end of exposure at %f" % time.time()

fitsfilename = "snap_${timestamp}-bias.fits"
arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
arcsub.synchCommand(10,"setParameter","ExpTime","0"); 
result = arcsub.synchCommand(200,"exposeAcquireAndSave");
rply=result.getResult()
result = arcsub.synchCommand(200,"exposeAcquireAndSave");
rply=result.getResult()

#arcsub.synchCommand(10,"setParameter","ExpTime","3000"); 
#for i in range(2) :
#    fitsfilename = "snap_${timestamp}-secondset-%d.fits" % i
#    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
#    result = arcsub.synchCommand(200,"exposeAcquireAndSave");
#    rply=result.getResult()

fitsfilename = result.getResult();

print "snap: END"
