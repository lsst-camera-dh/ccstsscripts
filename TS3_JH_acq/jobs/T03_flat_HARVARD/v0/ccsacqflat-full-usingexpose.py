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

CCS.setThrowExceptions(False);

#attach CCS subsystem Devices for scripting
print "Attaching teststand subsystems"
tssub  = CCS.attachSubsystem("ts");
biassub = CCS.attachSubsystem("ts/Bias");
pdsub = CCS.attachSubsystem("ts/PhotoDiode");
cryosub = CCS.attachSubsystem("ts/Cryo");
vacsub  = CCS.attachSubsystem("ts/VacuumGauge");
lampsub = CCS.attachSubsystem("ts/Lamp");
monosub = CCS.attachSubsystem("ts/Monochromator");
    
print "Attaching archon subsystem"
arcsub  = CCS.attachSubsystem("archon");

serno = 1   # in the future this will be passed in
imcount = 2         

cdir = "/opt/ccs/lcatr/share/T03_flat_HARVARD/v0/";

# Initialization
print "doing initialization"
#result = arcsub.synchCommand(10,"setConfigFromFile","/opt/ccs/scripts/archon-harvard2.acf");
#result = arcsub.synchCommand(20,"applyConfig");

#result = arcsub.synchCommand(10,"setParameter","Expo","1");
#result = arcsub.synchCommand(10,"setParameter","Light","1");
#result = arcsub.synchCommand(10,"applyParams");

# move to TS acquisition state
print "setting acquisition state"
tssub.synchCommand(10,"settstest");

# turn lamp on
result = lampsub.synchCommand(10,"setlamppowerenable",1);

#check state of ts devices
print "wait for ts state to become ready";
tsstate = 0
while True:
    print "checking";
    result = tssub.synchCommand(10,"istsready");
    tsstate = result.getResult();
#    tsstate=1;
    if tsstate!=0 :
        break
#put in acquisition state
tssub.synchCommand(120,"goteststand");

wl = 550.0; # default wl

# go through config file looking for 'flat' instructions, take the flats
seq = 0  # image pair number in sequence

print "Scanning config file for FLAT specifications";
fp = open("/opt/ccs/scripts/HARVARD.cfg","r");
for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'flat')):
        target = float(tokens[1])
        print "target wl = ";
        print target;
        exptime = 100;
#        exptime = eolib.expCheck(lab, target, wl, hi_lim, lo_lim, test='FLAT', use_nd=False)
        wl = target;

#        result = arcsub.synchCommand(10,"setParameter","ExpTime",exptime);

#        avg = ht.fitsAverage(fname)
#        print "DATA : Average signal = %8.2f DN" % (avg - bias);
        seq = seq + 1     

        print "image pair number is %d" % seq

        for i in range(imcount):
            print "starting acquisition step for lambda = %8.2f" % wl
            result = monosub.synchCommand(10,"setWave",wl);
#...            result = arcsub.synchCommand(20,"setParameter","ACQ","1");
#...            result = arcsub.synchCommand(30,"applyParams");

# prepare to readout diodes
            result = pdsub.synchCommand(10,"accumBuffer",20,10);
# start acquisition
            print "starting acquisition"
#            result = arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));
#            result = arcsub.synchCommand(120,"exposeAcquireAndSave");
            print "done with exposure # %d" % i
            print "getting photodiode readings"
            result = pdsub.synchCommand(120,"readBuffer");
            readings=result.getResult();
            print "photo diode readings = "
            print ["%0.2f" % i for i in readings]
fp.close();

#   avg = ht.fitsAverage(fname)
#   print "DATA : Average signal = %8.2f DN" % (avg - bias)

fp = open("%s/status.out" % (cdir),"w");

istate=0;
result = tssub.synchCommandLine(10,"getstate");
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

result = tssub.synchCommandLine(10,"printFullState");
print result.getResult();
fp.close();

# move TS to idle state
                    
tssub.synchCommand(10,"setTSIdle");

print "FLAT: END"
