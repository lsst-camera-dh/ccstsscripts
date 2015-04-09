#!/usr/bin/env python
import os
import sys
import shutil
import pyfits
import lsst.eotest.image_utils as imutils
import lsst.eotest.sensor as sensorTest
from lcatr.harness.helpers import dependency_glob

dark_files = dependency_glob('*_dark_dark*.fits', jobname='TS3_dark')
mask_files = dependency_glob('*_mask.fits')

print mask_files
sys.stdout.flush()

# Infer the sensor_id from the first dark filename as per LCA-10140.
sensor_id = os.path.basename(dark_files[0]).split('_')[0]

print "sensor_id = %s . Dependency will be on %s_eotest_results.fits in flat_pairs" % (sensor_id,sensor_id)

#gainfiles = dependency_glob('%s_eotest_results.fits' % sensor_id, jobname='bright_pixels')
#print "gainfiles = %s" % gainfiles

gain_file = dependency_glob('%s_eotest_results.fits' % sensor_id, jobname='fe55_analysis')[0]
#                            jobname='read_noise')[0]

gains = sensorTest.EOTestResults(gain_file)['GAIN']

# Handle annoying off-by-one issue in amplifier numbering:
gains = dict([(amp, gains[amp-1]) for amp in range(1, 17)])

# Make a local copy to fill with task results.
shutil.copy(gain_file, os.path.basename(gain_file))
task = sensorTest.DarkCurrentTask()
task.run(sensor_id, dark_files, mask_files, gains)
