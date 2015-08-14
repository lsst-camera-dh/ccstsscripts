###############################################################################
# ready_acq
# test the test stand for readiness
#
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys 
import time
import eolib
import pyfits as pf

CCS.setThrowExceptions(True);

try:
#attach CCS subsystem Devices for scripting
    print "Attaching teststand subsystems"
    tssub  = CCS.attachSubsystem("%s" % ts);
    print "attaching Bias subsystem"
    biassub = CCS.attachSubsystem("%s/Bias" % ts);
    print "attaching PD subsystem"
    pdsub   = CCS.attachSubsystem("%s/PhotoDiode" % ts);
    print "attaching Mono subsystem"
    monosub = CCS.attachSubsystem("%s/Monochromator" % ts );
    print "attaching PDU subsystem"
    pdusub = CCS.attachSubsystem("%s/PDU" % ts );
    print "Attaching archon subsystem"
    arcsub  = CCS.attachSubsystem("%s" % archon);

    time.sleep(3.)

    cdir = tsCWD

# Initialization

    print "resetting the Photo Diode device to make sure it is in a good state"
    result = pdsub.synchCommand(20,"reset")
    reply = result.getResult();
    time.sleep(5.)

    print "Loading configuration file into the Archon controller"
    result = arcsub.synchCommand(20,"setConfigFromFile",acffile);
    reply = result.getResult();
    print "Applying configuration"
    result = arcsub.synchCommand(25,"applyConfig");
    reply = result.getResult();
    print "Powering on the CCD"
    result = arcsub.synchCommand(30,"powerOnCCD");
    reply = result.getResult();
    time.sleep(3.);
#    arcsub.synchCommand(10,"setAcqParam","Nexpo");
    arcsub.synchCommand(10,"setParameter","Expo","1");

# the first image is usually bad so throw it away
    print "Throwing away the first image"
    arcsub.synchCommand(10,"setFitsFilename","");
    result = arcsub.synchCommand(200,"exposeAcquireAndSave");
    reply = result.getResult();

    print "Setting the current ranges on the Bias and PD devices"
    biassub.synchCommand(10,"setCurrentRange",0.0002)
    pdsub.synchCommand(10,"setCurrentRange",0.000002)

# move to TS acquisition state
    print "setting acquisition state"
    result = tssub.synchCommand(60,"setTSTEST");
    rply = result.getResult();

#check state of ts devices
    print "wait for ts state to become ready";
    tsstate = 0
    starttim = time.time()
    while True:
        print "checking for test stand to be ready for acq";
        result = tssub.synchCommand(10,"isTestStandReady");
        tsstate = result.getResult();
# the following line is just for test situations so that there would be no waiting
        tsstate=1;
        if ((time.time()-starttim)>240):
            print "Something is wrong ... we will never make it to a runnable state"
            exit
        if tsstate!=0 :
            break
        time.sleep(5.)

#put in acquisition state
    print "Since this is just a readiness check, we will NOT ramp the bias "
    result = tssub.synchCommand(120,"goTestStand");
    rply = result.getResult();

# get the glowing vacuum gauge off
    result = pdusub.synchCommand(120,"setOutletState",vac_outlet,False);
    rply = result.getResult();

    lo_lim = float(eolib.getCfgVal(acqcfgfile, 'LAMBDA_LOLIM', default='1.0'))
    hi_lim = float(eolib.getCfgVal(acqcfgfile, 'LAMBDA_HILIM', default='120.0'))
    bcount = int(eolib.getCfgVal(acqcfgfile, 'LAMBDA_BCOUNT', default='1'))
    imcount = int(eolib.getCfgVal(acqcfgfile, 'LAMBDA_IMCOUNT', default='1'))

    seq = 0

#number of PLCs between readings
    nplc = 1

    ccd = CCDID
    print "Working on CCD %s" % ccd

    print "set filter position"
    monosub.synchCommand(30,"setFilter",1); # open position

    flux1 = array("f")
    flux2 = array("f")
    iwl = 0
    wl1 = 0.
    wl2 = 0.
    arcsub.synchCommand(10,"setParameter","ExpTime","2000");

    for wl in [450., 823.] :
        monosub.synchCommand(30,"setWave",wl);
        
        arcsub.synchCommand(10,"setFitsFilename","");
        result = arcsub.synchCommand(200,"exposeAcquireAndSave");
        rply = result.getResult();
        arcsub.synchCommand(10,"setFitsFilename","fluxcalimage-${TIMESTAMP}-%f" % wl);
        result = arcsub.synchCommand(200,"exposeAcquireAndSave");
        fitsfilename = result.getResult();

        hdulist = pf.open(fitsfilename)
        hdr=hdulist[segment].header
        prim = hdulist[0].header
        gain = float(pruim['CCDGAIN'])
        for i in range(16):
            hdr=hdulist[i+1].header
            avg = float(hdr['AVWOBIAS'])
            bias = float(hdr['AVGBIAS'])
            signal = (avg-bias)*gain         # in electrons
            flux = max(signal/exptime, 1.0)  # in electrons/second (can't be < 0 !)
            if (iwl==0) :
                flux1.append(flux)
                wl1 = wl
            if (iwl==1) :
                flux2.append(flux)
                wl2 = wl
        iwl = iwl + 1
    for i in range(16) :
        print "segment %d, wl1 = %f, flux1 = %f, wl2 = %f, flux2 = %f" % (i,wl1,flux1[i],wl2,flux2[i])

#        Result = arcsub.synchCommand(10,"getImageAverageSignal");
#        avg = result.getResult();
#        avg = ht.fitsAverage(fname)      # in DN


