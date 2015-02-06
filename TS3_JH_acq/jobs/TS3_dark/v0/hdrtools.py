# LSST FITS Header Keyword Tools
# Various useful tools for manipulating FITS header keywords

import os

###########################################################################
# fitsAverage : get RTS2 computed average fof all segments in FITS file
def fitsAverage(filename):
    if (os.path.getsize(filename) < 35000000):
        print "File %s appears to be bogus." % filename
        return 0
    hdulist = pf.open(filename, mode='update')
    avg = 0.0
    segcount = 0
    for i in range(16):
        hdr=hdulist[i+1].header
        if 'AVERAGE' in hdr.keys(): 
            avg = avg + float(hdr['AVERAGE'])
            segcount = segcount+1
    avg = avg / segcount
    hdulist.close()
    return avg
