###############################################################################
# fe55
# Acquire fe55 image pairs
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

arcsub.synchCommand(10,"setConfigFromFile",acffile);
arcsub.synchCommand(20,"applyConfig");
arcsub.synchCommand(10,"powerOnCCD");

arcsub.synchCommand(10,"setParameter","Expo","1");
arcsub.synchCommand(10,"setParameter","Light","0");

monosub.synchCommand(10,"closeShutter");
monosub.synchCommand(10,"setFilter",1); // open position

# enable the Fe55 arm                                                                                                                                     
//????????

//result = arcsub.synchCommand(10,"clearCCD");

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

seq = 0  # image pair number in sequence

#number of PLCs between readings                                                                         
nplc = 1

ccd = CCDID

print "Working on CCD %s" % ccd


# go through config file looking for 'fe55' instructions, take the fe55s
arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));


print "Scanning config file for fe55 specifications";

fp = open(acqcfgfile,"r");
fpfiles = open("%s/acqfilelist" % cdir,"w");

for line in fp:
    tokens = str.split(line)
    if ((len(tokens) > 0) and (tokens[0] == 'fe55')):
        exptime  = float(tokens[1])
        imcount = int(tokens[2])

        result = arcsub.synchCommand(10,"setParameter","ExpTime",exptime);
        result = arcsub.synchCommand(30,"applyParams");

        for i in range(imcount):
# prepare to readout diodes                                                                              
            nreads = exptime*60/nplc + 200
            if (nreads > 3000):
                nreads = 3000
nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

            result = pdsub.asynchCommand("accumBuffer",int(nreads),nplc,True);

            timestamp = time.time()

# make sure to get some readings before the state of the shutter changes       
            time.sleep(0.2);

# start acquisition
            arcsub.synchCommand(45,"printControllerStatus");

            fitsfilename = "%s_fe55_%3.3d_fe55%d_${timestamp}.fits" % (ccd,seq,i+1)
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
            result = pdsub.synchCommand(500,"readBuffer","%s/%s" % (cdir,pdfilename));
            print "Finished getting readings at %f" % time.time()

            fpfiles.write("%s %s %f\n" % (fitsfilename,pdfilename,timestamp))

        seq = seq + 1

fpfiles.close();
fp.close();


# disable the Fe55 arm                                                                                                                                     
????????


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

print "FE55: END"
