#!/usr/bin/env python
import os
import sys
import lsst.eotest.sensor as sensorTest
from lcatr.harness.helpers import dependency_glob

fe55_files = dependency_glob('*fe55_fe55*.fits', jobname='TS3_fe55')

print fe55_files
sys.stdout.flush()

# Infer the sensor_id from the first Fe55 filename as per LCA-10140.
sensor_id = os.path.basename(fe55_files[0]).split('_')[0]

# Roll-off defects mask needs an input file to get the vendor
# geometry, and will be used for all analyses.
#
rolloff_mask_file = '%s_rolloff_defects_mask.fits' % sensor_id
sensorTest.rolloff_mask(fe55_files[0], rolloff_mask_file)

task = sensorTest.Fe55Task()
task.run(sensor_id, fe55_files, (rolloff_mask_file,))

#
# @todo: figure out how to set task.config.chiprob_min in JH context.
#
