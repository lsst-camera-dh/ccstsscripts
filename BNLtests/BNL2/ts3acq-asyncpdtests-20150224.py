#!/usr/bin/env python
from PythonBinding import *
import os
#import lsst.eotest.sensor as sensorTest
import sys
import hdrtools as ht



#from lcatr.harness.helpers import dependency_glob
print "reading file %s" % sys.argv[1]
fileName = sys.argv[1]
fo = open(fileName, "r");
content = fo.read();
fo.close();
print "sending to Jython"
try:
#Create an instance of the python binding
    ccs1 = CcsJythonInterpreter("ccsscript");
 
    ccs1.syncExecution("tsCWD = '%s'" % os.getcwd());
    ccs1.syncExecution("lab = 'BNL'");
    ccs1.syncExecution("LAMBDA = 500.");
    ccs1.syncExecution("EXPTIME = 250");
    ccs1.syncExecution("NPLC = 0.01");

    ccs1.syncExecution("acffile = '%s/archon641-merged2-singleshot.acf'" % os.getcwd());
    ccs1.syncExecution("acqcfgfile = '%s/BNL-short.cfg'" % os.getcwd());
    ccs1.syncExecution("calfile = '%s/fluxcal_20140529150721.txt'" % os.getcwd(
));
    print 'starting synch execution'
    result1 = ccs1.syncExecution(content);
    print result1.getOutput();    
 
 
except CcsException as ex:
    print 'Failure', ex

fpfiles = open("acqfilelist", "r");
for line in fpfiles :
    tokens = str.split(line)
    fitsfile = tokens[0]
    pdfile = tokens[1]
    biasfile = tokens[2]
    nplc = tokens[3]
    try:
        ht.addPDvals(fitsfile,pdfile,"PhotoDiode1Readings",nplc)
        ht.addPDvals(fitsfile,biasfile,"PhotoDiode2Readings",nplc)
        print ht.fitsAverage(fitsfile)
    except:
        print "check that %s was actually created" % fitsfile

fpfiles.close()

#fitsfile = "ArchonImageFile_1423709683459.fits"
