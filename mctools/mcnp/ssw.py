#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#
# file format description (not exactly correspond to the 6.1 version):
# https://mcnp.lanl.gov/pdf_files/la-ur-16-20109.pdf

import sys, math, struct, array

def fortranRead(f):
        """Read a fortran structure from a binary file
        return data, None for EOF
        """
        blen = f.read(4)
        if len(blen)==0: return None
        (size,) = struct.unpack("=i", blen)
        data  = f.read(size)
        blen2 = f.read(4)
        if blen != blen2:
                raise IOError("Reading fortran block")
        return data

#        """Class to read the SSW output file (wssa)"""
class SSW:
    def __init__(self, filename=None, verbose=False, debug=False):
        """Initialise a SSW structure"""
        self.reset()
        if filename is None: return
        self.verbose = verbose
        self.debug = debug
        self.mcnp6 = False
        self.readHeader(filename)

    def reset(self):
        """Reset header information"""
        self.file = None
        self.fname = ""
        self.kods = "" # 8 Code name
        self.vers = "" # 5 Version
        self.lods = "" # 8 Compilation Date
        self.idtms = "" # 19 Date and time that the file was generated
        self.probs = "" # 19 User specified surface source filename, minus extension
        self.aids = ""  # 80 problem description string
        self.knods = 0 #  last dump of SSW-run
        self.nevt = 0 # number of events (hits)

        self.isurfs = [] # 10 Surface indexes from MCNP input file
        self.kstpps = [] # 10 Surface type numbers of all the surfaces (from MCNP_GLOBAL module)
        self.ntppsp = [] # 10 Number of coefficients needed to define the surface type
        self.tpps = [] # 10,64 Array for surface parameters

        self.nrcd = 0 # length of ssb-array (?) = evtl+1 (?)
        self.nrcdo = 0
        self.N = 0 # number of incident particles

#     Structure of SSB-Arrays -- see Harold Breitkreutz thesis for details
        self.ssb  = [] # 11   Surface-Source info
        self.nslr = [] # 14,10  SS Info record

        self.supported_mcnpx_verstions = ('2.6.0', '26b', '2.7.0')
        self.supported_mcnp6_versions = ('6', '6.mpi')
        self.supported_mcnp_versions = self.supported_mcnpx_verstions + self.supported_mcnp6_versions
        self.isMacroBody = False # true if at least one of the surfaces is macrobody

    def getTitle(self):
        """Return the problem title"""
        return self.aids

    def getNTracks(self):
            """Return number of tracks"""
            return self.nevt

    def unsupported(self):
            print("WARNING: This version of MCNP(X) is not supported.", file=sys.stderr)
            print("         Contact the mc-tools authors in order to have this problem fixed.", file=sys.stderr)
            print("         https://github.com/kbat/mc-tools", file=sys.stderr)

    def readHeader(self, filename):
        """Read header information and return the file handle"""

        self.reset()
        self.fname = filename
        self.file = open(self.fname, "rb")

        data = fortranRead(self.file)
        if data is None: raise IOError("Invalid SSW file")
        size = len(data)
        if self.debug:
                print("* size1: ", size)
        if size == 8: # mcnp 6
                (tmpi0) = struct.unpack('8s',data) # wssa file type
                # print(" type_of_rssa:", tmpi0[0].decode())
                data = fortranRead(self.file)
                size = len(data)
                if self.debug:
                        print("*  size2: ", size)
                if size == 143: # mcnp <= 6.1
                        (self.kods, self.vers, self.lods, self.idtms, self.aids, self.knods) = struct.unpack("=8s5s28s18s80si", data)
                elif size == 191: # mcnp 6.2 [EV]
                        (self.kods, self.vers, self.lods, self.idtms, self.aids, self.knods) = struct.unpack("=8s5s28s18s128si", data)
                else:
                        self.unsupported()
                        sys.exit(1)

                self.vers = self.vers.decode().strip()
                if self.vers not in self.supported_mcnp6_versions:
                        print("version: %s" % self.vers)
                        raise IOError("ssw.py: format error _%s_" % self.vers)
        elif size==163:
                (self.kods, self.vers, self.lods, self.idtms, self.probs, self.aids, self.knods) = struct.unpack("=8s5s28s19s19s80si", data) # length=160
                self.vers = self.vers.decode().strip()
                self.probs = self.probs.decode().strip()

        elif size==167: # like in the Tibor's file with 2.7.0
                tmp = float(0)
                (self.kods, self.vers, self.lods, self.idtms, self.probs, self.aids, self.knods, tmp) = struct.unpack("=8s5s28s19s19s80sif", data) # length=160
                self.vers = self.vers.decode().strip()
                self.probs = self.probs.decode().strip()
        else:
                self.unsupported()
                sys.exit(1)

        self.kods = self.kods.decode().strip()   # code name
        self.lods = self.lods.decode().strip()   # date
        self.idtms = self.idtms.decode().strip() # machine designator
        self.aids = self.aids.decode().strip()   # title

        if self.verbose:
                print("Code:\t\t%s" % self.kods)
                print("Version:\t%s" % self.vers)
                print("Date:\t\t%s" % self.lods)
                print("Machine designator:", self.idtms)
                print("Problem id:\t%s" % self.probs) # why not read???
                print("Title:\t\t%s" % self.aids)
                print("knods:", self.knods)

        if self.kods not in ['mcnpx', 'mcnp'] or self.vers not in self.supported_mcnp_versions:
                self.unsupported()

        self.mcnp6 = self.vers in ("6", "6.mpi") # just to run readHit faster

        data = fortranRead(self.file)
        size = len(data)
        # np1 - history number in ssw-run
        # nrss - number of tracks in RSSA data
        # njsw - number of surfaces in RSSA data
        # niss - number of histories in RSSA data
        # niwr - number of cells in RSSA data (np1<0)
        # mipts - Partikel der Quelldatei = incident particles (?) (np1<0)
        if self.debug:
                print("* size3:", size)
        if self.vers in self.supported_mcnp6_versions:
                (np1,tmp1, nrss, tmp2, tmp3, njsw, self.nrcd,niss) = struct.unpack("=8i", data)
                if self.debug:
                        print("probs: ",np1, tmp1, nrss, tmp2, tmp3, njsw, self.nrcd, niss)
        elif size==20:
                (np1,nrss,self.nrcd,njsw,niss) = struct.unpack("=5i", data)
        elif size==40: # Tibor with 2.7.0
                (np1,tmp4,nrss,tmp2,self.nrcd, tmp1, njsw, tmp3, niss, tmp5) = struct.unpack("=5i5i", data)
        else:
                print(self.vers, size)
                self.unsupported()
                sys.exit(1)

        self.N = abs(np1)
        if self.verbose:
                print("number of incident particles:\t%i" % self.N)
                print("number of tracks:\t%i" % nrss)
                print("length of ssb array:\t%i" % self.nrcd)
                print("number of surfaces in RSSA data:\t%i" % njsw)
