#!/usr/bin/env python
import glob
#import numpy as np
import lcatr.schema

results = []

cdir = "/home/homer/lsst/lcatr/share/bnl_flat_acq3/v0";

fo = open("%s/status.out" % (cdir), "r");
tsstat = fo.readline();
tsvolt = fo.readline();
tscurr = fo.readline();
tspres = fo.readline();
tstemp = fo.readline();
fo.close();

results.append(lcatr.schema.valid(lcatr.schema.get('bnl_flat_acq3'),stat=tsstat,volt=tsvolt,curr=tscurr,pres=tspres,temp=tstemp))

files = glob.glob('%s/ArchonImage*.fits' % (cdir))
#files.append(bnl_flat_acq3_file)
data_products = [lcatr.schema.fileref.make(item) for item in files]
results.extend(data_products)

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
        
