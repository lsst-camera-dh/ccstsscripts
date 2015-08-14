###############################################################################
#  Flux scan script script
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time

sys.path.append(tsCWD);

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
#monosub.synchCommand(10,"setHandshake",0);

print "Attaching archon subsystem"
#arcsub  = CCS.attachSubsystem("archon");

filter = 1

#cdir = tsCWD

# Initialization
print "doing initialization at %f" % time.time()

biassub.synchCommand(10,"setcurrentrange",0.0002)

fp = open("/data1/Flux/flux-scan-with-filter%d.dat" % filter,"w");

monosub.synchCommand(30,"setFilter",2);
ifilt = 2

for wl in range(300,1210,5):
    if (wl<560. and ifilt!=2 ) :
        monosub.synchCommand(30,"setFilter",2);
        ifilt = 2
    if (wl>560. and ifilt!=3 ) :
        monosub.synchCommand(30,"setFilter",3);
        ifilt = 3
    for sw in range(6,30,10):
        print "starting  step for lambda = %8.2f, slit width = %8.0f" % (wl,sw)
        result = monosub.synchCommand(200,"setWave",wl);
        rply = result.getResult();
        time.sleep(0.1);
        print "setting slit size to %f" % sw
        result = monosub.synchCommand(200,"setSlitSize",1,sw);
        rply = result.getResult();
#    result = biassub.synchCommand(10,"readcurrent");
        print "Reading PD current"
        result = pdsub.synchCommand(200,"readCurrent");
        pdcurrent = result.getResult()
        print "PD Current = %s" % pdcurrent
        pdcurrent = pdcurrent * -1.0
        print "Reading BIAS PD current"
        result = biassub.synchCommand(200,"readCurrent");
        bscurrent = result.getResult()
        print "BIAS PD Current = %s" % bscurrent
        bscurrent = bscurrent * -1.0
        print "getting wavelength"
        result = monosub.synchCommand(200,"getWave");
        rwl = result.getResult()
        print "getting filter wheel setting"
        result = monosub.synchCommand(200,"getFilter");
        ifl = result.getResult()
        time.sleep(0.1);
        result = monosub.synchCommand(200,"getSlitSize",1);
        rsw = result.getResult()
        print "wavelength = %s, returned wl = %s, slitsize = %s, returned slitsize = %s, pdcurrent = %s, bscurrent = %s" % (wl,rwl,sw,rsw,pdcurrent,bscurrent)
        print "writing results"
        fp.write(`rwl`+" "+`rsw`+" "+`pdcurrent`+" "+`bscurrent`+" "+`ifl`+"\n");
        fp.flush()
        time.sleep(0.1);

fp.close();

print "wv-test: END"