#                print("number of histories in RSSA data:\t%i" % niss)
        if self.debug:
                print("tmp: ",tmp1,tmp2,tmp3)

#       raise IOError("end")

        nevt = nrss # Number of tracks
        self.nrcdo = self.nrcd # Length of ssb array
        np1o = np1

        self.nevt = nevt
        tmp = []
        if np1 < 0:
                np1 = abs(np1)
                data = fortranRead(self.file)
                tmp = struct.unpack("=%di" % int(len(data)/4) ,data) # ??? why tmp ???
                niwr = tmp[0]
                mipts = tmp[1]
                if self.debug:
                        print("* np1<0 => tmp vector:",tmp)
        else:
                raise IOError("np1>=0")

        if self.nrcd != 6 and self.nrcd != 10: self.nrcd = self.nrcd - 1

        if self.debug:
                print("* for loop length (total number of surfaces): ",njsw+niwr)

        for i in range(njsw+niwr):
            data = fortranRead(self.file)
            size = len(data)
            isurfs, kstpps, ntppsp, tpps = struct.unpack("=3i%ds" % int(size-12), data) #  12=3*4 due to '3i'
            if kstpps>=30:
                    self.isMacroBody = True

            # convert tmp of type string into array of doubles:
            if self.isMacroBody != False:
                    vtpps = array.array('d')
            else:
                    vtpps = array.array('i')
            vtpps.fromstring(tpps)

            if self.debug:
                    print(f"* surface index: {isurfs}; type: {kstpps}; number of coefficients: {ntppsp}; surface coefficients: ", vtpps)
            self.isurfs.append(isurfs) # Surface indices from MCNP input file
            self.kstpps.append(kstpps) # Surface type numbers of all the surfaces (from MCNP_GLOBAL module)
            self.ntppsp.append(ntppsp) # Number of coefficients needed to define the surface type
            self.tpps.append(vtpps)    # Surface coefficients for each surface

        # Summary:
        data = fortranRead(self.file)
        size = len(data)
#        print(len(data), (2+4*mipts), (njsw+niwr))
#        for i in range(2+4*mipts):
#            for j in range(njsw+niwr):
#                a = 1 # !!! to be implemented

        return self.file

    def readHit(self):
        """Read neutron data and return the SSB array"""

        data = fortranRead(self.file)
        if self.mcnp6:
                size = len(data)
                size = size/8
                ssb = struct.unpack("=%dd" % int(size), data)
        else:
                ssb = struct.unpack("=%dd" % int(self.nrcd+1), data)

        return ssb
