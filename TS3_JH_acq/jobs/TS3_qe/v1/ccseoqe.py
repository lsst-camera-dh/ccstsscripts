###############################################################################
# qe
# Acquire qe images
#
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys

sys.path.append(tsCWD);
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

lo_lim = float(eolib.getCfgVal(acqcfgfile, 'LAMBDA_LOLIM', default='1.0'))
hi_lim = float(eolib.getCfgVal(acqcfgfile, 'LAMBDA_HILIM', default='120.0'))
bcount = int(eolib.getCfgVal(acqcfgfile, 'LAMBDA_BCOUNT', default='1'))
imcount = int(eolib.getCfgVal(acqcfgfile, 'LAMBDA_IMCOUNT', default='1'))

serno = 1   # in the future this will be passed in
imcount = 2         

#number of PLCs between readings                                                  nplc = 1

result = arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

result = monosub.synchCommand(10,"setFilter",5); // open position

# go through config file looking for 'qe' instructions, take the qes
print "Scanning config file for LAMBDA specifications";
fp = open(acqcfgfile,"r");
fpfiles = open("%s/acqfilelist" % cdir,"w");

for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'lambda')):
        wl = int(tokens[1])
        target = float(tokens[1])
        print "target wl = %f" % target;

        exptime = eolib.expCheck(calfile, lab, target, wl, hi_lim, lo_lim, test='LAMBDA', use_nd=False)

        result = arcsub.synchCommand(10,"setParameter","ExpTime",exptime);

# take bias images
        result = arcsub.synchCommand(10,"setParameter","Light","0");
        result = arcsub.synchCommand(10,"applyParams");
        for i in range(bcount):
            timestamp = time.time()
            fitsfilename = "ArchonImage_Bias_%d-for-seq-%d-exp-%d.fits" % (int(timestamp),seq,i)
            result = arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

            print "Ready to take image. time = %f" % time.time()
            result = arcsub.synchCommand(200,"exposeAcquireAndSave");
            print "after click click at %f" % time.time()


# take light exposures
        result = arcsub.synchCommand(10,"setParameter","Light","1");
        result = arcsub.synchCommand(10,"applyParams");
        for i in range(imcount):
            print "starting acquisition step for lambda = %8.2f" % wl

            result = monosub.synchCommand(30,"setWave",wl);

# prepare to readout diodes                                                                              
            nreads = exptime*60/nplc + 200
            if (nreads > 3000):
                nreads = 3000
                nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

            result = pdsub.asynchCommand("accumBuffer",int(nreads),nplc,True);

# start acquisition                                                                                      
            result = arcsub.synchCommand(45,"printControllerStatus");

            timestamp = time.time()
            fitsfilename = "ArchonImage_%d-for-seq-%d-exp-%d.fits" % (int(timestamp),seq,i)
            result = arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

            print "Ready to take image. time = %f" % time.time()
            result = arcsub.synchCommand(200,"exposeAcquireAndSave");
            print "after click click at %f" % time.time()

# make sure the sample of the photo diode is complete                                                    
            time.sleep(10.)

            print "done with exposure # %d" % i
            print "getting photodiode readings"

            pdfilename = "pd-values_%d-for-seq-%d-exp-%d" % (timestamp,seq,i)
            result = pdsub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pdfilename));
            print "Finished getting readings at %f" % time.time()

            fpfiles.write("%s %s %f\n" % (fitsfilename,pdfilename,timestamp))

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

#result = tssub.synchCommandLine(10,"printFullState");
#print result.getResult();
fp.close();

# move TS to idle state
                    
tssub.synchCommand(10,"setTSIdle");

print "QE: END"
