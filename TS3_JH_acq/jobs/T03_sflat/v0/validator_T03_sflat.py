#!/usr/bin/env python
import glob
#import numpy as np
import lcatr.schema
import hdrtools as ht
    
results = []

cdir = "/home/homer/lsst/lcatr/share/T03_sflat/v0";

fo = open("%s/status.out" % (cdir), "r");
tsstat = fo.readline();
tsvolt = fo.readline();
tscurr = fo.readline();
tspres = fo.readline();
tstemp = fo.readline();
fo.close();

results.append(lcatr.schema.valid(lcatr.schema.get('T03_sflat'),stat=tsstat,volt=tsvolt,curr=tscurr,pres=tspres,temp=tstemp))

files = glob.glob('%s/ArchonImage*.fits' % (cdir))
bias = ht.fitsAverage('%s/ArchonImage_Bias.fits' % (cdir));
    
for fname in files
    avg = ht.fitsAverage(fname)
    print "DATA : Average signal = %8.2f DN" % (avg - bias)
    
data_products = [lcatr.schema.fileref.make(item) for item in files]
results.extend(data_products)

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
        
