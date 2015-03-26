#!/usr/bin/env python
import glob
import lcatr.schema

results_file = glob.glob('*_eotest_results.fits')[0]
det_resp_data = glob.glob('*_det_response.fits')[0]

results = [lcatr.schema.fileref.make(x) for x in (results_file, 
                                                  det_resp_data)]

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
