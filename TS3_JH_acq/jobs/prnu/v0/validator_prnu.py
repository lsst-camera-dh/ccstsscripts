#!/usr/bin/env python
import glob
import numpy as np
import pyfits
import lcatr.schema

results_file = glob.glob('*eotest_results.fits')[0]

prnu_results = pyfits.open(results_file)['PRNU_RESULTS'].data

results = [lcatr.schema.fileref.make(results_file)]
for wl, stdev, mean in zip(prnu_results['WAVELENGTH'], 
                           prnu_results['STDEV'], prnu_results['MEAN']):
    results.append(lcatr.schema.valid(lcatr.schema.get('prnu'),
                                      wavelength=int(np.round(wl)), 
                                      pixel_stdev=stdev, pixel_mean=mean))

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
