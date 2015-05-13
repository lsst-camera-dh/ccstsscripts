#!/usr/bin/env python
import os
import shutil
import pyfits
import pylab
import lsst.eotest.sensor as sensorTest
from lcatr.harness.helpers import dependency_glob

results_file = dependency_glob('*_eotest_results.fits',
                               jobname='flat_pairs')[0]

#results_file = dependency_glob('*_eotest_results.fits',
#                               jobname='fe55_analysis')[0]

# Infer the sensor_id from the results filename.
sensor_id = os.path.basename(results_file).split('_')[0]

shutil.copy(results_file, os.path.basename(results_file))

plots = sensorTest.EOTestPlots(sensor_id, results_file=results_file)

# Fe55 flux distribution fits
fe55_file = dependency_glob('%s_psf_results*.fits' % sensor_id,
                            jobname='fe55_analysis')[0]
plots.fe55_dists(fe55_file=fe55_file)
pylab.savefig('%s_fe55_dists.png' % sensor_id)

# PSF distributions from Fe55 fits
plots.psf_dists(fe55_file=fe55_file)
pylab.savefig('%s_psf_dists.png' % sensor_id)

# Photon Transfer Curves
ptc_file = dependency_glob('%s_ptc.fits' % sensor_id, jobname='ptc')[0]
plots.ptcs(ptc_file=ptc_file)
pylab.savefig('%s_ptcs.png' % sensor_id)

# Linearity plots
detresp_file = dependency_glob('%s_det_response.fits' % sensor_id,
                               jobname='flat_pairs')[0]
plots.linearity(ptc_file=ptc_file, detresp_file=detresp_file)
pylab.savefig('%s_linearity.png' % sensor_id)

# System Gain per segment
plots.gains()
pylab.savefig('%s_gains.png' % sensor_id)

# Read Noise per segment
plots.noise()
pylab.savefig('%s_noise.png' % sensor_id)

# Quantum Efficiency
qe_file = dependency_glob('*%s_QE.fits' % sensor_id, jobname='qe')[0]
plots.qe(qe_file=qe_file)
pylab.savefig('%s_qe.png' % sensor_id)

# Crosstalk matrix
xtalk_file = dependency_glob('*%s_xtalk_matrix.fits' % sensor_id,
                             jobname='crosstalk')[0]
plots.crosstalk_matrix(xtalk_file=xtalk_file)
pylab.savefig('%s_xtalk.png' % sensor_id)

# Flat fields at wavelengths nearest the centers of the standard bands
wl_files = dependency_glob('*_lambda_*.fits', jobname='ts3_lambda')
plots.flat_fields(os.path.split(wl_files[0])[0])
pylab.savefig('%s_flat_fields.png' % sensor_id)

plots.latex_tables('%s_results_table.tex' % sensor_id)
