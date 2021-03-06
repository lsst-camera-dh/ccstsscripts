#!/usr/bin/env python
from PythonBinding import *
import glob
import os
import sys

jobname = os.environ["LCATR_JOB"]

jobdir = "%sshare/%s/%s/" % (os.environ["LCATR_MODULES-PATH"], jobname, os.environ["LCATR_VERSION"])
print "jobdir = %s" % jobdir

sitedir = "%sTS3_JH_acq/site" % os.environ["LCATR_MODULES-PATH"]

print "PWD = %s" % os.environ["PWD"]
print "OLDPWD = %s" % os.environ["OLDPWD"]
print "getcwd = %s" % os.getcwd();

fileName = "%s/sitename" % sitedir
fo = open(fileName, "r");
ssitename = fo.read();
fo.close();
sitename = "%s" % ssitename.rstrip()
print "sitename = %s" % sitename


fileName = glob.glob('%s/ccseo*.py' % jobdir)[0]
#fileName = "%s/ccseoflat.py" % jobdir
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
    acffile = "%s/acffile" % sitedir
    cfgfile = "%s/cfgfile" % sitedir
    print "acffile = '%s'" % acffile
    ccs1.syncExecution("acffile = '%s'" % acffile);
    ccs1.syncExecution("acqcfgfile = '%s'" % cfgfile);

# add links to the acf and cfg file so that they will get archived too
    os.system("cp -p %s acf.used" % acffile);
    os.system("cp -p %s cfg.used" % cfgfile);

    ccs1.syncExecution("calfile = '%s/fluxfile'" % sitedir);
    ccs1.syncExecution("CCDID = '%s'" % os.environ["LCATR_UNIT_ID"]);

    print 'starting synch execution'
    result1 = ccs1.syncExecution(content);
    llog = result1.getOutput();    
    print llog
    fo = open("job.log", "w");
    fo.write(llog);
    fo.close();

except CcsException as ex:
    print 'Failure', ex

