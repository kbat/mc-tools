#! /usr/bin/python
# $Id$

import sys, math, struct

#-------------------------------------------------------------------------------
# Read a fortran structure from a binary file
# @return data, None for EOF
#-------------------------------------------------------------------------------
def fortranRead(f):
        blen = f.read(4)
        if len(blen)==0: return None
        (size,) = struct.unpack("=i", blen)
        data  = f.read(size)
        blen2 = f.read(4)
        if blen != blen2:
                raise IOError("Reading fortran block")
        return data

#-------------------------------------------------------------------------------
# Skip a fortran block from a binary file
# @return size, None for EOF
#-------------------------------------------------------------------------------
def fortranSkip(f):
        blen = f.read(4)
        if len(blen)==0: return 0
        (size,) = struct.unpack("=i", blen)
        f.seek(size, 1)
        blen2 = f.read(4)
        if blen != blen2:
                raise IOError("Skipping fortran block")
        return size

#-------------------------------------------------------------------------------
# Unpack an array of floating point numbers
#-------------------------------------------------------------------------------
def unpackArray(data):
        return struct.unpack("=%df"%(len(data)//4),  data)

class SSW:
    def __init__(self, filename=None):
        """Initialise a SSW structure"""
        self.reset()
        if filename is None: return
        self.readHeader(filename)

    def reset(self):
        """Reset header information"""
        self.file = None
        self.fname = ""
        self.kods = "" # 8 Code
        self.vers = "" # 5 Version
        self.lods = "" # 8 Date
        self.idtms = "" # 19 Machine Designator
        self.probs = "" # 19 Problem ID
        self.aids = ""  # 80 Creation-Run Problem-Title-Card
        self.nevt = 0 # number of events (hits)

        self.isurfs = [] # 10 Array fur Oberflachen
        self.kstpps = [] # 10 Array fur Overflachentypen
        self.ntppsp = [] # 10 Array fur Anzahl der Oberflachen-Parameter
        self.tpps = [] # 10,64 Array for surface parameters

        self.nrcd = 0
        self.nrcdo = 0

#     Structure of SSB-Arrays -- see Harold Breitkreutz thesis for details
        self.ssb  = [] # 11   Surface-Source info
        self.nslr = [] # 14,10  SS Info record

    def getTitle(self):
	"""Return the problem title"""
	return self.aids.strip()

    def readHeader(self, filename, nevt=0):
        """Read header information and return the file handle"""
        self.reset()
        self.fname = filename
        self.file = open(self.fname, "rb")

        data = fortranRead(self.file)
        if data is None: raise IOError("Invalid SSW file")
        size = len(data)
        # This is according to Esben's subs.f, but the format seems to be wrong
#        (kods, vers, lods, idtms, probs, aids, knods) = struct.unpack("=8s5s8s19s19s80s24s", data) # ??? why 24s ???
        # This has been modified to fix the format:
        (kods, vers, lods, idtms, probs, aids, knods) = struct.unpack("=8s5s28s19s19s80si", data)


        print "Code:\t\t%s" % kods
        print "Version:\t%s" % vers
        print "Date:\t\t%s" % lods
        print "Machine designator:", idtms
        print "Problem id:\t%s" % probs
        print "Title:\t\t%s" % aids.strip()
        print "knods:", knods

        data = fortranRead(self.file)
        size = len(data)
        (np1,nrss,self.nrcd,njsw,niss) = struct.unpack("=5i", data)
        print np1,nrss,self.nrcd,njsw,niss

        nevt = nrss
        self.nrcdo = self.nrcd
        np1o = np1

        print "Number of hits:", nevt
        self.nevt = nevt
        tmp = []
        if np1 < 0:
            np1 = abs(np1)
            data = fortranRead(self.file)
#            print len(data)
            # (niwr, mipts,tmp
            tmp = struct.unpack("=%di" % int(len(data)/4) ,data) # ??? why tmp ???
            niwr = tmp[0]
            mipts = tmp[1]
            print niwr,mipts,tmp
            
        if self.nrcd != 6 and self.nrcd != 10: self.nrcd = self.nrcd - 1

        for i in range(njsw+niwr):
            data = fortranRead(self.file)
            size = len(data)
#            print "size", size
            tmpii, tmpkk, tmpnn, tmp = struct.unpack("=3i%ds" % int(size-12), data) #  12=3*4 due to '3i'
#            print "tmpnn", tmpnn, len(tmp)
            print struct.unpack("2f", tmp)
            self.isurfs.append(tmpii)
            self.kstpps.append(tmpkk)
            self.ntppsp.append(tmpnn)

        data = fortranRead(self.file)
#        print len(data), (2+4*mipts), (njsw+niwr)
#        for i in range(2+4*mipts):
#            for j in range(njsw+niwr):
#                a = 1 # !!! to be implemented
        
        return self.file

    def readHit(self):
        """Read neutron data and return the SSB array"""
        data = fortranRead(self.file)
#        print self.nrcd, len(data)
        ssb = struct.unpack("=%dd" % int(self.nrcd+1), data) # ??? why +1 Esben does not have it
#        print len(ssb)
        # print "1 history:", ssb[0]
        # print "2 particle:", ssb[1]
        # print "3 weight:", ssb[2]
        # print "4 time:", ssb[3]
        # print "5 time [sec]:", ssb[4]
        # print "6 x:", ssb[5]
        # print "7 y:", ssb[6]
        # print "8 z:", ssb[7]
        # print "9 wx:", ssb[8] # ??? is it correct ???
        # print "10 wy:", ssb[9] # ??? is it correct ???
        return ssb
