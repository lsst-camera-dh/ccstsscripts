###############################################################################
# fluxcal
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time

sys.path.append(libdir);
import eolib

CCS.setThrowExceptions(False);

#attach CCS subsystem Devices for scripting
print "Attaching teststand subsystems"
tssub  = CCS.attachSubsystem("ts");
biassub = CCS.attachSubsystem("ts/Bias");
pdsub   = CCS.attachSubsystem("ts/PhotoDiode");
cryosub = CCS.attachSubsystem("ts/Cryo");
vacsub  = CCS.attachSubsystem("ts/VacuumGauge");
lampsub = CCS.attachSubsystem("ts/Lamp");
monosub = CCS.attachSubsystem("ts/Monochromator");
    
print "Attaching archon subsystem"
arcsub  = CCS.attachSubsystem("archon");

serno = 1   # in the future this will be passed in

cdir = tsCWD

# Initialization
print "doing initialization"

result = arcsub.synchCommand(10,"setConfigFromFile",acffile);
result = arcsub.synchCommand(20,"applyConfig");
result = arcsub.synchCommand(10,"powerOnCCD");

result = arcsub.synchCommand(10,"setParameter","Expo","1");
result = arcsub.synchCommand(10,"setParameter","Light","1");
result = arcsub.synchCommand(10,"applyParams");

# move to TS acquisition state
print "setting acquisition state"
tssub.synchCommand(10,"settstest");

#check state of ts devices
print "wait for ts state to become ready";
tsstate = 0
starttim = time.time()
while True:
    print "checking";
    result = tssub.synchCommand(10,"istsready");
    tsstate = result.getResult();
# the following line is just for test situations so that there would be no waiting
    tsstate=1;
    if ((time.time()-starttim)>240):
        print "Something is wrong ... we will never make it to a runnable state"
        exit
    if tsstate!=0 :
        break
#put in acquisition state
tssub.synchCommand(120,"goteststand");

targflux = float(eolib.getCfgVal(acqcfgfile, 'FLUXCAL_TARGET', default='5000'))
exp_hilim = float(eolib.getCfgVal(acqcfgfile, 'FLUXCAL_HILIM', default='60'))
exp_lolim = float(eolib.getCfgVal(acqcfgfile, 'FLUXCAL_LOLIM', default='2.0'))

print("FLUXCAL: START")
print("FLUXCAL: Calibration directory : %s" % fluxcaldir)

# find the most recent calibration file and use that as source               
files = sorted(glob.glob(fluxcaldir+'/fluxcal*.txt'))
if (len(files) != 0):
    print "Number of fluxcal files =", len(files)
    lastcal = files[len(files)-1]
else:
    lastcal = 'None'

print("FLUXCAL: Last calibration file = %s" % lastcal)

# create a new calibration file and copy header into it                                                                                                   
newfile = fluxcaldir+"/fluxcal_"+eolib.tstamp()+".txt"

f = open(newfile, 'w')
f.write("######################################################################\n")
f.write("# Flux calibration file: %s\n" % os.path.split(newfile)[1])
f.write("# Date: %s\n" % time.strftime("%Y%m%d"))
f.write("# Time: %s\n" % time.strftime("%H:%M:%S"))
f.write("# Target flux = %8.2f\n" % targflux)
f.write("# System Gain = %8.2f e-/DN\n" % gain)
f.write("# Exposure Limits = %8.2f   %8.2f\n" % (exp_lolim, exp_hilim))
f.write("# Lamp Manufacturer = %s\n" % lab['lamp'].getInfo()[0])
f.write("# Lamp Model = %s\n" % lab['lamp'].getInfo()[1])
f.write("# Lamp bulb hours = %s\n" % lab['lamp'].getHours())
f.write("# Last calibration file: %s\n" % os.path.split(lastcal)[1])
f.write("######################################################################\n")
f.close()
fname = "fluxcal_bias"
fname = camera.bias_acq(fname, path=datadir, test='FLUXCAL', img='BIAS')
result = arcsub.synchCommand(10,"setFitsFilename",fname);
result = arcsub.synchCommand(200,"exposeAcquireAndSave");
result = arcsub.synchCommand(10,"getImageAverageSignal");
bias = result.getResult();
#bias = ht.fitsAverage(fname)  # in DN                                                                                                                     
if ((lastcal == 'None') or (new == True)):
    f = open(newfile, 'a')
    f.write("{:<10}{:^4}{:^12}".format('command','wl','flux'))
    f.write("{:^12}{:^7}\n".format('signal','exptime'))
    f.write("{:<10}{:>4}{:>12}".format('-------','----','----------'))
    f.write("{:>12}{:>9}\n".format('----------','-------'))
    f.close()
    wl = 320
    while (wl <= 1100):
        result = monosub.synchCommand(30,"setWave",wl);
        
        exptime = 2.0
        fname = "fluxcal_%04d" % wl
