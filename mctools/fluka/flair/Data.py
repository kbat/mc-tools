#!/bin/env python
#
# Copyright and User License
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# Copyright Vasilis.Vlachoudis@cern.ch for the
# European Organization for Nuclear Research (CERN)
#
# Please consult the flair documentation for the license
#
# DISCLAIMER
# ~~~~~~~~~~
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, IMPLIED WARRANTIES OF MERCHANTABILITY, OF
# SATISFACTORY QUALITY, AND FITNESS FOR A PARTICULAR PURPOSE
# OR USE ARE DISCLAIMED. THE COPYRIGHT HOLDERS AND THE
# AUTHORS MAKE NO REPRESENTATION THAT THE SOFTWARE AND
# MODIFICATIONS THEREOF, WILL NOT INFRINGE ANY PATENT,
# COPYRIGHT, TRADE SECRET OR OTHER PROPRIETARY RIGHT.
#
# LIMITATION OF LIABILITY
# ~~~~~~~~~~~~~~~~~~~~~~~
# THE COPYRIGHT HOLDERS AND THE AUTHORS SHALL HAVE NO
# LIABILITY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL,
# CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES OF ANY
# CHARACTER INCLUDING, WITHOUT LIMITATION, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES, LOSS OF USE, DATA OR PROFITS,
# OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND ON ANY THEORY
# OF CONTRACT, WARRANTY, TORT (INCLUDING NEGLIGENCE), PRODUCT
# LIABILITY OR OTHERWISE, ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGES.
#
# Author:	Vasilis.Vlachoudis@cern.ch
# Date:	24-Oct-2006

__author__ = "Vasilis Vlachoudis"
__email__  = "Vasilis.Vlachoudis@cern.ch"

import re
import math
import bmath
import struct
import fortran
from log import say

try:
	from cStringIO import StringIO
except ImportError:
	from io import StringIO
try:
	import numpy
except ImportError:
	numpy = None

