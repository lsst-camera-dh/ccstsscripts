#!/usr/bin/env python
import glob
import lcatr.schema
import hdrtools as ht
import os
    
results = []

jobname = os.environ["LCATR_JOB"]
jobdir = "%sshare/%s/%s/" % (os.environ["LCATR_MODULES-PATH"], jobname, os.environ["LCATR_VERSION"])
sitedir = "%sTS3_JH_acq/site" % os.environ["LCATR_MODULES-PATH"]

fpfiles = open("%s/acqfilelist" % os.getcwd(), "r");
for line in fpfiles :
    tokens = str.split(line)
    fitsfile = tokens[0]
    pdfile = tokens[1]
    tstamp = tokens[2]
    try:
        ht.addPDvals(fitsfile,pdfile,"AMP0.MEAS_TIMES","AMP0",tstamp)
    except:
        print "Problem in addPDvals: Check that %s was actually created: " % fitsfile
    try:
        print ht.fitsAverage(fitsfile)
    except:
        print "Problem in fitsAverage: Check that %s was actually created: " % fitsfile
    try:
        ht.hdrsummary(fitsfile,"summary.txt")
# make summary file - new info will be appended to an existing summary
#        ht.hdrsummary(fitsfile,"%s/summary.txt" % os.getcwd())
    except:
        print "Problem in hdrsummary: Check that %s was actually created: " % fitsfile
fpfiles.close()


try:
    fo = open("%s/status.out" % os.getcwd(), "r");
    tsstat = fo.readline();
    fo.close();
except:
    print "Status file MISSING! Something went wrong."

results.append(lcatr.schema.valid(lcatr.schema.get(jobname),stat=tsstat))

os.system("%s/dotemppressplots.sh" % sitedir)

#copy all the lcatr job files too
os.system("cp -vp %s/{*.py,*.fits} ." % jobdir)
os.mkdir("bias")
biasfiles = glob.glob('*bias*.fits')
for file in biasfiles :
    os.system("ln -t bias -s ../%s" % file)

files = glob.glob('*.fits,*values*,*log*,*summary*,*.dat,*.png,*.py')
data_products = [lcatr.schema.fileref.make(item) for item in files]
results.extend(data_products)

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
