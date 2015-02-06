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

cdir = "/home/homer/lsst/lcatr/TS3_JH_analysis/jobs/bnl_flat_acq3/v0";

# Initialization
#check state of ts3 devices
print "Retrieving ts3 state";
try:
    result = ts3sub.synchCommand(10,"ists3ready");
except ScriptingTimeoutException, timeout:
    print 'Timeout Exception', timeout
except Exception, execution:
    print 'Execution Exception', execution
else:
    ts3state = result.getResult();
    print "Execution Successful",ts3state;
    if (ts3state==1):
        print "ts3 devices ready for acquisition";
    else:
        print "Please check ts3 devices monitoring. Aborting acquisition!";
        exit(0);

#check lamp current
print "Getting the lamp current";
try:
    result = lampsub.synchCommand(10,"readlampcurrent");
except ScriptingTimeoutException, timeout:
    print 'Timeout Exception', timeout
except Exception, execution:
    print 'Execution Exception', execution
else:
    lampcurrent = result.getResult();
    print "Execution Successful. Lamp current =",lampcurrent;
# the following will become configuration parameters
    MINCUR = 0.0;
    MAXCUR = 0.002;
    if (lampcurrent>MINCUR and lampcurrent<MAXCUR):
        print "lamp ready";
    else:
        print "lamp not ready .... aborting!";
#        exit(0);

#ramp bias voltage to -70V
#set the source output ON
try:
    result = biassub.synchCommandLine(10,"setoutput 1");
except ScriptingTimeoutException, timeout:
    print 'Timeout Exception', timeout
except Exception, execution:
    print 'Execution Exception', execution
else:
    print "Execution Successful";

#ramp the voltage to operating value
try:
    result = biassub.synchCommand(10,"rampvolts",5.0,-70.);
except ScriptingTimeoutException, timeout:
    print 'Timeout Exception', timeout
except Exception, execution:
    print 'Execution Exception', execution
else:
    print "Execution Successful";

#verify voltage
try:
    result = biassub.synchCommand(10,"readvoltage");
except ScriptingTimeoutException, timeout:
    print 'Timeout Exception', timeout
except Exception, execution:
    print 'Execution Exception', execution
else:
    biasvolts = result.getResult();
    print "voltage read gives V=",biasvolts,"V";


# Acquisition

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
fp = open("%s/BNL.cfg" % (cdir) ,"r");
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
fp = open("%s/BNL.cfg" % (cdir),"r");
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
                result = arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));
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

fp = open("%s/status.out" % (cdir),"w");

istate=0;
result = ts3sub.synchCommandLine(10,"getState");
istate=result.getResult();
fp.write(`istate`+"\n");
result = biassub.synchCommand(10,"readvoltage");
volts=result.getResult();
fp.write(`volts`+"\n");
result = biassub.synchCommand(10,"readcurrent");
curr=result.getResult();
fp.write(`curr`+"\n");
result = vacsub.synchCommand(10,"readpressure");
vac=result.getResult();
fp.write(`vac`+"\n");
result = cryosub.synchCommand(10,"getTemp","A");
temp=result.getResult();
fp.write(`temp`+"\n");

result = ts3sub.synchCommandLine(10,"printFullState");
print result.getResult();
fp.close();

# restore to idle state
#ramp bias voltage to 0V
#ramp the voltage to operating value
try:
    result = biassub.synchCommand(10,"rampvolts",5.0,0.);
except ScriptingTimeoutException, timeout:
    print 'Timeout Exception', timeout
except Exception, execution:
    print 'Execution Exception', execution
else:
    print "Execution Successful";


#set the source output OFF
try:
    result = biassub.synchCommandLine(10,"setoutput 0");
except ScriptingTimeoutException, timeout:
    print 'Timeout Exception', timeout
except Exception, execution:
    print 'Execution Exception', execution
else:
    print "Execution Successful";

print "FLAT: END"