_detectorPattern = re.compile(r"^ ?# ?Detector ?n?:\s*\d*\s*(.*)\s*", re.MULTILINE)
_blockPattern	 = re.compile(r"^ ?# ?Block ?n?:\s*\d*\s*(.*)\s*",    re.MULTILINE)

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
			self.ncase = long(self.ncase) + long(over1b)*1000000000

		self.title = title.strip()
		self.time  = time.strip()

		return f

	# ----------------------------------------------------------------------
	# Read detector data
	# ----------------------------------------------------------------------
	def readData(self, det):
		"""Read detector det data structure"""
		f = open(self.file,"rb")
		fortran.skip(f)	# Skip header
		for i in range(2*det):
			fortran.skip(f)	# Detector Header & Data
		fortran.skip(f)		# Detector Header
		data = fortran.read(f)
		f.close()
		return data

	# ----------------------------------------------------------------------
	# Read detector statistical data
	# ----------------------------------------------------------------------
	def readStat(self, det):
		"""Read detector det statistical data"""
		if self.statpos < 0: return None
		f = open(self.file,"rb")
		f.seek(self.statpos)
		for i in range(det):
			fortran.skip(f)	# Detector Data
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
		"""Read residual nuclei detector information"""
		f = Usrxxx.readHeader(self, filename)
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

		for i in range(1000):
			# Header
			data = fortran.read(f)
			if data is None: break
			size = len(data)
			self.irrdt = None

			# Statistics are present?
			if size == 14 and data[:8] ==	"ISOMERS:":
				self.nisomers = struct.unpack("=10xi",data)[0]
				data = fortran.read(f)
				data = fortran.read(f)
				size = len(data)

			if size == 14 and data[:10] == "STATISTICS":
				self.statpos = f.tell()
				break

			if size != 38:
				raise IOError("Invalid RESNUCLEi file header size=%d"%(size))

			# Parse header
			header = struct.unpack("=i10siif3i", data)

			det = Detector()
			det.nb	   = header[ 0]
			det.name   = header[ 1].strip()
			det.type   = header[ 2]
			det.region = header[ 3]
			det.volume = header[ 4]
			det.mhigh  = header[ 5]
			det.zhigh  = header[ 6]
			det.nmzmin = header[ 7]

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
		"""Read detector det data structure"""
		f = open(self.file, "rb")
		fortran.skip(f)
		if self.evol:
			fortran.skip(f)

		for i in range(n):
			fortran.skip(f)		# Detector Header & Data
			if self.evol:
				fortran.skip(f)	# TDecay
			fortran.skip(f)		# Detector data
			if self.nisomers:
				fortran.skip(f)	# Isomers header
				fortran.skip(f)	# Isomers data

		fortran.skip(f)			# Detector Header & Data
		if self.evol:
			fortran.skip(f)		# TDecay
		data = fortran.read(f)		# Detector data
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

		for i in range(n):
			fortran.skip(f)		# Detector Header & Data
			if self.evol:
				fortran.skip(f) # TDecay
			fortran.skip(f)		# Detector data
			if self.nisomers:
				fortran.skip(f) # Isomers header
				fortran.skip(f) # Isomers data
		fortran.skip(f)
		if self.evol:
			fortran.skip(f) # TDecay
		fortran.skip(f)		# Detector data
		isohead = fortran.read(f) # Isomers header
		data = fortran.read(f)	  # Isomers data
		#print "isohead:",len(isohead)
		header = struct.unpack("=10xi", isohead)
		#print "isohead:",header[0]
		f.close()
		return (isohead, data)

	# ----------------------------------------------------------------------
	# Read detector statistical data
	# ----------------------------------------------------------------------
	def readStat(self, n):
		"""Read detector det statistical data"""
		if self.statpos < 0: return None
		f = open(self.file,"rb")
		f.seek(self.statpos)

		f.seek(self.statpos)
		if self.nisomers:
			nskip = 7*n
		else:
			nskip = 6*n
		for i in range(nskip):
			fortran.skip(f)	# Detector Data

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
			bin = self.detector[det]
			say("Bin    : ", bin.nb)
			say("Title  : ", bin.name)
			say("Type   : ", bin.type)
			say("Region : ", bin.region)
			say("Volume : ", bin.volume)
			say("Mhigh  : ", bin.mhigh)
			say("Zhigh  : ", bin.zhigh)
			say("NMZmin : ", bin.nmzmin)

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
		f = Usrxxx.readHeader(self, filename)

		for i in range(1000):
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
			if size != 78: raise IOError("Invalid USRBDX file")

			# Parse header
			header = struct.unpack("=i10siiiifiiiffifffif", data)

			det = Detector()
			det.nb	    = header[ 0]		# mx
			det.name    = header[ 1].strip()	# titusx
			det.type    = header[ 2]		# itusbx
			det.dist    = header[ 3]		# idusbx
			det.reg1    = header[ 4]		# nr1usx
			det.reg2    = header[ 5]		# nr2usx
			det.area    = header[ 6]		# ausbdx
			det.twoway  = header[ 7]		# lwusbx
			det.fluence = header[ 8]		# lfusbx
			det.lowneu  = header[ 9]		# llnusx
			det.elow    = header[10]		# ebxlow
			det.ehigh   = header[11]		# ebxhgh 
			det.ne	    = header[12]		# nebxbn
			det.de	    = header[13]		# debxbn
			det.alow    = header[14]		# abxlow
			det.ahigh   = header[15]		# abxhgh
			det.na	    = header[16]		# nabxbn
			det.da	    = header[17]		# dabxbn

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
		"""Read detector n data structure"""
		f = open(self.file, "rb")
		fortran.skip(f)
		for i in range(n):
			fortran.skip(f)		# Detector Header
			if self.detector[i].lowneu: fortran.skip(f)	# Detector low enetry neutron groups
			fortran.skip(f)		# Detector data

		fortran.skip(f)		# Detector Header
		if self.detector[n].lowneu: fortran.skip(f)	# Detector low enetry neutron groups
		data = fortran.read(f)	# Detector data
		f.close()
		return data

	# ----------------------------------------------------------------------
	# Read detector statistical data
	# ----------------------------------------------------------------------
	def readStat(self, n):
		"""Read detector n statistical data"""
		if self.statpos < 0: return None
		f = open(self.file,"rb")
		f.seek(self.statpos)
		for i in range(n):
			for j in range(7):
				fortran.skip(f)	# Detector Data

		for j in range(6):
			fortran.skip(f)	# Detector Data
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
		f = Usrxxx.readHeader(self, filename)

		for i in range(1000):
			# Header
			data = fortran.read(f)
			if data is None: break
			size = len(data)

			# Statistics are present?
			if size == 14 and data[:10] == "STATISTICS":
				self.statpos = f.tell()
				break
			if size != 86: raise IOError("Invalid USRBIN file")

			# Parse header
			header = struct.unpack("=i10siiffifffifffififff", data)

			bin = Detector()
			bin.nb	  = header[ 0]
			bin.name  = header[ 1].strip()
			bin.type  = header[ 2]
			bin.score = header[ 3]

			bin.xlow  = float(bmath.format(header[ 4],9,useD=False))
			bin.xhigh = float(bmath.format(header[ 5],9,useD=False))
			bin.nx	  = header[ 6]
			if bin.nx > 0 and bin.type not in (2,12,8,18):
				bin.dx = (bin.xhigh-bin.xlow) / float(bin.nx)
			else:
				bin.dx = float(bmath.format(header[ 7],9,useD=False))

			if bin.type in (1,11):
				bin.ylow  = -math.pi
				bin.yhigh =  math.pi
			else:
				bin.ylow  = float(bmath.format(header[ 8],9,useD=False))
				bin.yhigh = float(bmath.format(header[ 9],9,useD=False))
			bin.ny	  = header[10]
			if bin.ny > 0 and bin.type not in (2,12,8,18):
				bin.dy = (bin.yhigh-bin.ylow) / float(bin.ny)
			else:
				bin.dy = float(bmath.format(header[11],9,useD=False))

			bin.zlow  = float(bmath.format(header[12],9,useD=False))
			bin.zhigh = float(bmath.format(header[13],9,useD=False))
			bin.nz	  = header[14]
			if bin.nz > 0 and bin.type not in (2,12):	# 8=special with z=real
				bin.dz = (bin.zhigh-bin.zlow) / float(bin.nz)
			else:
				bin.dz = float(bmath.format(header[15],9,useD=False))

			bin.lntzer= header[16]
			bin.bk	  = header[17]
			bin.b2	  = header[18]
			bin.tc	  = header[19]

			self.detector.append(bin)

			size  = bin.nx * bin.ny * bin.nz * 4
			if fortran.skip(f) != size:
				raise IOError("Invalid USRBIN file")
		f.close()

	# ----------------------------------------------------------------------
	# Read detector data
	# ----------------------------------------------------------------------
	def readData(self, n):
		"""Read detector det data structure"""
		f = open(self.file, "rb")
		fortran.skip(f)
		for i in range(n):
			fortran.skip(f)		# Detector Header
			fortran.skip(f)		# Detector data
		fortran.skip(f)		# Detector Header
		data = fortran.read(f)	# Detector data
		f.close()
		return data

	# ----------------------------------------------------------------------
	# Read detector statistical data
	# ----------------------------------------------------------------------
	def readStat(self, n):
		"""Read detector n statistical data"""
		if self.statpos < 0: return None
		f = open(self.file,"rb")
		f.seek(self.statpos)
		for i in range(n):
			fortran.skip(f)	# Detector Data
		data = fortran.read(f)
		f.close()
		return data

	# ----------------------------------------------------------------------
	def say(self, det=None):
		"""print header/detector information"""
		if det is None:
			self.sayHeader()
		else:
			bin = self.detector[det]
			say("Bin    : ", bin.nb)
			say("Title  : ", bin.name)
			say("Type   : ", bin.type)
			say("Score  : ", bin.score)
			say("X	    : [", bin.xlow,"-",bin.xhigh,"] x", bin.nx, "dx=",bin.dx)
			say("Y	    : [", bin.ylow,"-",bin.yhigh,"] x", bin.ny, "dy=",bin.dy)
			say("Z	    : [", bin.zlow,"-",bin.zhigh,"] x", bin.nz, "dz=",bin.dz)
			say("L	    : ", bin.lntzer)
			say("bk     : ", bin.bk)
			say("b2     : ", bin.b2)
			say("tc     : ", bin.tc)

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
	def readEvent(self, type=None):
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
			if type is None or type == 0:
				self.readTracking(ndum, mdum, jdum, edum, wdum)
			else:
				fortran.skip(self.hnd)
			return 0
		elif ndum == 0:
			if type is None or type == 1:
				self.readEnergy(mdum, jdum, edum, wdum)
			else:
				fortran.skip(self.hnd)
			return 1
		else:
			if type is None or type == 2:
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
# 1D data from tab.lis format
#===============================================================================
class Data1D:
	def __init__(self, n, name=None):
		self.idx   = n
		self.name  = name
		self.xlow  = []
		self.xhigh = []
		self.value = []
		self.error = []

