#!/usr/bin/env python
import os
import sys
import subprocess
from lcatr.harness.helpers import dependency_glob

print "The documents received with the hardware will be searched for in the Desktop hardwareReceipt folder"

vendor_files = dependency_glob('*', jobname='Vendor-Data-Acceptance')
#vendor_files = dependency_glob('*', jobname='vendorIngest')

print "A window is now being opened showing the directory of vendor data\nreceived at registration time";
print " for you to check against the information received with the actual hardware.";
print "A list of the files will also appear here:";
print vendor_files
subprocess.Popen(["nautilus",os.path.dirname(vendor_files[0])]);