#       fname = camera.exp_acq(fname, exptime, path=datadir, test='FLUXCAL', img='FLAT')
        result = arcsub.synchCommand(10,"setFitsFilename",fname);
        result = arcsub.synchCommand(200,"exposeAcquireAndSave");

        result = arcsub.synchCommand(10,"getImageAverageSignal");
        avg = result.getResult();
#        avg = ht.fitsAverage(fname)      # in DN                                                                                                          
        signal = (avg-bias)*gain         # in electrons                                                                                                   
        flux = max(signal/exptime, 1.0)  # in electrons/second (can't be < 0 !)                                                                           
        f = open(newfile, 'a')
        f.write("{:<10}{:>4d}{:>12.2f}{:>12.2f}{:>9.2f}\n".format('fluxcal',wl,flux,signal,exptime))
        f.close()
        wl = wl + 5
else:
    f = open(newfile, 'a')
    f.write("{:<10}{:^4}{:^12}{:^12}".format('command','wl','flux','signal'))
    f.write("{:^9}{:^12}{:>10}\n".format('exptime','previous','% change'))
    f.write("{:<10}{:^4}{:>12}{:>12}".format('-------','----','----------','----------'))
    f.write("{:>9}{:>12}{:>10}\n".format('-------','----------','--------'))
    f.close()
    with open(lastcal) as fp:
        for line in fp:
            tokens = str.split(line)
            if ((len(tokens) > 0) and (tokens[0] == 'fluxcal')):
                wl = int(tokens[1])
                oldflux = max (float(tokens[2]), 1) # better not be zero or negative                   
                
                result = monosub.synchCommand(30,"setWave",wl);
                
                exptime = min(max(float(targflux)/oldflux, exp_lolim), exp_hilim)
                fname = "fluxcal_%04d" % wl
#                 fname = camera.exp_acq(fname, exptime, path=datadir, test='FLUXCAL', img='FLAT')
                result = arcsub.synchCommand(10,"setFitsFilename",fname);
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                result = arcsub.synchCommand(10,"getImageAverageSignal");
                avg = result.getResult();
#                avg = ht.fitsAverage(fname)      # in DN                                                                                                  
                signal = (avg-bias)*gain         # in electrons                                                                                           
                flux = signal/exptime            # in electrons/second                                                                                    
                if (flux <= 0.0):
                    flux = oldflux    # that's ridiculous, use the old value                                                                              
                change = ((flux-oldflux)/oldflux) * 100   # percent change since last time                                                                
                # write the result into the calibration file                                                                         f = open(newfile, 'a')
                f.write("{:<10}{:>4}{:>12.2f}{:>12.2f}".format('fluxcal',wl,flux,signal))
                f.write("{:>9.2f}{:>12.2f}{:>10.2f}\n".format(exptime,oldflux,change))
                f.close()



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

#result = tssub.synchCommandLine(10,"printFullState");
#print result.getResult();
fp.close();

# move TS to idle state
                    
tssub.synchCommand(10,"setTSIdle");

print "FLUXCAL: END"