#===============================================================================
# Tablis format
#===============================================================================
def tabLis(filename, detector, block=-1):
	f = open(filename,'r')
	raw_data = f.read()				# read whole file as a single line
	f.close()

	#raw_data = raw_data.split(' # Detector n:  ')	# split in to chunks (detector data)
	#if raw_data[0] == '':
	#	del raw_data[0]				# delete blank header

	dataset = raw_data.split('\n\n\n')

	if block != -1:
		datablock = dataset[detector].split('\n\n')
		part = StringIO(datablock[block])
	else:
		part = StringIO(dataset[detector])

	name = part.readline().split()[1]

	# use the fact that it's a file object to make reading the data easy
	x_bin_min, x_bin_max, x_vals, x_err = numpy.loadtxt(part, unpack=True)
	return name, x_bin_min, x_bin_max, x_vals, x_err  # return the columns and detector name

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

		det	= 0
		ind	= 1
		half	= 0
		block	= 1
		lastind = 0

		name  = "Detector"
		blockname = ""
		blockspresent = False

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
					self.det.insert(END, entry)
					lastind = ind
					if not first:
						first = entry
					half  = 0
					block = 0
					blockspresent = False
					continue


				m = _blockPattern.match(line)
				if m:
					blockname = m.group(1)
					blockspresent = True
					half = 1
					continue

				if lastind != ind:
					self.det.insert(END, "%d %s"%(ind,line[1:].strip()))
					lastind = ind

			else:
				if half == 1:
					block += 1
