#!/usr/bin/env python
import os
import shutil
import pyfits
import lsst.eotest.image_utils as imutils
import lsst.eotest.sensor as sensorTest
from lcatr.harness.helpers import dependency_glob

trap_file = dependency_glob('*_trap_ppump*.fits', jobname='TS3_ppump')[0]
mask_files = dependency_glob('*_mask.fits')

# Infer the sensor_id from the first dark filename as per LCA-10140.
sensor_id = os.path.basename(trap_file).split('_')[0]

gain_file = dependency_glob('%s_eotest_results.fits' % sensor_id,
                            jobname='prnu')[0]
gains = sensorTest.EOTestResults(gain_file)['GAIN']

# Handle annoying off-by-one issue in amplifier numbering:
gains = dict([(amp, gains[amp-1]) for amp in range(1, 17)])

shutil.copy(gain_file, os.path.basename(gain_file))
task = sensorTest.TrapTask()
task.run(sensor_id, trap_file, mask_files, gains)
