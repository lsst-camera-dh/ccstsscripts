#!/usr/bin/env python
import glob
#import numpy as np
import lcatr.schema

results = []

fo = open("/home/homer/lsst/lcatr/share/flat_acq/v0/status.out", "r");
tsstat = fo.read();
fo.close();

results.append(lcatr.schema.valid(lcatr.schema.get('flat_acq'),
                                                                       stat=tsstat))

files = glob.glob('/home/homer/lsst/Archon*.fits')
#files.append(read_noise_file)
data_products = [lcatr.schema.fileref.make(item) for item in files]
results.extend(data_products)

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
        