#					if blockname != "":
#						self.det.insert(END, "%d-%d %s %s"%(ind,block,name,blockname))
#						lastind = ind
#					elif not blockspresent:
##						self.det.insert(END, "%d-%d %s ?"%(ind,block,name))
#						lastind = ind
#					blockname = ""
				half = 0
		f.close()
#		if first:
#			self.det.set(first)

#===============================================================================
if __name__ == "__main__":
	import sys
#	say("="*80)
#	mgdraw = Mgdraw("examples/source001_source")
#	while mgdraw.readEvent():
#		say(mgdraw.data)

	say("="*80)
	usr = Usrbdx(sys.argv[1])
	usr.say()
	for i in range(len(usr.detector)):
		say("-"*50)
		usr.say(i)
		data = unpackArray(usr.readData(i))
		stat = unpackArray(usr.readStat(i))
		#say( len(data), len(stat))
		#for j,(d,e) in enumerate(zip(data,stat)):
		#	say(j,d,e)
		#say()

	#usr = Resnuclei(sys.argv[1])
	#usr.say()
	#for i in range(len(usr.detector)):
	#	say("-"*50)
	#	usr.say(i)
	#say("="*80)
	#file = "examples/ex_final001_fort.64"
	#file = "examples/ex_final_resnuclei_64"
	#f = open(file,"rb")
	#while True:
	#	data=fortran.read(f)
	#	size = len(data)
	#	if size==14:
	#		say("Size=",size,data)
	#	else:
	#		say("Size=",size)
	#	if size<0: break
	#f.close()
	#res = Resnuclei(file)
	#res.say()
	#for i in range(len(res.detector)):
	#	say("-"*50)
	#	res.say(i)
#
#	data = res.readData(0)
#	(btotal,bA,beA,bZ,beZ,berr) = res.readStat(0)
#
#	say(len(data))
#	fdata = unpackArray(data)
#	total = unpackArray(btotal)
#	A     = unpackArray(bA)
#	eA    = unpackArray(beA)
#	Z     = unpackArray(bZ)
#	eZ    = unpackArray(beZ)
#	edata = unpackArray(berr)
#
#	del data
#	del btotal, bA, beA, bZ, beZ, berr
#
#	fmin = min([x for x in fdata if x>0.0])
#	fmax = max(fdata)
#	say("Min=",fmin)
#	say("Max=",fmax)
#	say("Tot=",total[0],total[1])
#
#	det = res.detector[0]
#	for z in range(det.zhigh):
#		sum  = 0.0
#		sum2 = 0.0
#		for m in range(det.mhigh):
#			pos = z + m * det.zhigh
#			val = fdata[pos]
#			err = edata[pos]
#			sum  += val
#			sum2 += (val*err)**2
#
#		say("Z=",z+1,"SUM=",sum,math.sqrt(sum2)/sum,"Z=",Z[z],eZ[z])
#
#	say()
#	amax = 2*det.zhigh + det.mhigh + det.nmzmin
#	length = len(fdata)
#	for a in range(1,amax+1):
#		sum = 0.0
#		for z in range(det.zhigh):
#			m = a - 2*z - det.nmzmin - 3
#			pos = z + m * det.zhigh
#			if 0 <= pos < length:
#				sum += fdata[pos]
#
#		say("A=",a,"SUM=",sum,"A=",A[a-1],eA[a-1])
#
#	#for f in fdata:
#	#	say(f)
