 ###############################################################################
# flat
# Acquire flat image pairs for linearity and gain measurement.
# For each 'flat' command a pair of flat field images are acquired
#
# In the configuration file the format for a flat command is
# flat   signal  
# where signal is the desired acquired signal level in e-/pixel
#
# FLAT_WL is used to determine what wavelength will be used for illumination
#
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception

CCS.setThrowExceptions(True);

#attach CCS subsystem Devices for scripting
ts3sub  = CCS.attachSubsystem("ts3");
biassub = CCS.attachSubsystem("ts3/Bias");
cryosub = CCS.attachSubsystem("ts3/Cryo");
vacsub  = CCS.attachSubsystem("ts3/VacuumGauge");
lampsub = CCS.attachSubsystem("ts3/Lamp");
monosub = CCS.attachSubsystem("ts3/Monochromator");
    
arcsub  = CCS.attachSubsystem("archon");

serno = 1   # in the future this will be passed in
imcount = 2         

#    try:
#        result = ts3sub.synchCommandLine(10,"get lolim");
#        lo_lim=result.getResult();
#        result = ts3sub.synchCommandLine(10,"get hilim");
#        hi_lim=result.getResult();
#        result = ts3sub.synchCommandLine(10,"get bcount");
#        bcount=result.getResult();
wl = 550.0; # default wl
# the following will be generalized and become a global function
#with open(lab['config']) as fp:
#with open("config") as fp:
fp = open("/home/homer/lsst/lcatr/TS3_JH_analysis/jobs/flat_acq/v0/BNL.cfg","r");
for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'FLAT_WL')):
        target = float(tokens[1])
        wl = float(tokens[1])
        print "wavelength for flats = ";
        print wl;
fp.close();

# go through config file looking for 'flat' instructions, take the flats
seq = 0  # image pair number in sequence
#with open(lab['config']) as fp:
print "Scanning config file for FLAT specifications";
fp = open("/home/homer/lsst/lcatr/TS3_JH_analysis/jobs/flat_acq/v0/BNL.cfg","r");
for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'flat')):
        target = float(tokens[1])
        print "target wl = ";
        print target;
#                    exptime = eolib.expCheck(lab, target, wl, hi_lim, lo_lim, 
#                                             test='FLAT', use_nd=False)
                    
#                avg = ht.fitsAverage(fname)
#                print "DATA : Average signal = %8.2f DN" % (avg - bias);
        seq = seq + 1     


        for i in range(imcount):
            try:
                result = monosub.synchCommand(10,"setWave",wl);
                result = arcsub.synchCommand(40,"acquireAndSaveImage");
            except ScriptingTimeoutException, timeout:
                print 'Timeout Exception', timeout
            except Exception, execution:
                print 'Execution Exception', execution
#            else:
#                if (imcount == 1):
#                    os.mv("archonimg-10000.raw", "%s_flat_%06u_flat1" % (serno, target))
#                else:
#                    os.mv("archonimg-10000.raw", "%s_flat_%06u_flat1" %(serno, int(wl), i) )
fp.close();

#   avg = ht.fitsAverage(fname)
#   print "DATA : Average signal = %8.2f DN" % (avg - bias)

fp = open("/home/homer/lsst/lcatr/TS3_JH_analysis/jobs/flat_acq/v0/status.out","w");

istate=0;
result = ts3sub.synchCommandLine(10,"getState");
istate=result.getResult();
fp.write(`istate`+"\n");
result = ts3sub.synchCommandLine(10,"printFullState");
print result.getResult();
fp.close();

print "FLAT: END"
