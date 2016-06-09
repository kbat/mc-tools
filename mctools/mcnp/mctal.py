#!/usr/bin/python -W all
#
# https://github.com/kbat/mc-tools
#

import sys, re, string, math
import numpy as np

#############################################################################################################################

class Header:
	"""This class contains header information from MCTAL file. We call 'header' what is written from the beginning to the first 'tally' keyword."""

	def __init__(self,verbose=False):
		self.verbose = verbose			# Verbosity flag
		self.kod = ""				# Name of the code, MCNPX
		self.ver = ""				# Code version
		self.probid = np.array((), dtype=str)	# Date and time when the problem was run
		self.knod = 0				# The dump number
		self.nps = 0   				# Number of histories that were run
		self.rnr = 0   				# Number of pseudoradom numbers that were used
		self.title = ""  			# Problem identification line
		self.ntal = 0   			# Number of tallies
		self.ntals = np.array((), dtype=int)	# Array of tally numbers
		self.npert = 0   			# Number of perturbations

	def Print(self):
	        """Prints the class members. Verbose flag on class initialization must be set to True."""

		if self.verbose:

		        print ("\033[1m[HEADER]\033[0m")
		        print ("code:\t\t%s" % self.kod)
	        	print ("version:\t%s" % self.ver)
		        print ("date and time:\t%s" % self.probid)
		        print ("dump number:\t%s" % self.knod)
	        	print ("number of histories:\t%s" % self.nps)
		        print ("number of pseudorandom numbers used:\t%s" % self.rnr)
		        print ("title: %s" % self.title)

		        if self.ntal>1:
				print self.ntal, 'tallies:', self.ntals
	        	else:
				print self.ntal, 'tally:', self.ntals


		        if self.npert != 0:
				print("number of perturbations: %s" % self.npert)

