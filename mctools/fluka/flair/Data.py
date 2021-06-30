# -*- coding: utf-8 -*-
#
# Copyright European Organization for Nuclear Research (CERN)
# All rights reserved
#
# Please look at the supplied documentation for the user's
# license
#
# Author: Vasilis.Vlachoudis@cern.ch
# Date:   24-Oct-2006

__author__ = "Vasilis Vlachoudis"
__email__  = "Vasilis.Vlachoudis@cern.ch"

import io
import re
import math
import struct

import mctools.fluka.flair.bmath as bmath
import mctools.fluka.flair.fortran as fortran
from mctools.fluka.flair.log import say
try:
        import numpy
except ImportError:
        numpy = None

_detectorPattern = re.compile(r"^ ?# ?Detector ?n?:\s*\d*\s*(.*)\s*", re.MULTILINE)
_blockPattern    = re.compile(r"^ ?# ?Block ?n?:\s*\d*\s*(.*)\s*",    re.MULTILINE)

#-------------------------------------------------------------------------------
# Unpack an array of floating point numbers
#-------------------------------------------------------------------------------
def unpackArray(data):
        return struct.unpack("=%df"%(len(data)//4),  data)

#===============================================================================
# Empty class to fill with detector data
#===============================================================================
class Detector:
        pass

#===============================================================================
# Base class for all detectors
#===============================================================================
class Usrxxx:
        def __init__(self, filename=None):
                """Initialize a USRxxx structure"""
                self.reset()
                if filename is None: return
                self.readHeader(filename)

        # ----------------------------------------------------------------------
        def reset(self):
                """Reset header information"""
                self.file     = ""
                self.title    = ""
                self.time     = ""
                self.weight   = 0
                self.ncase    = 0
                self.nbatch   = 0
                self.detector = []
                self.seekpos  = -1
                self.statpos  = -1

        # ----------------------------------------------------------------------
        # Read information from USRxxx file
        # @return the handle to the file opened
        # ----------------------------------------------------------------------
        def readHeader(self, filename):
                """Read header information, and return the file handle"""
                self.reset()
                self.file = filename
                f = open(self.file, "rb")

                # Read header
                data = fortran.read(f)
                if data is None: raise IOError("Invalid USRxxx file")
                size   = len(data)
                over1b = 0
                if   size == 116:
                        (title, time, self.weight) = \
                                struct.unpack("=80s32sf", data)
                        self.ncase  = 1
                        self.nbatch = 1
                elif size == 120:
                        (title, time, self.weight, self.ncase) = \
                                struct.unpack("=80s32sfi", data)
                        self.nbatch = 1
                elif size == 124:
                        (title, time, self.weight,
                         self.ncase, self.nbatch) = \
                                struct.unpack("=80s32sfii", data)
                elif size == 128:
                        (title, time, self.weight,
                         self.ncase, over1b, self.nbatch) = \
                                struct.unpack("=80s32sfiii", data)
                else:
                        raise IOError("Invalid USRxxx file")

                if over1b>0:
                        self.ncase = self.ncase + over1b*1000000000

                self.title = title.strip().decode()
                self.time  = time.strip().decode()

                return f

        # ----------------------------------------------------------------------
        # Read detector data
        # ----------------------------------------------------------------------
        def readData(self, n):
                """Read n(th) detector data structure"""
                f = open(self.file, "rb")
                fortran.skip(f) # Skip header
                for _ in range(2*n):
                        fortran.skip(f) # Detector Header & Data
                fortran.skip(f)         # Detector Header
                data = fortran.read(f)
                f.close()
                return data

        # ----------------------------------------------------------------------
        # Read detector statistical data
        # ----------------------------------------------------------------------
        def readStat(self, n):
                """Read n(th) detector statistical data"""
                if self.statpos < 0: return None
                f = open(self.file, "rb")
                f.seek(self.statpos)
                for _ in range(n):
                        fortran.skip(f) # Detector Data
                data = fortran.read(f)
                f.close()
                return data

        # ----------------------------------------------------------------------
        def sayHeader(self):
                say("File   : ",self.file)
                say("Title  : ",self.title)
                say("Time   : ",self.time)
                say("Weight : ",self.weight)
                say("NCase  : ",self.ncase)
                say("NBatch : ",self.nbatch)

#===============================================================================
# Residual nuclei detector
#===============================================================================
class Resnuclei(Usrxxx):
        # ----------------------------------------------------------------------
        # Read information from a RESNUCLEi file
        # Fill the self.detector structure
        # ----------------------------------------------------------------------
        def readHeader(self, filename):
                """Read residual nuclei detector information """
                f = super().readHeader(filename)
                self.nisomers = 0
                if self.ncase <= 0:
                        self.evol = True
                        self.ncase = -self.ncase

                        data = fortran.read(f)
                        nir = (len(data)-4)//8
                        self.irrdt = struct.unpack("=i%df"%(2*nir), data)
                else:
                        self.evol  = False
                        self.irrdt = None

                for _ in range(1000):
                        # Header
                        data = fortran.read(f)
                        if data is None: break
                        size = len(data)
                        self.irrdt = None

                        # Statistics are present?
                        if size == 14:
                                if data[:8] == b"ISOMERS:":
                                        self.nisomers = struct.unpack("=10xi",data)[0]
                                        data = fortran.read(f)
                                        data = fortran.read(f)
                                        size = len(data)
                                if data[:10] == b"STATISTICS":
                                        self.statpos = f.tell()
                                        break
                        elif size != 38:
                                raise IOError("Invalid RESNUCLEi file header size=%d"%(size))

                        # Parse header
                        header = struct.unpack("=i10siif3i", data)

                        det = Detector()
                        det.nb     = header[0]
                        det.name   = header[1].strip().decode()
                        det.type   = header[2]
                        det.region = header[3]
                        det.volume = header[4]
                        det.mhigh  = header[5]
                        det.zhigh  = header[6]
                        det.nmzmin = header[7]

                        self.detector.append(det)

                        if self.evol:
                                data = fortran.read(f)
                                self.tdecay = struct.unpack("=f", data)
                        else:
                                self.tdecay = 0.0

                        size  = det.zhigh * det.mhigh * 4
                        if size != fortran.skip(f):
                                raise IOError("Invalid RESNUCLEi file")

                f.close()

        # ----------------------------------------------------------------------
        # Read detector data
        # ----------------------------------------------------------------------
        def readData(self, n):
                """Read n(th) detector data structure"""
                f = open(self.file, "rb")
                fortran.skip(f)
                if self.evol:
                        fortran.skip(f)

                for _ in range(n):
                        fortran.skip(f)         # Detector Header & Data
                        if self.evol:
                                fortran.skip(f) # TDecay
                        fortran.skip(f)         # Detector data
                        if self.nisomers:
                                fortran.skip(f) # Isomers header
                                fortran.skip(f) # Isomers data

                fortran.skip(f)                 # Detector Header & Data
                if self.evol:
                        fortran.skip(f)         # TDecay
                data = fortran.read(f)          # Detector data
                f.close()
                return data

        # ----------------------------------------------------------------------
        # Read detector isomeric data
        #SM START: Added method to read isomeric data  02/08/2016
        # ----------------------------------------------------------------------
        def readIso(self, n):
                """Read detector det data structure"""
                #print "self.nisomers:", self.nisomers
                if self.nisomers < 0: return None
                f = open(self.file, "rb")
                fortran.skip(f)
                if self.evol:
                        fortran.skip(f)

                for _ in range(n):
                        fortran.skip(f)         # Detector Header & Data
                        if self.evol:
                                fortran.skip(f) # TDecay
                        fortran.skip(f)         # Detector data
                        if self.nisomers:
                                fortran.skip(f) # Isomers header
                                fortran.skip(f) # Isomers data
                fortran.skip(f)
                if self.evol:
                        fortran.skip(f) # TDecay
                fortran.skip(f)         # Detector data
                isohead = fortran.read(f) # Isomers header
                data = fortran.read(f)    # Isomers data
                #print "isohead:",len(isohead)
                #header = struct.unpack("=10xi", isohead)
                #print "isohead:",header[0]
                f.close()
                return (isohead, data)

        # ----------------------------------------------------------------------
        # Read detector statistical data
        # ----------------------------------------------------------------------
        def readStat(self, n):
                """Read n(th) detector statistical data"""
                if self.statpos < 0: return None
                f = open(self.file, "rb")
                f.seek(self.statpos)

                f.seek(self.statpos)
                if self.nisomers:
                        nskip = 7*n
                else:
                        nskip = 6*n
                for _ in range(nskip):
                        fortran.skip(f) # Detector Data

                total = fortran.read(f)
                A     = fortran.read(f)
                errA  = fortran.read(f)
                Z     = fortran.read(f)
                errZ  = fortran.read(f)
                data  = fortran.read(f)
                if self.nisomers:
                        iso = fortran.read(f)
                else:
                        iso = None
                f.close()
                return (total, A, errA, Z, errZ, data, iso)

        # ----------------------------------------------------------------------
        def say(self, det=None):
                """print header/detector information"""
                if det is None:
                        self.sayHeader()
                else:
                        binning = self.detector[det]
                        say("Bin    : ", binning.nb)
                        say("Title  : ", binning.name)
                        say("Type   : ", binning.type)
                        say("Region : ", binning.region)
                        say("Volume : ", binning.volume)
                        say("Mhigh  : ", binning.mhigh)
                        say("Zhigh  : ", binning.zhigh)
                        say("NMZmin : ", binning.nmzmin)

#===============================================================================
# Usrbdx Boundary Crossing detector
#===============================================================================
class Usrbdx(Usrxxx):
        # ----------------------------------------------------------------------
        # Read information from a USRBDX file
        # Fill the self.detector structure
        # ----------------------------------------------------------------------
        def readHeader(self, filename):
                """Read boundary crossing detector information"""
                f = super().readHeader(filename)

                for _ in range(1000):
                        # Header
                        data = fortran.read(f)
                        if data is None: break
                        size = len(data)

                        # Statistics are present?
                        if size == 14:
                                # In statistics
                                #   1: total, error
                                #   2: N,NG,Elow (array with Emaxi)
                                #   3: Differential integrated over solid angle
                                #   4: -//- errors
                                #   5: Cumulative integrated over solid angle
                                #   6: -//- errors
                                #   7: Double differential data
                                self.statpos = f.tell()
                                for det in self.detector:
                                        data = unpackArray(fortran.read(f))
                                        det.total = data[0]
                                        det.totalerror = data[1]
                                        for j in range(6):
                                                fortran.skip(f)
                                break
                        elif size != 78: raise IOError("Invalid USRBDX file")

                        # Parse header
                        header = struct.unpack("=i10siiiifiiiffifffif", data)

                        det = Detector()
                        det.nb      = header[ 0]                # mx
                        det.name    = header[ 1].strip().decode()       # titusx
                        det.type    = header[ 2]                # itusbx
                        det.dist    = header[ 3]                # idusbx
                        det.reg1    = header[ 4]                # nr1usx
                        det.reg2    = header[ 5]                # nr2usx
                        det.area    = header[ 6]                # ausbdx
                        det.twoway  = header[ 7]                # lwusbx
                        det.fluence = header[ 8]                # lfusbx
                        det.lowneu  = header[ 9]                # llnusx
                        det.elow    = header[10]                # ebxlow
                        det.ehigh   = header[11]                # ebxhgh
                        det.ne      = header[12]                # nebxbn
                        det.de      = header[13]                # debxbn
                        det.alow    = header[14]                # abxlow
                        det.ahigh   = header[15]                # abxhgh
                        det.na      = header[16]                # nabxbn
                        det.da      = header[17]                # dabxbn

                        self.detector.append(det)

                        if det.lowneu:
                                data = fortran.read(f)
                                det.ngroup = struct.unpack("=i",data[:4])[0]
                                det.egroup = struct.unpack("=%df"%(det.ngroup+1), data[4:])
                        else:
                                det.ngroup = 0
                                det.egroup = []

                        size  = (det.ngroup+det.ne) * det.na * 4
                        if size != fortran.skip(f):
                                raise IOError("Invalid USRBDX file")
                f.close()

        # ----------------------------------------------------------------------
        # Read detector data
        # ----------------------------------------------------------------------
        def readData(self, n):
                """Read n(th) detector data structure"""
                f = open(self.file, "rb")
                fortran.skip(f)
                for i in range(n):
                        fortran.skip(f)         # Detector Header
                        if self.detector[i].lowneu: fortran.skip(f)     # Detector low enetry neutron groups
                        fortran.skip(f)         # Detector data

                fortran.skip(f)         # Detector Header
                if self.detector[n].lowneu: fortran.skip(f)     # Detector low enetry neutron groups
                data = fortran.read(f)  # Detector data
                f.close()
                return data

        # ----------------------------------------------------------------------
        # Read detector statistical data
        # ----------------------------------------------------------------------
        def readStat(self, n):
                """Read n(th) detector statistical data"""
                if self.statpos < 0: return None
                f = open(self.file, "rb")
                f.seek(self.statpos)
                for _ in range(n):
                        for j in range(7):
                                fortran.skip(f) # Detector Data

                for _ in range(6):
                        fortran.skip(f) # Detector Data
                data = fortran.read(f)
                f.close()
                return data

        # ----------------------------------------------------------------------
        def say(self, det=None):
                """print header/detector information"""
                if det is None:
                        self.sayHeader()
                else:
                        det = self.detector[det]
                        say("BDX    : ", det.nb)
                        say("Title  : ", det.name)
                        say("Type   : ", det.type)
                        say("Dist   : ", det.dist)
                        say("Reg1   : ", det.reg1)
                        say("Reg2   : ", det.reg2)
                        say("Area   : ", det.area)
                        say("2way   : ", det.twoway)
                        say("Fluence: ", det.fluence)
                        say("LowNeu : ", det.lowneu)
                        say("Energy : [", det.elow,"..",det.ehigh,"] ne=", det.ne, "de=",det.de)
                        if det.lowneu:
                                say("LOWNeut : [",det.egroup[-1],"..",det.egroup[0],"] ne=",det.ngroup)
                        say("Angle  : [", det.alow,"..",det.ahigh,"] na=", det.na, "da=",det.da)
                        say("Total  : ", det.total, "+/-", det.totalerror)

#===============================================================================
# Usrbin detector
#===============================================================================
class Usrbin(Usrxxx):
        # ----------------------------------------------------------------------
        # Read information from USRBIN file
        # Fill the self.detector structure
        # ----------------------------------------------------------------------
        def readHeader(self, filename):
                """Read USRBIN detector information"""
                f = super().readHeader(filename)

                for _ in range(1000):
                        # Header
                        data = fortran.read(f)
                        if data is None: break
                        size = len(data)

                        # Statistics are present?
                        if size == 14 and data[:10] == b"STATISTICS":
                                self.statpos = f.tell()
                                break
                        elif size != 86: raise IOError("Invalid USRBIN file")

                        # Parse header
                        header = struct.unpack("=i10siiffifffifffififff", data)

                        usrbin = Detector()
                        usrbin.nb    = header[0]
                        usrbin.name  = header[1].strip().decode()
                        usrbin.type  = header[2]
                        usrbin.score = header[3]

                        usrbin.xlow  = float(bmath.format(header[ 4],9))
                        usrbin.xhigh = float(bmath.format(header[ 5],9))
                        usrbin.nx    = header[ 6]
                        if usrbin.nx > 0 and usrbin.type not in (2,12,8,18):
                                usrbin.dx = (usrbin.xhigh-usrbin.xlow) / float(usrbin.nx)
                        else:
                                usrbin.dx = float(bmath.format(header[ 7],9))

                        usrbin.ylow  = float(bmath.format(header[ 8],9))
                        usrbin.yhigh = float(bmath.format(header[ 9],9))
                        if usrbin.type in (1,11):
                                # Round to pi if needed
                                if abs(usrbin.ylow+math.pi) < 1e-6:
                                        usrbin.ylow = -math.pi
                                if abs(usrbin.yhigh-math.pi) < 1e-6:
                                        usrbin.yhigh = math.pi
                                elif abs(usrbin.yhigh-math.pi*2) < 1e-6:
                                        usrbin.yhigh = 2*math.pi
                        usrbin.ny = header[10]
                        if usrbin.ny > 0 and usrbin.type not in (2,12,8,18):
                                usrbin.dy = (usrbin.yhigh-usrbin.ylow) / float(usrbin.ny)
                        else:
                                usrbin.dy = float(bmath.format(header[11],9))

                        usrbin.zlow  = float(bmath.format(header[12],9))
                        usrbin.zhigh = float(bmath.format(header[13],9))
                        usrbin.nz    = header[14]
                        if usrbin.nz > 0 and usrbin.type not in (2,12): # 8=special with z=real
                                usrbin.dz = (usrbin.zhigh-usrbin.zlow) / float(usrbin.nz)
                        else:
                                usrbin.dz = float(bmath.format(header[15],9))

                        usrbin.lntzer = header[16]
                        usrbin.bk     = header[17]
                        usrbin.b2     = header[18]
                        usrbin.tc     = header[19]

                        self.detector.append(usrbin)

                        size  = usrbin.nx * usrbin.ny * usrbin.nz * 4
                        if fortran.skip(f) != size:
                                raise IOError("Invalid USRBIN file")
                f.close()

        # ----------------------------------------------------------------------
        # Read detector data
        # ----------------------------------------------------------------------
        def readData(self, n):
                """Read n(th) detector data structure"""
                f = open(self.file, "rb")
                fortran.skip(f)
                for _ in range(n):
                        fortran.skip(f)         # Detector Header
                        fortran.skip(f)         # Detector data
                fortran.skip(f)                 # Detector Header
                data = fortran.read(f)          # Detector data
                f.close()
                return data

        # ----------------------------------------------------------------------
        # Read data and return a numpy array
        # ----------------------------------------------------------------------
        def readArray(self, n):
                data = unpackArray(self.readData(n))
                dim  = [self.detector[n].nx, self.detector[n].ny, self.detector[n].nz]
                return numpy.reshape(data, dim, order="F")

        # ----------------------------------------------------------------------
        # Read detector statistical data
        # ----------------------------------------------------------------------
        def readStat(self, n):
                """Read n(th) detector statistical data"""
                if self.statpos < 0: return None
                f = open(self.file, "rb")
                f.seek(self.statpos)
                for _ in range(n):
                        fortran.skip(f)         # Detector Data
                data = fortran.read(f)
                f.close()
                return data

        # ----------------------------------------------------------------------
        def say(self, det=None):
                """print header/detector information"""
                if det is None:
                        self.sayHeader()
                else:
                        binning = self.detector[det]
                        say("Bin    : ", binning.nb)
                        say("Title  : ", binning.name)
                        say("Type   : ", binning.type)
                        say("Score  : ", binning.score)
                        say("X      : [", binning.xlow,"-",binning.xhigh,"] x", binning.nx, "dx=",binning.dx)
                        say("Y      : [", binning.ylow,"-",binning.yhigh,"] x", binning.ny, "dy=",binning.dy)
                        say("Z      : [", binning.zlow,"-",binning.zhigh,"] x", binning.nz, "dz=",binning.dz)
                        say("L      : ", binning.lntzer)
                        say("bk     : ", binning.bk)
                        say("b2     : ", binning.b2)
                        say("tc     : ", binning.tc)

#===============================================================================
# MGDRAW output
#===============================================================================
class Mgdraw:
        def __init__(self, filename=None):
                """Initialize a MGDRAW structure"""
                self.reset()
                if filename is None: return
                self.open(filename)

        # ----------------------------------------------------------------------
        def reset(self):
                """Reset information"""
                self.file     = ""
                self.hnd      = None
                self.nevent   = 0
                self.data     = None

        # ----------------------------------------------------------------------
        # Open file and return handle
        # ----------------------------------------------------------------------
        def open(self, filename):
                """Read header information, and return the file handle"""
                self.reset()
                self.file = filename
                try:
                        self.hnd = open(self.file, "rb")
                except IOError:
                        self.hnd = None
                return self.hnd

        # ----------------------------------------------------------------------
        def close(self):
                self.hnd.close()

        # ----------------------------------------------------------------------
        # Read or skip next event from mgread structure
        # ----------------------------------------------------------------------
        def readEvent(self, typeid=None):
                # Read header
                data = fortran.read(self.hnd)
                if data is None: return None
                if len(data) == 20:
                        ndum, mdum, jdum, edum, wdum \
                                = struct.unpack("=iiiff", data)
                else:
                        raise IOError("Invalid MGREAD file")

                self.nevent += 1

                if ndum > 0:
                        if typeid is None or typeid == 0:
                                self.readTracking(ndum, mdum, jdum, edum, wdum)
                        else:
                                fortran.skip(self.hnd)
                        return 0
                elif ndum == 0:
                        if typeid is None or typeid == 1:
                                self.readEnergy(mdum, jdum, edum, wdum)
                        else:
                                fortran.skip(self.hnd)
                        return 1
                else:
                        if typeid is None or typeid == 2:
                                self.readSource(-ndum, mdum, jdum, edum, wdum)
                        else:
                                fortran.skip(self.hnd)
                        return 2

        # ----------------------------------------------------------------------
        def readTracking(self, ntrack, mtrack, jtrack, etrack, wtrack):
                self.ntrack = ntrack
                self.mtrack = mtrack
                self.jtrack = jtrack
                self.etrack = etrack
                self.wtrack = wtrack
                data = fortran.read(self.hnd)
                if data is None: raise IOError("Invalid track event")
                fmt = "=%df" % (3*(ntrack+1) + mtrack + 1)
                self.data = struct.unpack(fmt, data)
                return ntrack

        # ----------------------------------------------------------------------
        def readEnergy(self, icode, jtrack, etrack, wtrack):
                self.icode  = icode
                self.jtrack = jtrack
                self.etrack = etrack
                self.wtrack = wtrack
                data = fortran.read(self.hnd)
                if data is None: raise IOError("Invalid energy deposition event")
                self.data = struct.unpack("=4f", data)
                return icode

        # ----------------------------------------------------------------------
        def readSource(self, ncase, npflka, nstmax, tkesum, weipri):
                self.ncase  = ncase
                self.npflka = npflka
                self.nstmax = nstmax
                self.tkesum = tkesum
                self.weipri = weipri

                data = fortran.read(self.hnd)
                if data is None: raise IOError("Invalid source event")
                fmt = "=" + ("i8f" * npflka)
                self.data = struct.unpack(fmt, data)
                return ncase

#===============================================================================
# Tablis format
#===============================================================================
def tabLis(filename, detector, block=-1):
        f = open(filename,'r')
        raw_data = f.read()                             # read whole file as a single line
        f.close()

        #raw_data = raw_data.split(' # Detector n:  ')  # split in to chunks (detector data)
        #if raw_data[0] == '':
        #       del raw_data[0]                         # delete blank header

        dataset = raw_data.split('\n\n\n')

        if block != -1:
                datablock = dataset[detector].split('\n\n')
                part = io.StringIO(datablock[block])
        else:
                part = io.StringIO(dataset[detector])

        name = part.readline().split()[1]

        # use the fact that it's a file object to make reading the data easy
        x_bin_min, x_bin_max, x_vals, x_err = numpy.loadtxt(part, unpack=True)
        return name, x_bin_min, x_bin_max, x_vals, x_err  # return the columns and detector name

#===============================================================================
# 1D data from tab.lis format
#===============================================================================
#class Data1D:
#       def __init__(self, n, name=None):
#               self.idx   = n
#               self.name  = name
#               self.xlow  = []
#               self.xhigh = []
#               self.value = []
#               self.error = []

#===============================================================================
# Read data from a _tab.lis file
#===============================================================================
class TabLis:
        def __init__(self, filename):
                self.filename = filename

        # ----------------------------------------------------------------------
        def read(self, filename=None): #, onlyheader=True):
                if filename is not None: self.filename = filename

                self.data = []

                try: f = open(self.filename,"r")
                except IOError: return None

                ind     = 1
                half    = 0
                block   = 1
                lastind = 0
                name    = "Detector"

                first = None
                for line in f:
                        #line = line.strip()
                        if line=="\n":
                                half += 1
                                if half == 2:
                                        half = 0
                                        ind += 1
                        elif line.find("#")>=0:
                                m = _detectorPattern.match(line)
                                if m:
                                        name = m.group(1)
                                        p = name.find("(")
                                        if p>0: name = name[:p]
                                        name = name.strip()
                                        entry = "%d %s"%(ind, name)
                                        lastind = ind
                                        if not first:
                                                first = entry
                                        half  = 0
                                        block = 0
                                        continue
                                m = _blockPattern.match(line)
                                if m:
                                        half = 1
                                        continue
                                if lastind != ind:
                                        lastind = ind
                        else:
                                if half == 1:
                                        block += 1
                                half = 0
                f.close()
