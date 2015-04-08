#!/usr/bin/env python
import glob
import lcatr.schema

qe_files = glob.glob('*QE.*')

results = [lcatr.schema.valid(lcatr.schema.get('qe'))]
results.extend([lcatr.schema.fileref.make(item) for item in qe_files])

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
