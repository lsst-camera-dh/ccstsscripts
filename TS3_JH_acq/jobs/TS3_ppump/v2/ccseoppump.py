###############################################################################
# ppump
#    script for doing pocket pumping acq
#
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

arcsub.synchCommand(10,"setConfigFromFile",acffile);
arcsub.synchCommand(20,"applyConfig");
arcsub.synchCommand(10,"powerOnCCD");

arcsub.synchCommand(10,"setParameter","Expo","1");
arcsub.synchCommand(10,"setParameter","Light","0");
arcsub.synchCommand(10,"applyParams");

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

wl     = float(eolib.getCfgVal(acqcfgfile, 'PPUMP_WL', default = "550.0"))
pcount = float(eolib.getCfgVal(acqcfgfile, 'PPUMP_BCOUNT', default = "25"))

#number of PLCs between readings
nplc = 1

arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

seq = 0  # image pair number in sequence
imcount = 2

monosub.synchCommand(10,"setFilter",5);

# go through config file looking for 'ppump' instructions, take the flats
print "Scanning config file for PPUMP specifications";
ccd = CCDID

print "Working on CCD %s" % ccd


fp = open(acqcfgfile,"r");
fpfiles = open("%s/acqfilelist" % cdir,"w");

for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'ppump')):

        wl      = float(tokens[1])
        exptime = float(tokens[2])
        nshifts  = float(tokens[3])

        print "starting acquisition step for lambda = %8.2f with exptime %8.2f s" % (wl, exptime)

        arcsub.synchCommand(10,"setParameter","Light","0");
        arcsub.synchCommand(10,"setParameter","Npump",nshifts);
        arcsub.synchCommand(10,"setParameter","Pdepth","1");
        monosub.synchCommand(30,"setWave",wl);

# pump with some darks then do a light exposure
# 2sec for the bias
        arcsub.synchCommand(10,"setParameter","ExpTime","2000"); 
        for i in range(pcount):
# start acquisition
            arcsub.synchCommand(45,"printControllerStatus");

            timestamp = time.time()
            fitsfilename = "%s_ppump_bias_%3.3d_${timestamp}.fits" % (ccd,seq)
            arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

            print "Ready to take image. time = %f" % time.time()
            result = arcsub.synchCommand(200,"exposeAcquireAndSave");
            fitsfilename = result.getResult();
            print "after click click at %f" % time.time()
            time.sleep(2.)

        arcsub.synchCommand(10,"setParameter","ExpTime",exptime);
        arcsub.synchCommand(10,"setParameter","Light","1");

        for i in range(imcount):

# prepare to readout diodes
            nreads = exptime*60/nplc + 200
            if (nreads > 3000):
                nreads = 3000
                nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

            pdsub.asynchCommand("accumBuffer",int(nreads),nplc,True);
            timestamp = time.time()

# make sure to get some readings before the state of the shutter changes       
            time.sleep(0.2);

# start acquisition
            arcsub.synchCommand(45,"printControllerStatus");

            fitsfilename = "%s_ppump_%3.3d_ppump%d_${timestamp}.fits" % (ccd,seq,i+1)
            arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

            print "Ready to take image. time = %f" % time.time()
            result = arcsub.synchCommand(200,"exposeAcquireAndSave");
            fitsfilename = result.getResult();
            print "after click click at %f" % time.time()

# make sure the sample of the photo diode is complete
            time.sleep(5.)

            print "done with exposure # %d" % i
            print "getting photodiode readings"

            pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i+1)
            pdsub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pdfilename));
            print "Finished getting readings at %f" % time.time()

            fpfiles.write("%s %s/%s %f\n" % (fitsfilename,cdir,pdfilename,timestamp))

        seq = seq + 1

fpfiles.close();
fp.close();

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

fp.close();

# move TS to idle state
                    
tssub.synchCommand(10,"setTSIdle");

print "PPUMP: END"
