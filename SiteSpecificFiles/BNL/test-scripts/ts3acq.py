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
    ccs1.syncExecution("libdir = '%s'" % os.getcwd());
    ccs1.syncExecution("jobdir = '%s'" % os.getcwd());
    ccs1.syncExecution("lab = 'BNL'");
    ccs1.syncExecution("labname = 'BNL'");
    ccs1.syncExecution("LAMBDA = 500.");
    ccs1.syncExecution("EXPTIME = 29");
#    ccs1.syncExecution("NPLC = 0.17");
    ccs1.syncExecution("NPLC = 1.0");

    ccs1.syncExecution("acffile = '%s/archon641-merged2-singleshot.acf'" % os.getcwd());
    ccs1.syncExecution("acqcfgfile = '%s/BNL-short.cfg'" % os.getcwd());
    ccs1.syncExecution("calfile = '%s/fluxcal_20140529150721.txt'" % os.getcwd(
));
    ccs1.syncExecution("CCDID = 112-10");
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
#    biasfile = tokens[2]
    tstamp = tokens[2]
    try:
        ht.addPDvals(fitsfile,pdfile,"AMP0.MEAS_TIMES","AMP0",tstamp)
#        ht.addPDvals(fitsfile,biasfile,"AMP1.MEAS_TIMES","AMP1",tstamp)
        print ht.fitsAverage(fitsfile)
        ht.hdrsummary(fitsfile,"summary.txt")
    except:
        print "check that %s was actually created" % fitsfile

fpfiles.close()

#fitsfile = "ArchonImageFile_1423709683459.fits"
