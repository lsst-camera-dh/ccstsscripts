# LSST FITS Header Keyword Tools
# Various useful tools for manipulating FITS header keywords

import pyfits as pf
import numpy
#from astropy.io import fits as pf
import os

###########################################################################
# fixKey : 'fix' a keyword. If found, use current value, else add it.
# In any case, update the comment. If specified, put it after some other 
def fixKey(hdr, name, default, comment, after='') :
    keys = hdr.keys()
    if name in keys : 
        if len(after) == 0 : hdr.update(name, hdr[name], comment)
        else : hdr.update(name, hdr[name], comment, after=after)
    else : 
        if len(after) == 0 : hdr.update(name, default, comment)
        else : hdr.update(name, default, comment, after=after)
    return

###########################################################################
# moveKey : move a keyword to a particular place in the header by specifying 
# the keyword that it should follow.
def moveKey(hdr, name, after) :
    keys = hdr.keys()
    if after not in keys : print "After Keyword ", after, " not found"
    else : 
        if name in keys : hdr.update(name, hdr[name], phdr.comments[name], after=after)
        else : print "Keyword ", name, " not found"
    return

###########################################################################
# copyKey : copy a keyword from one image header to another, optionally
# specifying the keyword that it should follow.
def copyKey(src_hdr, dest_hdr, name, after) :
    skeys = src_hdr.keys()
    if name in skeys : 
        if len(after) == 0 : hdr.update(name, dest_hdr[name], comment)
        else : hdr.update(name, hdr[name], comment, after=after)
    else : 
        if len(after) == 0 : hdr.update(name, default, comment)
        else : hdr.update(name, default, comment, after=after)
    return    
    
###############################################################################
# addKey : add a keyword/value pair to the header of a FITS file    
def addKey(filename, keyword, value, ext_no=0):
    if (os.path.getsize(filename) < 35000000):
        print "File %s appears to be bogus." % filename
        return
    hdulist = pf.open(filename, mode='update')
    hdr=hdulist[int(ext_no)].header   # get the right header
    hdr.update(keyword, value)
    hdulist.close()
    return
    
###########################################################################
# delKey : delete a keyword. If it doesn't exist, don't crash.
def delKey(hdr, name) :
    keys = hdr.keys()
    if name in keys : 
        hdr.remove(name)
    return
    
###########################################################################
# rts2fix : go through header keys replacing . with _ as required 
def rts2fix( hdr ):
    # Get rid of some useless keywords. These are always 'T'
    delKey(hdr,'CHAN1')
    delKey(hdr,'CHAN2')
    delKey(hdr,'CHAN3')
    delKey(hdr,'CHAN4')
    delKey(hdr,'CHAN5')
    delKey(hdr,'CHAN6')
    delKey(hdr,'CHAN7')
    delKey(hdr,'CHAN8')
    delKey(hdr,'CHAN9')
    delKey(hdr,'CHAN10')
    delKey(hdr,'CHAN11')
    delKey(hdr,'CHAN12')
    delKey(hdr,'CHAN13')
    delKey(hdr,'CHAN14')
    delKey(hdr,'CHAN15')
    delKey(hdr,'CHAN16')
    ### we don't use these for anything, ever 
    delKey(hdr,'DEVNAME')
    delKey(hdr,'DEVNUM')
    delKey(hdr,'DEVNT')
    delKey(hdr,'SDELAY')
    ### these have values that are too long and pyfits can't seem to deal 
    delKey(hdr,'K_PHOT_IDN')
    delKey(hdr,'K_BIAS_IDN')
    delKey(hdr,'E3631A_IDN')
    delKey(hdr,'K_PHOT.IDN')
    delKey(hdr,'K_BIAS.IDN')
    delKey(hdr,'E3631A.IDN')
    delKey(hdr,'LAMP.hours')

    hdr_keys = hdr.keys()
    for j in range(0, len(hdr_keys)) :
        name = hdr_keys[j]
        value = hdr[name]
        comment = hdr.comments[name]
        # if name includes a '.', replace with a '_' and update hdr
        if name.find('.') != -1 :
            new_name = name.replace('.','_')
            new_name = new_name.upper()
            if (len(new_name) > 8) : new_name = 'HIERARCH '+new_name
            hdr[new_name] = (value, comment)
