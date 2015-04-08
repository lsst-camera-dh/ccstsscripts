#!/usr/bin/env python
import glob
import pyfits
import lsst.eotest.image_utils as imutils
import lcatr.schema

eotest_results = glob.glob('*eotest_results.fits')[0]

bp_mask_file = glob.glob('*bright_pixel_mask.fits')[0]
bp_mask = pyfits.open(bp_mask_file)
results = []
for amp in imutils.allAmps:
    results.append(lcatr.schema.valid(lcatr.schema.get('bright_pixels'),
                                      amp=amp,
                                      bright_pixels=bp_mask[amp].header['NBRTPIX'],
                                      bright_columns=bp_mask[amp].header['NBRTCOL']))

results.append(lcatr.schema.fileref.make(bp_mask_file))
results.append(lcatr.schema.fileref.make(eotest_results))

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