#############################################################################################################################
class Tally:
	"""This class is aimed to store all the information contained in a tally."""

	def __init__(self,tN,verbose=False):
		self.verbose = verbose				# Verbosity flag
		self.tallyNumber = tN				# Tally number
		self.typeNumber = 0				# Particle type number
		self.detectorType = None			# The type of detector tally where 0=none, 1=point, 2=ring, 3=pinhole radiograph,
								#     4=transmitted image radiograph (rectangular grid),
								#     5=transmitted image radiograph (cylindrical grid)
								# When negative, it provides the type of mesh tally
		self.radiograph = False				# Flag set to True is the tally is a radiograph tally.
		self.tallyParticles = np.array((), dtype=int)	# List of 0/1 entries indicating which particle types are used by the tally
		self.tallyComment   = np.array((), dtype=str)	# The FC card lines
		self.nCells = 0					# Number of cell, surface or detector bins
		self.mesh = False				# True if the tally is a mesh tally
		self.meshInfo = np.array([0,1,1,1], dtype=int)	# Mesh binning information in the case of a mesh tally
		self.nDir = 0					# Number of total vs. direct or flagged vs. unflagged bins
		self.nUsr = 0					# Number of user bins
		self.usrTC = None				# Total / cumulative bin in the user bins
		self.nSeg = 0					# Number of segment bins
		self.segTC = None				# Total / cumulative bin in the segment bins
		self.nMul = 0					# Number of multiplier bins
		self.mulTC = None				# Total / cumulative bin in the multiplier bins
		self.nCos = 0					# Number of cosine bins
		self.cosTC = None				# Total / cumulative bin in the cosine bins
		self.cosFlag = 0				# The integer flag of cosine bins
		self.nErg = 0					# Number of energy bins
		self.ergTC = None				# Total / cumulative bin in the energy bins
		self.ergFlag = 0				# The integer flag of energy bins
		self.nTim = 0					# Number of time bins
		self.timTC = None				# Total / cumulative bin in the time bins
		self.timFlag = 0				# The integer flag of time bins

		self.cells = np.array(())			# Array of cell     bin boundaries
		self.usr = np.array(())				# Array of user     bin boundaries
		self.seg = np.array(())				# Array of segments bin boundaries
		self.cos = np.array(())				# Array of cosine   bin boundaries
		self.erg = np.array(())				# Array of energy   bin boundaries
		self.tim = np.array(())				# Array of time     bin boundaries
		self.cora = np.array(())			# Array of cora     bin boundaries for mesh tallies (or lattices)
		self.corb = np.array(())			# Array of corb     bin boundaries for mesh tallies (or lattices)
		self.corc = np.array(())			# Array of corc     bin boundaries for mesh tallies (or lattices)

		self.tfc_jtf = np.array(())			# List of numbers in the tfc line
		self.tfc_dat = []				# Tally fluctuation chart data (NPS, tally, error, figure of merit)

		self.detectorTypeList = { -6 : "smesh"                , -5 : "cmesh"                                          , -4 : "rmesh"                 ,
					   # The line below duplicates the line above with short names for tally naming during conversion.
					   # See the function getDetectorType to see how this information is used
					  -3 : "Spherical mesh tally" , -2 : "Cylindrical mesh tally"                         , -1 : "Rectangular mesh tally",
					   0 : "None"                 ,  1 : "Point"                                          ,  2 : "Ring"                  ,
					   3 : "Pinhole radiograph"   ,  4 : "Transmitted image rdiograph (rectangular grid)" ,  5 : "Transmitted image radiograph (cylindrical grid)",
					   # The line below duplicates the line above, with short names for tally naming during conversion.
					   # See the function getDetectorType to see how this information is used
					   6 : "pi"                   ,  7 : "tir"                                            ,  8 : "tic" }

		self.particleListShort = { 1 : "Neutron"                     , 2 : "Photon"             , 3 : "Neutron + Photon"  , 
					   4 : "Electron"                    , 5 : "Neutron + Electron" , 6 : "Photon + Electron" ,
					   7 : "Neutron + Photon + Electron"  }

				     #1                2               3               4               5              6                     7
		self.particleList = ("Neutron"      , "Photon"      , "Electron"    , "Muon"        , "Tau"        , "Electron Neutrino" , "Muon Neutrino" ,
				     #8                9               10              11              12             13                    14
				     "Tau Neutrino" , "Proton"      , "Lambda 0"    , "Sigma +"     , "Sigma -"    , "Cascade 0"         , "Cascade -"     ,
				     #15               16              17              18              19             20                    21
				     "Omega -"      , "Lambda c +"  , "Cascade c +" , "Cascade c 0" , "Lambda b 0" , "Pion +"            , "Neutral Pion"  ,
				     #22               23              24              25              26             27                    28
				     "Kaon +"       , "K0 Short"    , "K0 Long"     , "D +"         , "D 0"        , "D s +"             , "B +"           ,
				     #29               30              31              32              33             34                    35
				     "B 0"          , "B s 0"       , "Deuteron"    , "Triton"      , "He3"        , "He4 (Alpha)"       , "Heavy ions")


		self.binIndexList = ("f","d","u","s","m","c","e","t","i","j","k")

		self.isInitialized = False
		self.valsErrors = None       # Array of values and errors

	def initializeValuesVectors(self):
		"""This function initializes the 9-D matrix for the storage of values and errors."""

		nCells = self.getNbins("f")
		nCora  = self.getNbins("i")
		nCorb  = self.getNbins("j")
		nCorc  = self.getNbins("k")
		nDir   = self.getNbins("d")
		nUsr   = self.getNbins("u")
		nSeg   = self.getNbins("s")
		nMul   = self.getNbins("m")
		nCos   = self.getNbins("c")
		nErg   = self.getNbins("e")
		nTim   = self.getNbins("t")

		self.valsErrors = np.empty( ( nCells , nDir , nUsr , nSeg , nMul , nCos , nErg , nTim , nCora , nCorb , nCorc , 2 ) , dtype=float)

		#self.valsErrors = [[[[[[[[[[[[[] for _ in xrange(2)]    for _ in xrange(nCorc)] for _ in xrange(nCorb)] for _ in xrange(nCora)] for _ in xrange(nTim)] 
		#				 for _ in xrange(nErg)] for _ in xrange(nCos)]  for _ in xrange(nMul)]  for _ in xrange(nSeg)]  for _ in xrange(nUsr)] 
		#				 for _ in xrange(nDir)] for _ in xrange(nCells)]

		self.isInitialized = True
		

	def Print(self, option=[]):
		"""Tally printer. Options: title. Verbose flag on class initialization must be set to True."""

		if self.verbose:
			print ("\033[1m[TALLY]\033[0m")
			print ("Tally Number: %5d" % self.tallyNumber)
			print ("Tally comment(s):")
			for comment in self.tallyComment:
				print ("\t%s" % comment)
			mt = "Yes" if self.mesh else "No"
			print ("Mesh tally: %s" % mt )
			rt = "Yes" if self.radiograph else "No"
			print ("Radiograph Tally: %s" % rt)
			print ("Detector type: %s" % self.getDetectorType())
			print ("List of particles in tally:")
			for i,name in enumerate(self.getTallyParticles()):
				print ("\t%2d - %s" % (i+1,name))
			if not self.mesh:
				print ("Number of cells/point detectors/surfaces/macrobodies: %5d" % self.getNbins("f"))
			else:
				mesh_tot = self.getNbins("i")*self.getNbins("j")*self.getNbins("k")

				print ("Number of mesh tally bins: %5d" % mesh_tot)
				print ("\tNumber of CORA bins: %5d" % self.getNbins("i"))
				print ("\tNumber of CORB bins: %5d" % self.getNbins("j"))
				print ("\tNumber of CORC bins: %5d" % self.getNbins("k"))
			print ("Number of tot vs. dir or flag vs. unflag bins: %5d" % self.getNbins("d"))
			print ("Number of user bins: %5d" % self.getNbins("u"))
			print ("Number of segments: %5d" % self.getNbins("s"))
			print ("Number of multipliers: %5d" % self.getNbins("m"))
			print ("Number of cosine bins: %5d" % self.getNbins("c"))
			print ("Number of energy bins: %5d" % self.getNbins("e"))
			print ("Number of time bins: %5d" % self.getNbins("t"))

			print ("Total values in the tally: %8d" % self.getTotNumber(False))

	

	def getDetectorType(self,short=False):
		"""Returns the type of the detector type used in the tally."""

		if not short:
			return self.detectorTypeList[self.detectorType]
		elif short and self.radiograph:
			return self.detectorTypeList[self.detectorType + 3]
		elif short and self.mesh:
			return self.detectorTypeList[self.detectorType - 3]

	def getTallyParticles(self):
		"""Returns the particles used in the tally. References can be found in Table 4-1 and page B-2 of the MCNPX manual."""

		particleNames = []

		if self.typeNumber > 0:
			particleNames.append(particleListShort[self.typeNumber]) 
		else:
			for i,name in enumerate(self.particleList):
				try:
					if self.tallyParticles[i] == 1:
						particleNames.append(self.particleList[i])
				except:
					pass # For some reasons there can be less than 35 particles listed. Skip in case.
		return particleNames
				

	def getTotNumber(self,includeTotalBin=True):
		"""Return the total number of bins."""

		nCells = self.getNbins("f",includeTotalBin)
		nCora  = self.getNbins("i",includeTotalBin)
		nCorb  = self.getNbins("j",includeTotalBin)
		nCorc  = self.getNbins("k",includeTotalBin)
		nDir   = self.getNbins("d",includeTotalBin)
		nUsr   = self.getNbins("u",includeTotalBin)
		nSeg   = self.getNbins("s",includeTotalBin)
		nMul   = self.getNbins("m",includeTotalBin)
		nCos   = self.getNbins("c",includeTotalBin)
		nErg   = self.getNbins("e",includeTotalBin)
		nTim   = self.getNbins("t",includeTotalBin)
                
                tot = nCells * nDir * nUsr * nSeg * nMul * nCos * nErg * nTim * nCora * nCorb * nCorc

                return tot

	def insertCell(self,cN):
		"""Insert cell number."""

		if len(self.cells) <= self.nCells:
			self.cells = np.append(self.cells, cN)
			return True 
		else:
			return False

	def insertCorBin(self,axis,value):
		"""Insert cora/b/c values."""

		if axis == 'a':
			if len(self.cora) <= self.meshInfo[1]+1:
				self.cora = np.append(self.cora, value)
				return True
			else:
				return False
		if axis == 'b':
			if len(self.corb) <= self.meshInfo[2]+1:
				self.corb = np.append(self.corb, value)
				return True
			else:
				return False

		if axis == 'c':
			if len(self.corc) <= self.meshInfo[3]+1:
				self.corc = np.append(self.corc, value)
				return True
			else:
				return False

	def insertUsr(self,uB):
		"""Insert usr bins."""

		if len(self.usr) <= self.nUsr:
			self.usr = np.append(self.usr, uB)
			return True
		else:
			return False

	def insertSeg(self,sB):
		"""Insert seg bins."""

		if len(self.seg) <= self.nSeg:
			self.seg = np.append(self.seg, sB)
			return True
		else:
			return False

	def insertCos(self,cB):
		"""Insert cosine bin."""

		if len(self.cos) <= self.nCos:
			self.cos = np.append(self.cos, cB)
			return True
		else:
			return False

	def insertRadiograph(self,axis,rB):
		"""Insert radiograph coordinates on s and t-axis."""

		if axis == "s":
			if len(self.seg) <= self.nSeg+1:
				self.seg = np.append(self.seg, rB)
				return True
			else:
				return False

		if axis == "t":
			if len(self.cos) <= self.nCos+1:
				self.cos = np.append(self.cos,rB)
				return True
			else:
				return False

	def insertErg(self,eB):
		"""Insert energy bin."""

		if len(self.erg) <= self.nErg:
			self.erg = np.append(self.erg, eB)
			return True
		else:
			return False

	def insertTim(self,tB):
		"""Insert time bin."""

		if len(self.tim) <= self.nTim:
			self.tim = np.append(self.tim, tB)
			return True
		else:
			return False

	def insertTfcJtf(self,jtf):
		"""Insert TFC jtf list."""

		if len(jtf) == 9:
			self.tfc_jtf = jtf
			return True
		else:
			return False

	def insertTfcDat(self,dat):
		"""Insert TFC values."""

		if len(dat) <= 4:
			self.tfc_dat.append(dat)
			return True
		else:
			return False

	def insertValue(self,c,d,u,s,m,a,e,t,f,i,j,k,val):
		"""Insert tally value."""

		if self.isInitialized == False:
			self.initializeValuesVectors()

		self.valsErrors[c][d][u][s][m][a][e][t][f][i][j][k] = val

	def getValue(self,f,d,u,s,m,c,e,t,i,j,k,v):
		"""Return a value from tally."""

		return self.valsErrors[f][d][u][s][m][c][e][t][i][j][k][v]

	def getAxis(self,axis):
		"""Returns an array containing the values of the axis bins. The desired axis is set by passing the corresponding letter as a function argument. The corrspondence is the usual defined in MCNPX manual (u,s,c,e,t) for the standard and (i,j,k) for mesh tallies axes (namely cora/b/c)."""

		if axis == "u":
			if len(self.usr) != 0:
				return np.append([0], self.usr)

		if axis == "s":
			if len(self.seg) != 0:
				if self.radiograph:
					return self.seg
				else:
					first = self.seg[0] - 1.
					return np.append([first], self.seg)

		if axis == "c":
			if len(self.cos) != 0:
				if self.radiograph:
					return self.cos
				else:
					first = -1.
					return np.append([first], self.cos)

		if axis == "e":
			if len(self.erg) != 0:
				first = self.erg[0] - 1.
				return np.append([first], self.erg)

		if axis == "t":
			if len(self.tim) != 0:
				first = self.tim[0] - 1.
				return np.append([first], self.tim)

		if axis == "i":
			return self.cora

		if axis == "j":
			return self.corb

		if axis == "k":
			return self.corc

		return []

	def getNbins(self,axis,includeTotalBin = True):
		"""Returns the number of bins relative to the desired axis. The correspondence is, as usual, (f,d,u,s,m,c,e,t) for standard 8D data, plus (i,j,k) for mesh tallies."""

		if axis == "f":
			nCells = 1 if self.nCells == 0 else self.nCells
			return nCells

		if axis == "i":
			return self.meshInfo[1]

		if axis == "j":
			return self.meshInfo[2]

		if axis == "k":
			return self.meshInfo[3]

		if axis == "d":
			nDir = 1 if self.nDir == 0 else self.nDir
			return nDir

		if axis == "u":
			nUsr = 1 if self.nUsr == 0 else self.nUsr
			nUsr = nUsr - 1 if self.usrTC == "t" and not includeTotalBin else nUsr
			return nUsr

		if axis == "s":
			nSeg = 1 if self.nSeg == 0 else self.nSeg
			nSeg = nSeg - 1 if self.segTC == "t" and not includeTotalBin else nSeg
			return nSeg

		if axis == "m":
			nMul = 1 if self.nMul == 0 else self.nMul
			nMul = nMul - 1 if self.mulTC == "t" and not includeTotalBin else nMul
			return nMul

		if axis == "c":
			nCos = 1 if self.nCos == 0 else self.nCos
			nCos = nCos - 1 if self.cosTC == "t" and not includeTotalBin else nCos
			return nCos

		if axis == "e":
			nErg = 1 if self.nErg == 0 else self.nErg
			nErg = nErg - 1 if self.ergTC == "t" and not includeTotalBin else nErg
			return nErg

		if axis == "t":
			nTim = 1 if self.nTim == 0 else self.nTim
			nTim = nTim - 1 if self.timTC == "t" and not includeTotalBin else nTim
			return nTim

