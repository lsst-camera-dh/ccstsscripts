#!/usr/bin/env python
import os
import sys
import subprocess
#from lcatr.harness.helpers import dependency_glob

print "The documents received with the hardware will be searched for in the Desktop hardwareReceipt folder"

#vendor_files = dependency_glob('*', jobname='Vendor-Data-Acceptance')
#vendor_files = dependency_glob('*', jobname='vendorIngest')
ccd = os.environ["LCATR_UNIT_ID"]
loc = "/nfs/farm/g/lsst/u1/jobHarness/jh_archive/CCD/%s/vendorIngest/v0/" % ccd
#lasttaskid = os.system("ssh -i ~/.ssh/id_vendor_data homer@rhel6-64.slac.stanford.edu ls -1 %s | tail -1" % loc)
rvndr = os.getenv("remote_vendor_acct")
os.system("ssh -i ~/.ssh/id_vendor_data %s ls -1 %s | tail -1 | xargs -n 1 --replace=ARG scp -rp -i ~/.ssh/id_vendor_data %s:%sARG/vendorData ." % (rvndr,loc,rvndr,loc))


print "A window is now being opened showing the directory of vendor data\nreceived at registration time";
print " for you to check against the information received with the actual hardware.";
print "A list of the files will also appear here:";
#print vendor_files
#subprocess.Popen(["nautilus",os.path.dirname(vendor_files[0])]);
subprocess.Popen(["nautilus","vendorData","/home/HardwareReceipt/Desktop/hardwareReceipt"]);