#            if name != 'LAMP.identification' :
#                if name != 'LAMP.hours' : delKey(hdr, name)
    return

###########################################################################
# dtStamp : add a date/time stamp to a FITS file name 

def dtStamp(filename) :
    if (os.path.getsize(filename) < 35000000):
        print "File %s appears to be bogus." % filename
        return filename
    hdulist = pf.open(filename, mode='update')
    phdr=hdulist[0].header
    phdr.add_history("Updated via LSST time/date stamper", before='CTIME')
    phdr_keys = phdr.keys()
    
    if 'TSTAMPED' in phdr_keys : 
        logger.log("File: ", filename, " already time stamped. Returning.")
    else:
        fixKey( phdr, 'TSTAMPED', 1, 'Time stamped', after='ORIGIN')
        phdr.add_history("Filename updated with time stamp", after='TSTAMPED')
        # get the date-obs string, make time stamp, add time stamp to header, close file
        if 'DATE-OBS' in phdr_keys :  
            dstr = phdr['DATE-OBS']
            tstamp = dstr[0:4]+dstr[5:7]+dstr[8:10]+dstr[11:13]+dstr[14:16]+dstr[17:19]
            phdr.update('TIMSTAMP', tstamp, 'File time stamp', after='DATE-OBS')        
            hdulist.close()
            # now apply timestamp to filename
            basename=filename[0:len(filename)-5]
            newname= basename+'_'+tstamp+'.fits'
            os.rename(filename,newname)
        else :
            print "No DATE-OBS keyword found in file : %s" % filename
    return newname

###########################################################################
# segAverage : get RTS2 computed average for a segment in a FITS file
def segAverage(filename, segment):
    if (os.path.getsize(filename) < 35000000):
        print "File %s appears to be bogus." % filename
        return 0
    hdulist = pf.open(filename, mode='update')
    hdr=hdulist[segment].header
    if 'AVERAGE' in hdr.keys(): 
        avg = float(hdr['AVERAGE'])
    else :
        avg = float(0.00)
    hdulist.close()
    return avg

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
        else :
            print "AVERAGE is not there for segment %d so we will calculate and put it there" % i
            segavg = 0.0
            nvals = 0
            nx2 = hdr['NAXIS2']
            for ix2 in range (nx2):
#                print "working on column %d" % ix2
                for val in hdulist[i+1].data[ix2] :
#                    print "val = %f" % float(val)
                    segavg = segavg + float(val)
                    nvals = nvals + 1
            segavg = segavg / nvals
            hdr.update("AVERAGE", segavg)
            print "AVERAGE set to %f for %d values" % (segavg,nvals)
            avg = avg + segavg
        segcount = segcount+1
    avg = avg / segcount
    hdulist.close()
    return avg

###########################################################################
# hdrsummary : produces a summary file (outfile) of essential values from the header
def hdrsummary(filename,outfile):
    if (os.path.getsize(filename) < 35000000):
        print "File %s appears to be bogus." % filename
        return 0
    outfl = open(outfile,"a")
    hdulist = pf.open(filename, mode='readonly')

    avg = fitsAverage(filename)
    outfl.write("%s\n" % filename);
    outfl.write("Average image signal = %f \n" % avg);

    phdr=hdulist[0].header
    outfl.write("Monochromator wavelength = %f\n" % phdr['MONOWL'])
    outfl.write("CCD temperature = %f\n" % phdr['CCDTEMP'])
    outfl.write("Photodiode reading  = %f\n" % phdr['MONDIOD'])
    outfl.write("Filter position  = %d\n" % phdr['FILTPOS'])
    for i in range(16):
        hdr=hdulist[i+1].header
        outfl.write("%15s | AVG= %9.3f | AVGBIAS= %9.3f | WITHOUTBIAS= %9.3f | STDBIAS= %9.3f\n" % (hdr['EXTNAME'],hdr['AVERAGE'],hdr['AVGOVR'],hdr['AVGNOOVR'],hdr['STDOVR']))
    hdulist.close()
    outfl.close()

