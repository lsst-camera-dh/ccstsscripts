#!/usr/bin/env python
import glob
import lcatr.schema
import hdrtools as ht
import os
    
results = []

jobname = "TS3_flat"

jobdir = "%sshare/%s/%s/" % (os.environ["INST_DIR"], jobname, os.environ["LCATR_VERSION"])

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



fo = open("%s/status.out" % os.getcwd(), "r");
tsstat = fo.readline();
tsvolt = fo.readline();
tscurr = fo.readline();
tspres = fo.readline();
tstemp = fo.readline();
fo.close();

results.append(lcatr.schema.valid(lcatr.schema.get('TS3_flat'),stat=tsstat,volt=tsvolt,curr=tscurr,pres=tspres,temp=tstemp))

files = glob.glob('%s/*.fits,*values*,*log*,*summary*' % os.getcwd())
#bias = ht.fitsAverage('%s/ArchonImage_Bias.fits' % (jobdir));
    
#for fname in files :
#    avg = ht.fitsAverage(fname)
#    print "DATA : Bias = %8.2f    Average signal = %8.2f DN" % (bias,avg - bias)



#files.append("ccseoflat.py")
    
data_products = [lcatr.schema.fileref.make(item) for item in files]
results.extend(data_products)

lcatr.schema.write_file(results)
lcatr.schema.validate_file()