#!/usr/bin/env python
import glob
#import numpy as np
import lcatr.schema

results = []

cdir = "/home/homer/lsst/lcatr/share/T03_flat/v0";

fo = open("%s/status.out" % (cdir), "r");
tsstat = fo.readline();
tsvolt = fo.readline();
tscurr = fo.readline();
tspres = fo.readline();
tstemp = fo.readline();
fo.close();

results.append(lcatr.schema.valid(lcatr.schema.get('T03_flat'),stat=tsstat,volt=tsvolt,curr=tscurr,pres=tspres,temp=tstemp))

files = glob.glob('%s/ArchonImage*.fits' % (cdir))

data_products = [lcatr.schema.fileref.make(item) for item in files]
results.extend(data_products)

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
        
