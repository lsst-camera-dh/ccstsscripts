#!/usr/bin/env python
import shutil
import glob
import numpy as np
import pyfits
import lsst.eotest.sensor as sensorTest
import lsst.eotest.image_utils as imutils
import lcatr.schema

#
# glob the output files from producer script. (If the sensor_id were
# available, then the output filenames could be used explicitly.)
#
gain_file = glob.glob('*_eotest_results.fits')[0]
psf_results = glob.glob('*_psf_results*.fits')[0]
rolloff_mask = glob.glob('*_rolloff_defects_mask.fits')[0]

results = []

gain_data = sensorTest.EOTestResults(gain_file)['GAIN']
for amp, gain_value in zip(imutils.allAmps, gain_data):
    results.append(lcatr.schema.valid(lcatr.schema.get('fe55_analysis'),
                                      amp=amp, gain=gain_value))

results.extend([lcatr.schema.fileref.make(x) for x in (psf_results,
                                                       gain_file,
                                                       rolloff_mask)])

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