###########################################################################
# addPDvals : add binary table of photodiode readings to a FITS file
#   1 | XTENSION= 'BINTABLE'           / binary table extension
#   2 | BITPIX  =                    8 / 8-bit bytes
#   3 | NAXIS   =                    2 / 2-dimensional binary table
#   4 | NAXIS1  =                   16 / width of table in bytes
#   5 | NAXIS2  =                  500 / number of rows in table
#   6 | PCOUNT  =                    0 / size of special data area
#   7 | GCOUNT  =                    1 / one data group (required keyword)
#   8 | TFIELDS =                    2 / number of fields in each row
#   9 | TTYPE1  = 'AMP0_MEAS_TIMES'    / label for field   1
#  10 | TFORM1  = 'D       '           / data format of field: 8-byte DOUBLE
#  11 | TUNIT1  = 'A       '           / physical unit of field
#  12 | TTYPE2  = 'AMP0_A_CURRENT'     / label for field   2
#  13 | TFORM2  = 'D       '           / data format of field: 8-byte DOUBLE
#  14 | TUNIT2  = 'A       '           / physical unit of field
#  15 | EXTNAME = 'AMP0.MEAS_TIMES'    / name of this binary table extension
#  16 | TSTART  =     1418929454.78162 / data are recorded from this time

def addPDvals(filename,pdfile,extnam,tstart):
    if (os.path.getsize(filename) < 35000000):
        print "File %s appears to be bogus." % filename
        return 0
    hdulist = pf.open(filename, mode='update')
    tmdata = numpy.zeros((3000), dtype=numpy.float64)
    pddata = numpy.zeros((3000), dtype=numpy.float64)
#    fpd = open("%s/pd-values-for-seq-%d-exp-%d" % (cdir,seq,i),"r");
    fpd = open(pdfile,"r");
    ival = 0
    for line in fpd:
        tokens = str.split(line)
        pdval = float(tokens[1])
        pdtime = float(tokens[0])
        print "time = %10.4e , pdval = %10.4e" % (pdtime,pdval)
        pddata[ival] = pdval
        tmdata[ival] = pdtime
        ival = ival + 1
    fpd.close()
#    hdulist.append(pf.BinTableHDU(data=(tmdata,pddata)))
    c1 = pf.Column(name='AMP0_MEAS_TIMES', format='D', array=tmdata)
    c2 = pf.Column(name="AMP0_A_CURRENT", format="D", array=pddata)
    table_hdu = pf.new_table([c1, c2])
    hdulist.append(table_hdu)

    for seg in hdulist :
        hdr=seg.header

    hdr.update("EXTNAME", extnam)
    hdr.update("TSTART", tstart)

    hdulist.close()


###########################################################################
# fitsExptime: get the exposure time from a FITS file
def fitsExptime(filename):
#...     try:
#...         hdulist = pf.open(filename, mode='update')
#...     except IOError:
#...         print "File %s appears to be bogus." % filename
#            return 'UNKNOWN'
    if (os.path.getsize(filename) < 35000000):
        print "File %s appears to be bogus." % filename
        return 'UNKNOWN'
    hdulist = pf.open(filename, mode='update')
    hdr=hdulist[0].header
    if 'EXPTIME' in hdr_keys: 
        exptime = float(hdr['EXPTIME'])
    else:
        exptime = 'UNKNOWN'
    hdulist.close()
    return exptime

#...     try:
#...         hdulist = pf.open(filename, mode='update')
#...     except IOError:
#...         print "File %s appears to be bogus." % filename
#            return 'UNKNOWN'
