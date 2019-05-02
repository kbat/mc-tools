#! /usr/bin/python  -W all
# https://github.com/kbat/mc-tools
# 

from __future__ import print_function
import sys, math, struct

#-------------------------------------------------------------------------------
# Read a fortran structure from a binary file
# @return data, None for EOF
#-------------------------------------------------------------------------------
def fortranRead(f):
        blen = f.read(4)
        if len(blen)==0: return None
        (size,) = struct.unpack("=i", blen)
#       print("length:", size)
        data  = f.read(size)
        blen2 = f.read(4)
        if blen != blen2:
                raise IOError("Reading fortran block")
        return data


#-------------------------------------------------------------------------------
# Unpack an array of floating point numbers
#-------------------------------------------------------------------------------
def unpackArray(data):
        return struct.unpack("=%df"%(len(data)//4),  data)


def unsupported():
        print("Your MCNP(X) version is not supported.", file=sys.stderr)
        sys.exit(1)


#       """Class to read the SSW output file (wssa)"""
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
        self.kods = "" # 8 Code ID
        self.vers = "" # 5 Version
        self.lods = "" # 8 Date
        self.idtms = "" # 19 Machine Designator and date of SSW-run
        self.probs = "" # 19 Problem ID
        self.aids = ""  # 80 Creation-Run Problem-Title-Card
        self.knods = 0 #  last dump of SSW-run
        self.nevt = 0 # number of events (hits)

        self.isurfs = [] # 10 Array fur Oberflachen
        self.kstpps = [] # 10 Array fur Overflachentypen
        self.ntppsp = [] # 10 Array fur Anzahl der Oberflachen-Parameter
        self.tpps = [] # 10,64 Array for surface parameters

        self.nrcd = 0 # length of ssb-array (?) = evtl+1 (?)
        self.nrcdo = 0
        self.N = 0 # number of incident particles

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
#        print("size: ", size)
        if size == 8: # mcnp 6
                (tmpi0) = struct.unpack("8s", data) # wssa file type
#               print("type_of_rssa:", tmpi0)
                data = fortranRead(self.file)
                (self.kods, self.vers, self.lods, self.idtms, self.aids, self.knods) = struct.unpack("=8s5s28s18s80si", data)
                self.vers = self.vers.strip()
                if self.vers not in  ("6", "6.mpi"):
                        print("'%s'" % self.vers)
                        raise IOError("ssw.py: format error %s")
        elif size==163:
                (self.kods, self.vers, self.lods, self.idtms, self.probs, self.aids, self.knods) = struct.unpack("=8s5s28s19s19s80si", data) # length=160
                self.vers = self.vers.strip()
        elif size==167: # like in the Tibor's file with 2.7.0
                tmp = float(0)
                (self.kods, self.vers, self.lods, self.idtms, self.probs, self.aids, self.knods, tmp) = struct.unpack("=8s5s28s19s19s80sif", data) # length=160
#               print("tmp: ", tmp)
                self.vers = self.vers.strip()
        else:
                unsupported()

        print("Code:\t\t%s" % self.kods)
        print("Version:\t%s" % self.vers)
        print("Date:\t\t%s" % self.lods)
        print("Machine designator:", self.idtms)
        print("Problem id:\t%s" % self.probs)
        print("Title:\t\t%s" % self.aids.strip())
#        print("knods:", self.knods)

        supported_mcnp_versions = ['2.6.0', '26b', '2.7.0', '6', '6.mpi']
#        print(self.kods.strip(), self.vers)
        if self.kods.strip() not in ['mcnpx', 'mcnp'] or self.vers not in supported_mcnp_versions:
                print("WARNING: This version of MCNPx (%s) might not be supported." % self.vers, file=sys.stderr)
                print("\t The code was developed for SSW files produced by these MCNPX versions:", supported_mcnp_versions, file=sys.stderr)

        data = fortranRead(self.file)
        size = len(data)
        # np1 - history number in ssw-run
        # nrss - number of tracks in RSSA data
        # njsw - number of surfaces in RSSA data
        # niss - number of histories in RSSA data
        # niwr - number of cells in RSSA data (np1<0)
        # mipts - Partikel der Quelldatei = incident particles (?) (np1<0)
#       print("size", size)
        if self.vers in ("6", "6.mpi"):
#               (np1,nrss,self.nrcd,njsw,niss,self.probs) = struct.unpack("=5i12s", data)
                (np1,tmp1, nrss, tmp2, tmp3, njsw, self.nrcd,niss) = struct.unpack("=4i4i", data)
                print("probs",np1, tmp1, tmp2, tmp3, nrss, self.nrcd, njsw, niss)
        elif size==20:
                (np1,nrss,self.nrcd,njsw,niss) = struct.unpack("=5i", data)
        elif size==40: # Tibor with 2.7.0
                (np1,tmp4,nrss,tmp2,self.nrcd, tmp1, njsw, tmp3, niss, tmp5) = struct.unpack("=5i5i", data)
#               print("A", np1,nrss, niss, tmp2, self.nrcd)
#               print("B", tmp1, njsw, tmp3, tmp4, tmp5)
        else:
                print(self.vers, size)
                unsupported()

        self.N = abs(np1)
        print("number of incident particles:\t%i" % abs(np1))
        print("number of tracks:\t%i" % nrss)
        print("length of ssb array:\t%i" % self.nrcd)
        print("number of surfaces in RSSA data:\t%i" % njsw)
        print("number of histories in RSSA data:\t%i" % niss)

#       raise IOError("end")
        

        nevt = nrss
        self.nrcdo = self.nrcd
        np1o = np1

#        print("Number of tracks:", nevt)
        self.nevt = nevt
        tmp = []
        if np1 < 0:
            np1 = abs(np1)
            data = fortranRead(self.file)
#            print(len(data))
            # (niwr, mipts,tmp
            tmp = struct.unpack("=%di" % int(len(data)/4) ,data) # ??? why tmp ???
            niwr = tmp[0]
            mipts = tmp[1]
#            print(niwr,mipts,tmp)
            
        if self.nrcd != 6 and self.nrcd != 10: self.nrcd = self.nrcd - 1

        for i in range(njsw+niwr):
            data = fortranRead(self.file)
            size = len(data)
#            print("size", size)
            tmpii, tmpkk, tmpnn, tmp = struct.unpack("=3i%ds" % int(size-12), data) #  12=3*4 due to '3i'
#            print("tmpnn", tmpnn, len(tmp))
            # if self.vers == '2.7.0':
            #       print("") # struct.unpack("2f", tmp)
            # elif self.vers == '2.6.0':
            #       print("") # struct.unpack("3f", tmp)
            # else:
            #       print("This MCNP version is not supported:", self.vers)
#                   sys.exit(1)
            self.isurfs.append(tmpii)
            self.kstpps.append(tmpkk)
            self.ntppsp.append(tmpnn)

        data = fortranRead(self.file)
#        print(len(data), (2+4*mipts), (njsw+niwr))
#        for i in range(2+4*mipts):
#            for j in range(njsw+niwr):
#                a = 1 # !!! to be implemented
        
        return self.file

    def readHit(self):
        """Read neutron data and return the SSB array"""
        data = fortranRead(self.file)
        if self.vers in ("6", "6.mpi"):
                size = len(data)
#               print("here", self.nrcd, size)
                size = size/8
                ssb = struct.unpack("=%dd" % int(size), data)
        else:
                ssb = struct.unpack("=%dd" % int(self.nrcd+1), data) # ??? why +1 Esben does not have it
        return ssb
