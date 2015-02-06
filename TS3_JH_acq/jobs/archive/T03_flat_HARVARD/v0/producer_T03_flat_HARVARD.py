#!/usr/bin/env python
from PythonBinding import *
import os
#import lsst.eotest.sensor as sensorTest
import sys
#from lcatr.harness.helpers import dependency_glob

fileName = "/opt/ccs/lcatr/share/T03_flat_HARVARD/v0/ccsacqflat-full.py"

fo = open(fileName, "r");
content = fo.read();
fo.close();

try:
#Create an instance of the python binding
    ccs1 = CcsJythonInterpreter();
 
 
    print 'starting synch execution'
    result1 = ccs1.syncExecution(content);
    print result1.getOutput();    
 
 
except CcsException as ex:
    print 'Failure', ex

