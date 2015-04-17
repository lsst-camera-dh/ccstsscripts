#!/usr/bin/env python
import os
import sys
import subprocess
from lcatr.harness.helpers import dependency_glob

#print "The documents will be searched for in /tmp/scan/"

vendor_files = dependency_glob('*', jobname='Vendor-Data-Acceptance')

print vendor_files
subprocess.Popen(["nautilus",os.path.dirname(vendor_files[0])]);
