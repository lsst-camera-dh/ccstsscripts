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
lampsub = CCS.attachSubsystem("ts/Lamp");
monosub = CCS.attachSubsystem("ts/Monochromator");


# Initialization
print "doing initialization at %f" % time.time()

biassub.synchCommand(10,"reset")
pdsub.synchCommand(10,"reset")
time.sleep(2.)
biassub.synchCommand(10,"setcurrentrange",0.0002)
pdsub.synchCommand(10,"setcurrentrange",0.0002)

fp = open("/data1/Flux/flux-scan-with-filter-%f.dat" % time.time(),"w");

monosub.synchCommand(30,"setFilter",2);
ifilt = 2

#for wl in range(655,1210,5):
for wl in [480, 510, 650] :
#for wl in range(300,455,5):
    result = monosub.synchCommand(200,"setWave",wl);
    rply = result.getResult();
    time.sleep(0.5);
    if (wl<560. and ifilt!=2 ) :
        monosub.synchCommand(30,"setFilter",2);
        ifilt = 2
    if (wl>560. and ifilt!=3 ) :
        monosub.synchCommand(30,"setFilter",3);
        ifilt = 3
    print "getting wavelength at time %f" % time.time()
    result = monosub.synchCommand(20,"getWave");
    time.sleep(0.5);
    rwl = result.getResult()
    print "getting filter wheel setting"
    result = monosub.synchCommand(20,"getFilter");
    ifl = result.getResult()
    rng1 = range(6,1200,100)
    rng2 = range(1200,2000,20)
    fullrange = rng1+rng2
    for sw in fullrange :
        print "starting  step for lambda = %8.2f, slit width = %8.0f at time %f" % (wl,sw,time.time())
        print "setting slit size to %f at time %f" % (sw,time.time())
        result = monosub.synchCommand(20,"setSlitSize",1,sw);
        rply = result.getResult();

        print "Reading currents at time %f" % time.time()
        totpdcur = 0.
        npdcur = 0
        totbscur = 0.
        nbscur = 0

        try:
            result = pdsub.synchCommand(10,"accumBuffer",100,1,False);
            rply = result.getResult();
            result = pdsub.synchCommand(20,"readBuffer");
            readings=result.getResult();
#            print "readings = %s" % readings
#           vals = readings.split(" ")
#            print "vals[2] = %s" % vals[2].strip(",")
#            print ["%9.2e" % pdval for pdval in readings]
            for i in range(0,99) :
                totpdcur = totpdcur + readings[0][i]
                npdcur = npdcur + 1
        except Exception, ex:
            print "bad PD current read, error = %s" % ex
        except TypeError, ex:
            print "bad PD data returned from buffer read. Error = %s" % ex

        try:
            result = biassub.synchCommand(10,"accumBuffer",100,1,False);
            rply = result.getResult();
            result = biassub.synchCommand(20,"readBuffer");
            readings=result.getResult();
            print "reading (0,0) = %e" % readings[0][0]
            print "reading (1,0) = %e" % readings[1][0]
            print "reading (0,1) = %e" % readings[0][1]
            print "reading (1,1) = %e" % readings[1][1]
            print "reading (0,2) = %e" % readings[0][2]
            print "reading (1,2) = %e" % readings[1][2]
#            print ["%9.2e" % pdval for pdval in readings]
            for i in range(0,99) :
                totbscur = totbscur + readings[0][i]
                nbscur = nbscur + 1
        except Exception, ex:
            print "bad BIAS current read, error = %s" % ex
        except TypeError, ex:
            print "bad BIAS data returned from buffer read. Error = %s" % ex

        pdcurrent = 0.0
        if (npdcur>0) :
            pdcurrent = -totpdcur / npdcur
        print "PD Current = %s at time %f" % (pdcurrent,time.time())
        bscurrent = 0.0
        if (nbscur>0) :
            bscurrent = -totbscur / nbscur
        print "BIAS PD Current = %s" % bscurrent
        result = monosub.synchCommand(20,"getSlitSize",1);
        rsw = result.getResult()
        result = lampsub.synchCommand(20,"getLampCurrent");
        lcur = result.getResult()
        print "wavelength = %s, returned wl = %s, slitsize = %s, returned slitsize = %s, pdcurrent = %s, bscurrent = %s, lamp current = %s at time %f" % (wl,rwl,sw,rsw,pdcurrent,bscurrent,lcur,time.time())
        print "writing results"
        fp.write(`rwl`+" "+`rsw`+" "+`pdcurrent`+" "+`bscurrent`+" "+`ifl`+" "+`lcur`+"\n");
#        fp.write(`rwl`+" "+`rsw`+" "+`pdcurrent`+" "+`bscurrent`+" "+`ifilt`+" "+`lcur`+"\n");
        fp.flush()
        time.sleep(0.1);

fp.close();

print "wv-test: END"
