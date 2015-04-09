#!/usr/bin/env python
import os
import pyfits
import lsst.eotest.image_utils as imutils
import lsst.eotest.sensor as sensorTest
from lcatr.harness.helpers import dependency_glob

sensorTestDir = os.path.split(sensorTest.__file__)[0]
ccd_cal_file = os.path.join(sensorTestDir, 'qe', 'OD142.csv')
sph_cal_file = os.path.join(sensorTestDir, 'qe', 'OD143.csv')
wlscan_file = os.path.join(sensorTestDir, 'qe', 'WLscan.txt')

lambda_files = dependency_glob('*_lambda_*.fits', jobname='TS3_qe')
mask_files = dependency_glob('*_mask.fits')

# Infer the sensor_id from the first input filename as per LCA-10140.
sensor_id = os.path.basename(lambda_files[0]).split('_')[0]

gain_file = dependency_glob('%s_eotest_results.fits' % sensor_id,
                            jobname='fe55_analysis')[0]
gains = sensorTest.EOTestResults(gain_file)['GAIN']

# Handle annoying off-by-one issue in amplifier numbering:
gains = dict([(amp, gains[amp-1]) for amp in range(1, 17)])

task = sensorTest.QeTask()
task.run(sensor_id, lambda_files, ccd_cal_file, sph_cal_file,
         wlscan_file, mask_files, gains)