#############################################################################################################################

class MCTAL:
	"""This class parses the whole MCTAL file."""

	def __init__(self,fname,verbose=False):
		self.verbose = verbose
		self.tallies = []
		self.thereAreNaNs = False
		self.header = Header(verbose)
		self.mctalFileName = fname
		self.mctalFile = open(self.mctalFileName, "r")
		self.line = None # This variable will contain the read lines one by one, but it is
		                 # important to keep it global because the last value from getHeaders()
				 # must be already available as first value for parseTally(). This will
				 # also apply to successive calls to parseTally().

	def Read(self):
		"""This function calls the functions getHeaders and parseTally in order to read the entier MCTAL file."""

		if self.verbose:
			print "\n\033[1;34m[Parsing file: %s...]\033[0m" % self.mctalFileName

		self.getHeaders()
		self.getTallies()

		if self.thereAreNaNs and self.verbose:
			print >> sys.stderr, "\n \033[1;30mThe MCTAL file contains one or more tallies with NaN values. Flagged.\033[0m\n"

		self.mctalFile.close()
		return self.tallies

	def getHeaders(self):
		"""This function reads the first lines from the MCTAL file. We call "header" what is written from the beginning to the first "tally" keyword."""

		self.line = self.mctalFile.readline().split()

		if len(self.line) == 7:
			self.header.kod = self.line[0]
			self.header.ver = self.line[1]
			pID_date = self.line[2]
			self.header.probid = np.append(self.header.probid, pID_date)
			pID_time = self.line[3]
			self.header.probid = np.append(self.header.probid, pID_time)
			self.header.knod = int(self.line[4])
			self.header.nps = int(self.line[5])
			self.header.rnr = int(self.line[6])
		elif len(self.line) == 3:
			self.header.knod = int(self.line[0])
			self.header.nps = int(self.line[1])
			self.header.rnr = int(self.line[2])
			

		self.header.title = self.mctalFile.readline().strip()

		self.line = self.mctalFile.readline().split()

		self.header.ntal = int(self.line[1])

		if self.header.ntal == 0:
			print >> sys.stderr, "\n \033[1;31mNo tallies in this MCTAL file. Exiting.\033[0m\n"
			sys.exit(1)

		if len(self.line) == 4:
			self.header.npert = int(self.line[3])
			print >> sys.stderr, "\n \033[1;31mMCTAL file with perturbation card. Not supported. Exiting.\033[0m\n"
			sys.exit(1)

		self.line = self.mctalFile.readline().split()

		while self.line[0].lower() != "tally":
			for l in self.line: self.header.ntals = np.append(self.header.ntals,int(l))
			self.line = self.mctalFile.readline().split()

	def getTallies(self):
		"""This function supervises the calls to parseTally() function. It will keep track of the position of cursor in the MCTAL file and stop execution when EOF is reached."""

		EOF = False

		while not EOF:
			EOF = self.parseTally()

	def parseTally(self):
		"""This function parses an entire tally."""

		# The first line processed by this function is already in memory, either coming from the
		# last readline() in Header class or from the previous call to parseTally()

		tally = Tally(int(self.line[1]),self.verbose)

		if self.verbose:
			print " \033[33mParsing tally: %5d\033[0m" % (tally.tallyNumber)

		tally.typeNumber = int(self.line[2])
		if len(self.line) == 4: tally.detectorType = int(self.line[3])

		if tally.detectorType >=  3: tally.radiograph = True
                # check for None is needed for MCNP6 and F1 tally
		if tally.detectorType is not None and tally.detectorType <= -1:
                        tally.mesh = True

		self.line = self.mctalFile.readline()
		line = self.line.split() # I must use this trick because some MCTAL files seem to omit
					 # the particle list and the code must be compatible with the 
					 # following part even if this line is missing, but I don't have
					 # the possibility to know in advance, so I must duplicate the
					 # read line.

		for p in line:
			if p.isdigit():
				v = int(p)
				tally.tallyParticles = np.append(tally.tallyParticles, v)

		if len(tally.tallyParticles) != 0: self.line = self.mctalFile.readline()

		while self.line[0].lower() != "f":
			tally.tallyComment = np.append(tally.tallyComment, self.line[5:].rstrip())
			self.line = self.mctalFile.readline()

		self.line = self.line.split()

		if not tally.mesh:
			tally.nCells = int(self.line[1])
		else:
			tally.nCells = 1
			tally.meshInfo[0] = int(self.line[2]) # Unknown number
			tally.meshInfo[1] = int(self.line[3]) # number of cora bins
			tally.meshInfo[2] = int(self.line[4]) # number of corb bins
			tally.meshInfo[3] = int(self.line[5]) # number of corc bins

		self.line = self.mctalFile.readline()

		i = 0
		axisNumber = 0
		axisName = ('a','b','c')
		corsVals = (tally.meshInfo[1], tally.meshInfo[2], tally.meshInfo[3]) 

		while self.line[0].lower() != "d": # CELLS
			if tally.mesh:
				for c in self.line.split():
					if not tally.insertCorBin(axisName[axisNumber],float(c)):
						raise IOError("Too many cells in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
					i = i + 1
					if i == (corsVals[axisNumber] + 1):
						axisNumber = axisNumber + 1
						i = 0
			elif "." in self.line and "E" not in self.line:
				for c in self.line.split():
					if not tally.insertCell(float(c)):
					        raise IOError("Too many cells in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
			else:
				for c in self.line.split():
					if not tally.insertCell(int(c)):  # This means that for some reason you are trying to
                                					  # insert more cells than the number stated in f
					        raise IOError("Too many cells in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))

			self.line = self.mctalFile.readline()

		# DIR
		self.line = self.line.split()
		tally.nDir = int(self.line[1])

		while self.line[0].lower() != "u":
			self.line = self.mctalFile.readline()

		# USR
		self.line = self.line.split()
		if self.line[0].lower() == "ut": tally.usrTC = "t"
		if self.line[0].lower() == "uc": tally.usrTC = "c"
		tally.nUsr = int(self.line[1])

		# USR BINS
		self.line = self.mctalFile.readline()
		while self.line[0].lower() != "s":
			for u in self.line.split():
				if not tally.insertUsr(float(u)):
					raise IOError("Too many user bins in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
			self.line = self.mctalFile.readline()

		# SEG
		self.line = self.line.split()
		if self.line[0].lower() == "st": tally.segTC = "t"
		if self.line[0].lower() == "sc": tally.segTC = "c"
		tally.nSeg = int(self.line[1])

		# SEGMENT BINS
		self.line = self.mctalFile.readline()
		while self.line[0].lower() != "m":
			for s in self.line.split():
				if tally.radiograph:
					if not tally.insertRadiograph("s",float(s)):
						raise IOError("Too many segment bins in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
				else:
					if not tally.insertSeg(float(s)):
						raise IOError("Too many segment bins in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
			self.line = self.mctalFile.readline()

		# MUL
		self.line = self.line.split()
		if self.line[0].lower() == "mt": tally.mulTC = "t"
		if self.line[0].lower() == "mc": tally.mulTC = "c"
		tally.nMul = int(self.line[1])

		while self.line[0].lower() != "c":
			self.line = self.mctalFile.readline()

		# COS
		self.line = self.line.split()
		if self.line[0].lower() == "ct": tally.cosTC = "t"
		if self.line[0].lower() == "cc": tally.cosTC = "c"
		tally.nCos = int(self.line[1])
		if len(self.line) == 3: tally.cosFlag = int(self.line[2])

		# COSINE BINS
		self.line = self.mctalFile.readline()
		while self.line[0].lower() != "e":
			for c in self.line.split():
				if tally.radiograph:
					if not tally.insertRadiograph("t",float(c)):
						raise IOError("Too many cosine bins in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
				else:
					if not tally.insertCos(float(c)):
						raise IOError("Too many cosine bins in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
			self.line = self.mctalFile.readline()

		# ERG
		self.line = self.line.split()
		if self.line[0].lower() == "et": tally.ergTC = "t"
		if self.line[0].lower() == "ec": tally.cosTC = "c"
		tally.nErg = int(self.line[1])
		if len(self.line) == 3: tally.ergFlag = int(self.line[2])

		# ENERGY BINS
		self.line = self.mctalFile.readline()
		while self.line[0].lower() != "t":
			for e in self.line.split():
				if not tally.insertErg(float(e)):
					raise IOError("Too many energy bins in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
			self.line = self.mctalFile.readline()

		# TIM
		self.line = self.line.split()
		if self.line[0].lower() == "tt": tally.timTC = "t"
		if self.line[0].lower() == "tc": tally.timTC = "c"
		tally.nTim = int(self.line[1])
		if len(self.line) == 3: tally.timFlag = int(self.line[2])

		# TIME BINS
		self.line = self.mctalFile.readline()
		while self.line.strip().lower() != "vals":
			for t in self.line.split():
				if not tally.insertTim(float(t)):
					raise IOError("Too many time bins in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))
			self.line = self.mctalFile.readline()

		# VALS
		f = 1
		Fld = []
		nFld = 0
		tally.initializeValuesVectors()

		nCells = tally.getNbins("f")
		nCora  = tally.getNbins("i")
		nCorb  = tally.getNbins("j")
		nCorc  = tally.getNbins("k")
		nDir   = tally.getNbins("d")
		nUsr   = tally.getNbins("u")
		nSeg   = tally.getNbins("s")
		nMul   = tally.getNbins("m")
		nCos   = tally.getNbins("c")
		nErg   = tally.getNbins("e")
		nTim   = tally.getNbins("t")

		for c in xrange(nCells):
			for d in xrange(nDir):
				for u in xrange(nUsr):
					for s in xrange(nSeg):
						for m in xrange(nMul):
							for a in xrange(nCos): # a is for Angle...forgive me
								for e in xrange(nErg):
									for t in xrange(nTim):
										for k in xrange(nCorc):
											for j in xrange(nCorb):
												for i in xrange(nCora):
													if (f > nFld): # f is for Field...again, forgive me
														del Fld
														del self.line
														self.line = self.mctalFile.readline().strip()
														Fld = self.line.split()
														nFld = len(Fld) - 1
														f = 0

													if self.line[0:3] != "tfc":
														if math.isnan(float(Fld[f])) or math.isnan(float(Fld[f+1])):
															self.thereAreNaNs = True
														tally.insertValue(c,d,u,s,m,a,e,t,i,j,k,0,float(Fld[f]))
														tally.insertValue(c,d,u,s,m,a,e,t,i,j,k,1,float(Fld[f+1]))

														f += 2

		del Fld

		if tally.mesh == False:
			# TFC JTF
			self.line = self.mctalFile.readline().strip().split()
			if self.line[0] != "tfc":
				raise IOError("There seem to be more values than expected in tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))

			del self.line[0]
			self.line = [int(i) for i in self.line]

			if not tally.insertTfcJtf(self.line):
				raise IOError("Wrong number of TFC jtf elements.")


			# TFC DAT
			self.line = self.mctalFile.readline().strip()
			while "tally" not in self.line and len(self.line) != 0:
				if "kcode" in self.line:
					print >> sys.stderr, "\n \033[1;31m Tally with KCODE card. Not supported. Exiting.\033[0m\n"
					sys.exit(1)

				self.line = self.line.split()
			
				tfcDat = []

				tfcDat.append(int(self.line[0]))
				if math.isnan(float(self.line[1])) or math.isnan(float(self.line[2])):
					self.thereAreNaNs = True
				tfcDat.append(float(self.line[1]))
				tfcDat.append(float(self.line[2]))
				if len(self.line) == 4:
					if math.isnan(float(self.line[1])):
						self.thereAreNaNs = True
					tfcDat.append(float(self.line[3]))
					
				if not tally.insertTfcDat(tfcDat):
					raise IOError("Wrong number of elements in TFC data line in the tally n. %d of %s" % (tally.tallyNumber, self.mctalFileName))

				self.line = self.mctalFile.readline().strip()

		else:
			while "tally" not in self.line and len(self.line) != 0:
				self.line = self.mctalFile.readline().strip()


		self.tallies.append(tally)

		if self.line == "":
			self.line = self.line
			return True
		elif "tally" in self.line:
			self.line = self.line.split()
			return False
