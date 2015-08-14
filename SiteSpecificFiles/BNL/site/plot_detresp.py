import glob
import pyfits
import lsst.eotest.sensor as sensorTest
import lsst.afw.math as afwMath
import pylab_plotter as plot

flats = sorted(glob.glob('/home/ts3prod/jobHarness/jh_stage/ITL-CCD/ITL-113-10/flat_acq/v0/3385/*_flat*flat1*.fits'))

amp = 1

outfile = 'flat1_data_amp%02i.txt' % amp
output = open(outfile, 'w')
output.write(" id    EXPTIME    MONDIODE   median ADU\n")
for flat in flats:
    ccd = sensorTest.MaskedCCD(flat)
    im = ccd.unbiased_and_trimmed_image(amp)
    adu_median = afwMath.makeStatistics(im, afwMath.MEDIAN).getValue()
    foo = pyfits.open(flat)
    hdr = foo[0].header
    id = flat.split('_')[3]
    format = "%s  %8.3f  %12.4e  %7.1f\n"
    output.write(format % (id, hdr['EXPTIME'], hdr['MONDIODE'], adu_median))
output.close()

detresp = sensorTest.DetectorResponse('/home/ts3prod/jobHarness/jh_stage/ITL-CCD/ITL-113-10/flat_pairs/v0/3398/ITL-113-10_det_response.fits')

win = plot.xyplot(detresp.flux, detresp.Ne[amp], xlog=1,
                  xrange=(1e-14, 1e-7), ylog=1,
                  xname='incident flux (=abs(EXPTIME*MONDIODE))',
                  yname='e-/pixel')
win.set_title('detector response, amp %i, gain=%.2f' % (amp, 0.75))
plot.hline(100)
plot.hline(5e4)
plot.save('detresp_amp%02i.png' % amp)
