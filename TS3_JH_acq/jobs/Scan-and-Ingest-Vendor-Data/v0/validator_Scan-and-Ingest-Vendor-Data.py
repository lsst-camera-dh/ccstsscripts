#!/usr/bin/env python
import glob
import os
    
results = []

#results.append(lcatr.schema.valid(lcatr.schema.get('TS3_flat'),stat=tsstat))

#copy
os.system("cp -vp /tmp/scan/* .")

files = glob.glob('*.*' % os.getcwd())    
data_products = [lcatr.schema.fileref.make(item) for item in files]
results.extend(data_products)

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
