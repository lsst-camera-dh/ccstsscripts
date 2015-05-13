#!/usr/bin/env python
import glob
import lcatr.schema

ptc_results = glob.glob('*_ptc.fits')[0]

results = [lcatr.schema.fileref.make(ptc_results)]

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