# go through config file looking for 'qe' instructions
    print "Scanning config file for LAMBDA specifications";
    fp = open(acqcfgfile,"r");
    fpfiles = open("%s/acqfilelist" % cdir,"w");

    print "Scan at a low and a high wavelength to test monochromator and filter wheel"
    for wl in [450.,823.] :

            target = float(wl)
            print "target wl = %f" % target;

            exptime = eolib.expCheck(calfile, labname, target, wl, hi_lim, lo_lim, test='LAMBDA', use_nd=False)
            exptime = 10.

# take bias images

            arcsub.synchCommand(10,"setParameter","ExpTime","0"); 
            arcsub.synchCommand(10,"setParameter","Light","0");

            print "setting location of bias fits directory"
            arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

            result = arcsub.synchCommand(10,"setHeader","TestType","PREFLIGHT")
            result = arcsub.synchCommand(10,"setHeader","ImageType","BIAS")
            for i in range(bcount):
                timestamp = time.time()
                fitsfilename = "%s_lambda_bias_%3.3d_${TIMESTAMP}.fits" % (ccd,seq)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

                print "Ready to take bias image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()
                time.sleep(0.2)


# take light exposures
            arcsub.synchCommand(10,"setParameter","Light","1");
            arcsub.synchCommand(10,"setParameter","ExpTime",str(int(exptime*1000)));
            print "setting location of fits exposure directory"
            arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

# prepare to readout diodes
            nreads = exptime*60/nplc + 200
            if (nreads > 3000):
                nreads = 3000
                nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

            result = arcsub.synchCommand(10,"setHeader","TestType","PREFLIGHT")
            result = arcsub.synchCommand(10,"setHeader","ImageType","PREFLIGHT")

            print "Throwing away the first image"
            arcsub.synchCommand(10,"setFitsFilename","");
            result = arcsub.synchCommand(200,"exposeAcquireAndSave");
            reply = result.getResult();

# adjust timeout because we will be waiting for the data to become ready
            mywait = nplc/60.*nreads*1.10 ;
            print "Setting timeout to %f s" % mywait
            pdsub.synchCommand(1000,"setTimeout",mywait);

            for i in range(imcount):
                print "starting acquisition step for lambda = %8.2f" % wl

                print "Setting the monochrmator wavelength and filter"
                print "You should HEAR some movement"
                result = monosub.synchCommand(30,"setWaveAndFilter",wl);
                rply = result.getResult()
                time.sleep(4.)
                print "Verifying wavelength setting of the monochromator"
                result = monosub.synchCommand(30,"getWave");
                rwl = result.getResult()
                print "publishing state"
                result = tssub.synchCommand(60,"publishState");

                print "getting filter wheel setting"
                result = monosub.synchCommand(60,"getFilter");
                ifl = result.getResult()
                print "The wavelength is at %f and the filter wheel is at %f " % (rwl,ifl)
                time.sleep(4.);
                


                print "Starting Photo Diode recording at %f" % time.time()
                print "You should see digits changing on the PD device"
                pdresult =  pdsub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);

                print "recording should now be in progress and the time is %f" % time.time()

# start acquisition
                timestamp = time.time()
                fitsfilename = "%s_lambda_%3.3d_%3.3d_lambda_%d_${TIMESTAMP}.fits" % (ccd,int(wl),seq,i+1)
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);

# make sure to get some readings before the state of the shutter changes       
                time.sleep(0.2);
 

                print "Taking an image now. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "Done taking image at %f" % time.time()

                print "done with exposure # %d" % i
                print "retrieving photodiode readings at time = %f" % time.time();

                pdfilename = "pd-values_%d-for-seq-%d-exp-%d.txt" % (int(timestamp),seq,i+1)
# the primary purpose of this is to guarantee that the accumBuffer method has completed
                print "starting the wait for an accumBuffer done status message at %f" % time.time()
                tottime = pdresult.get();

# make sure the sample of the photo diode is complete
                time.sleep(10.)

                print "executing readBuffer, cdir=%s , pdfilename = %s" % (cdir,pdfilename)
                result = pdsub.synchCommand(1000,"readBuffer","%s/%s" % (cdir,pdfilename));
                buff = result.getResult()
                print "Finished getting readings at %f" % time.time()


                result = arcsub.synchCommand(200,"addBinaryTable","%s/%s" % (cdir,pdfilename),fitsfilename,"AMP0","AMP0_MEAS_TIMES","AMP0_A_CURRENT",timestamp)
#/home/ts3prod/jobHarness/jh_stage/e2v-CCD/NoCCD1/ready_acq/v0/180/pd-values_1434501729-for-seq-0-exp-1.txt /home/ts3prod/jobHarness/jh_stage/e2v-CCD/NoCCD1/ready_acq/v0/180/NoCCD1_lambda_400_000_lambda_1_20150616204212.fits MP time pd 123.00
                fpfiles.write("%s %s/%s %f\n" % (fitsfilename,cdir,pdfilename,timestamp))

# reset timeout to something reasonable for a regular command
            pdsub.synchCommand(1000,"setTimeout",10.);
            seq = seq + 1

    fpfiles.close();
    fp.close();

    fp = open("%s/status.out" % (cdir),"w");

    istate=0;
    result = tssub.synchCommandLine(10,"getstate");
    istate=result.getResult();
    fp.write(`istate`+"\n");
    fp.close();

# move TS to ready state                    
    tssub.synchCommand(60,"setTSReady");

# get the glowing vacuum gauge back on
    result = pdusub.synchCommand(120,"setOutletState",vac_outlet,True);
    rply = result.getResult();

    print "            TEST STAND APPEARS TO BE READY"
    print "          PLEASE PROCEED WITH THE EO TESTING"

except Exception, ex:

    raise Exception("There was an exception in the acquisition producer script. The message is\n (%s)\nPlease retry the step or contact an expert," % ex)


print "TS3_ready: COMPLETED"
