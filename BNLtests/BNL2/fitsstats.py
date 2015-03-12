#!/usr/bin/env python
import glob
#import numpy as np
#import lcatr.schema
import hdrtools as ht
import os
    
results = []

cdir = "/home/ts3prod/prod/lcatr/share/TS3_flat/v2";

fo = open("%s/status.out" % os.getcwd(), "r");
tsstat = fo.readline();
tsvolt = fo.readline();
tscurr = fo.readline();
tspres = fo.readline();
tstemp = fo.readline();
fo.close();

#results.append(lcatr.schema.valid(lcatr.schema.get('TS3_flat'),stat=tsstat,volt=tsvolt,curr=tscurr,pres=tspres,temp=tstemp))

#files = glob.glob('%s/ArchonImage*.fits' % os.getcdw())

print "files found = %s" % files
bias = ht.fitsAverage('%s/ArchonImage_Bias.fits' % (cdir));
    
#for fname in files
fname = "ArchonImageFile_1424272059593.fits"
avg = ht.fitsAverage(fname)
print "DATA : Average signal = %8.2f DN" % (avg - bias)
    
#data_products = [lcatr.schema.fileref.make(item) for item in files]
#results.extend(data_products)

#lcatr.schema.write_file(results)
#lcatr.schema.validate_file()
        
