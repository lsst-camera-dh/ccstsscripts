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

arcsub.synchCommand(10,"setConfigFromFile","/home/ts3prod/prod/acfs/bnl_STA_20150714_Fe55.acf");
#print "applying configuration"
#arcsub.synchCommand(20,"applyConfig");
#print "powering on CCD"
#arcsub.synchCommand(300,"powerOnCCD");
#print "setting parameters"
#arcsub.synchCommand(10,"setParameter","Expo","1");
#arcsub.synchCommand(10,"setParameter","ExpTime","500"); 

print "setting up file names and directories"
arcsub.synchCommand(10,"setFitsDirectory","/data1/Fe55/last/");

fitsfilename = "Fe55_${timestamp}.fits"

arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

print "starting loop over exposures"
 
for i in range(25) :
    print "Ready to take image. time = %f" % time.time()
#    result = arcsub.synchCommand(200,"exposeAcquireAndSave");
    result = arcsub.synchCommand(200,"acquireAndSaveImage");
    fitsfilename = result.getResult();
    print "Acquired fits image into file %s" % fitsfilename
    time.sleep(0.1);

print "snap-Fe55: FINISHED"
