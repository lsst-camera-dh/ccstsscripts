#!/usr/bin/env python
import glob
import lcatr.schema
import os
import stat
    
results = []

#results.append(lcatr.schema.valid(lcatr.schema.get('TS3_flat'),stat=tsstat))

#copy
os.system("cp -vp ~/Desktop/vendorData/* .")
#os.chmod("*.*",stat.S_IRGRP|stat.S_IROTH)
os.system("chmod 644 *.*")

files = glob.glob('*.*')    
data_products = [lcatr.schema.fileref.make(item) for item in files]
results.extend(data_products)

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
