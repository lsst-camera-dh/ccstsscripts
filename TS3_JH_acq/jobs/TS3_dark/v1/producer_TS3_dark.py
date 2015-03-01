#!/usr/bin/env python
from PythonBinding import *
import os
import sys

jobname = "TS3_dark"

jobdir = "%sshare/%s/%s/" % (os.environ["INST_DIR"], jobname, os.environ["LCATR_VERSION"])
print "jobdir = %s" % jobdir

sitedir = "%s/TS3_JH_acq/site" % os.environ["VIRTUAL_ENV"]

print "PWD = %s" % os.environ["PWD"]
print "OLDPWD = %s" % os.environ["OLDPWD"]
print "getcwd = %s" % os.getcwd();

fileName = "%s/sitename" % sitedir
fo = open(fileName, "r");
ssitename = fo.read();
fo.close();
sitename = "%s" % ssitename.rstrip()
print "sitename = %s" % sitename


fileName = "%s/ccseodark.py" % jobdir
fo = open(fileName, "r");
content = fo.read();
fo.close();

try:
#Create an instance of the python binding
    ccs1 = CcsJythonInterpreter();
 
    ccs1.syncExecution("tsCWD = '%s'" % os.getcwd());
    print "Executing labname=%s" % sitename
    ccs1.syncExecution("labname = '%s'" % sitename);
    print "Executing libdir=%s" % jobdir
    ccs1.syncExecution("libdir = '%s'" % jobdir);
    ccs1.syncExecution("acffile = '%s/acffile'" % sitedir);
    ccs1.syncExecution("acqcfgfile = '%s/cfgfile'" % sitedir);
    ccs1.syncExecution("calfile = '%s/fluxfile'" % sitedir);
    ccs1.syncExecution("fitsfile = 'ArchonImageFile_${timestamp}.fits'");

 
    print 'starting synch execution'
    result1 = ccs1.syncExecution(content);
    print result1.getOutput();    
 

except CcsException as ex:
    print 'Failure', ex

