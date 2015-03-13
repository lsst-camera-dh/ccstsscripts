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
# addPDvals : get RTS2 computed average fof all segments in FITS file
def addPDvals(filename,pdfile,extnam,nplc):
    if (os.path.getsize(filename) < 35000000):
        print "File %s appears to be bogus." % filename
        return 0
    hdulist = pf.open(filename, mode='update')
    data = numpy.zeros((3000), dtype=numpy.float64)
#    fpd = open("%s/pd-values-for-seq-%d-exp-%d" % (cdir,seq,i),"r");
    fpd = open(pdfile,"r");
    ival = 1
    for line in fpd:
        pdval = float(line)
        print "pdval = %10.4e" % pdval
        data[ival] = pdval
        ival = ival + 1
    fpd.close()
    hdulist.append(pf.ImageHDU(data=data))
    for seg in hdulist :
        hdr=seg.header
    hdr.update("EXTNAME", extnam)
    hdr.update("NPLC", int(nplc))

#    seg = hdulist[17]
# Float64
#    seg.BITPIX = -64
# one dimension
#    seg.NAXIS  = 1
# number of values
#    seg.NAXIS1 = 3000
#    seg.data.dtype = -64
#    print "dtype = %d" % seg.data.dtype
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
