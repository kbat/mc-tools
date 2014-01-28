#!/usr/bin/python -W all
#
# mctal reading script by Nicolo' Borghi
# Started on 04/12/2013 at ESS Lund
# based on scripts developed by the author,
# Dr. Gallmeier and Dr. Batkov
#
#

import sys, re, string, math
from array import array

#############################################################################################################################

class Header:
	"""This class contains header information from MCTAL file. We call 'header' what is written from the beginning to the first 'tally' keyword."""

	def __init__(self,verbose=False):
		self.verbose = verbose  # Verbosity flag
		self.kod = ""  		# Name of the code, MCNPX
		self.ver = ""  		# Code version
		self.probid = []	# Date and time when the problem was run
		self.knod = 0   	# The dump number
		self.nps = 0   		# Number of histories that were run
		self.rnr = 0   		# Number of pseudoradom numbers that were used
		self.title = ""  	# Problem identification line
		self.ntal = 0   	# Number of tallies
		self.ntals = []		# Array of tally numbers
		self.npert = 0   	# Number of perturbations

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
		self.verbose = verbose     # Verbosity flag
		self.tallyNumber = tN      # Tally number
		self.typeNumber = 0        # Particle type number
		self.detectorType = None   # The type of detector tally where 0=none, 1=point, 2=ring, 3=pinhole radiograph,
                                           #     4=transmitted image radiograph (rectangular grid),
                                           #     5=transmitted image radiograph (cylindrical grid)
					   # When negative, it provides the type of mesh tally
		self.tallyParticles = []   # List of 0/1 entries indicating which particle types are used by the tally
		self.tallyComment = []     # The FC card lines
		self.nCells = 0            # Number of cell, surface or detector bins
		self.mesh = False          # True if the tally is a mesh tally
		self.meshInfo = [0,1,1,1]  # Mesh binning information in the case of a mesh tally
		self.nDir = 0              # Number of total vs. direct or flagged vs. unflagged bins
		self.nUsr = 0              # Number of user bins
		self.usrTC = None          # Total / cumulative bin in the user bins
		self.nSeg = 0              # Number of segment bins
		self.segTC = None          # Total / cumulative bin in the segment bins
		self.nMul = 0              # Number of multiplier bins
		self.mulTC = None          # Total / cumulative bin in the multiplier bins
		self.nCos = 0              # Number of cosine bins
		self.cosTC = None          # Total / cumulative bin in the cosine bins
		self.cosFlag = 0           # The integer flag of cosine bins
		self.nErg = 0              # Number of energy bins
		self.ergTC = None          # Total / cumulative bin in the energy bins
		self.ergFlag = 0           # The integer flag of energy bins
		self.nTim = 0              # Number of time bins
		self.timTC = None          # Total / cumulative bin in the time bins
		self.timFlag = 0           # The integer flag of time bins

		self.cells = []            # Array of cell   bin boundaries
		self.usr = []              # Array of user   bin boundaries
		self.cos = []              # Array of cosine bin boundaries
		self.erg = []              # Array of energy bin boundaries
		self.tim = []              # Array of time   bin boundaries
		self.cora = []		   # Array of cora   bin boundaries for mesh tallies (or lattices)
		self.corb = []		   # Array of corb   bin boundaries for mesh tallies (or lattices)
		self.corc = []		   # Array of corc   bin boundaries for mesh tallies (or lattices)

		self.tfc_jtf = []          # List of numbers in the tfc line
		self.tfc_dat = []          # Tally fluctuation chart data (NPS, tally, error, figure of merit)
		
		self.binIndexList = ("f","d","u","s","m","c","e","t","i","j","k")

		self.isInitialized = False
		self.valsErrors = []       # Array of values and errors

		#self.thereAreNaNs = False # If some of values, errors or TFC data are NaN, the tally will be saved with
					   # this flag set to true. The reading tests will not fail and in the conversion
					   # script nbmctal2root.py this flag will be used to skip the conversion of the
					   # tally


	def initializeValuesVectors(self):
		"""This function initializes the 9-D matrix for the storage of values and errors."""

                nCells = self.nCells
                if self.nCells == 0: nCells = 1
		nCora = self.meshInfo[1]
		nCorb = self.meshInfo[2]
		nCorc = self.meshInfo[3]
                nDir = self.nDir
                if self.nDir   == 0: nDir   = 1
                nUsr = self.nUsr
                if self.nUsr   == 0: nUsr   = 1
                nSeg = self.nSeg
                if self.nSeg   == 0: nSeg   = 1
                nMul = self.nMul
                if self.nMul   == 0: nMul   = 1
                nCos = self.nCos
                if self.nCos   == 0: nCos   = 1
                nErg = self.nErg
                if self.nErg   == 0: nErg   = 1
                nTim = self.nTim
                if self.nTim   == 0: nTim   = 1

		self.valsErrors = [[[[[[[[[[[[[] for _ in range(2)] for _ in range(nCorc)] for _ in range(nCorb)] for _ in range(nCora)] for _ in range(nTim)] for _ in range(nErg)] for _ in range(nCos)] for _ in range(nMul)] for _ in range(nSeg)] for _ in range(nUsr)] for _ in range(nDir)] for _ in xrange(nCells)]

		self.isInitialized = True
		

	def Print(self, option=[]):
		"""Tally printer. Options: title. Verbose flag on class initialization must be set to True."""

		if self.verbose:
			print "To be implemented. Not essential for now.\n"

	def getTotNumber(self):
		"""Return the total number of bins."""

                nCells = self.nCells
                if self.nCells == 0: nCells = 1
		nCora = self.meshInfo[1]
		nCorb = self.meshInfo[2]
		nCorc = self.meshInfo[3]
                nDir = self.nDir
                if self.nDir   == 0: nDir   = 1
                nUsr = self.nUsr
                if self.nUsr   == 0: nUsr   = 1
                nSeg = self.nSeg
                if self.nSeg   == 0: nSeg   = 1
                nMul = self.nMul
                if self.nMul   == 0: nMul   = 1
                nCos = self.nCos
                if self.nCos   == 0: nCos   = 1
                nErg = self.nErg
                if self.nErg   == 0: nErg   = 1
                nTim = self.nTim
                if self.nTim   == 0: nTim   = 1
                
                tot = nCells * nDir * nUsr * nSeg * nMul * nCos * nErg * nTim * nCora * nCorb * nCorc

                return tot

	def insertCell(self,cN):
		"""Insert cell number."""

		if len(self.cells) <= self.nCells:
			self.cells.append(cN)
			return True 
		else:
			return False

	def insertCorBin(self,axis,value):
		"""Insert cora/b/c values."""

		if axis == 'a':
			if len(self.cora) <= self.meshInfo[1]+1:
				self.cora.append(value)
				return True
			else:
				return False
		if axis == 'b':
			if len(self.corb) <= self.meshInfo[2]+1:
				self.corb.append(value)
				return True
			else:
				return False

		if axis == 'c':
			if len(self.corc) <= self.meshInfo[3]+1:
				self.corc.append(value)
				return True
			else:
				return False

	def insertUsr(self,uB):
		"""Insert usr bins."""

		if len(self.usr) <= self.nUsr:
			self.usr.append(uB)
			return True
		else:
			return False

	def insertCos(self,cB):
		"""Insert cosine bin."""

		if len(self.cos) <= self.nCos:
			self.cos.append(cB)
			return True
		else:
			return False

	def insertErg(self,eB):
		"""Insert energy bin."""

		if len(self.erg) <= self.nErg:
			self.erg.append(eB)
			return True
		else:
			return False

	def insertTim(self,tB):
		"""Insert time bin."""

		if len(self.tim) <= self.nTim:
			self.tim.append(tB)
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
		"""Returns an array containing the values of the axis bins. The desired axis is set by passing the corresponding letter as a function argument. The corrspondence is the usual defined in MCNPX manual (u,c,e,t) for the standard and (i,j,k) for mesh tallies axes (namely cora/b/c)."""

		if axis == "u":
			if len(self.usr) != 0:
				u = [0] + self.usr
				return array('d',u)

		if axis == "c":
			if len(self.cos) != 0:
				c = [-1.5] + self.cos
				return array('d',c)

		if axis == "e":
			if len(self.erg) != 0:
				e = [0] + self.erg
				return array('d',e)

		if axis == "t":
			if len(self.tim) != 0:
				t = [0] + self.tim
				return array('d',t)

		if axis == "i":
			return array('d',self.cora)

		if axis == "j":
			return array('d',self.corb)

		if axis == "k":
			return array('d',self.corc)

		return []

	def getNbins(self,axis):
		"""Returns the number of bins relative to the desired axis. The correspondence is, as usual, (f,d,u,s,m,c,e,t) for standard 8D data, plus (i,j,k) for mesh tallies."""

		if axis == "f":
			nCells = self.nCells
			if self.nCells == 0: nCells = 1
			return nCells

		if axis == "i":
			return self.meshInfo[1]

		if axis == "j":
			return self.meshInfo[2]

		if axis == "k":
			return self.meshInfo[3]

		if axis == "d":
			nDir = self.nDir
			if self.nDir == 0: nDir = 1
			return nDir

		if axis == "u":
			nUsr = self.nUsr
			if self.nUsr == 0: nUsr = 1
			if self.usrTC == "t":
				nUsr = nUsr - 1
			return nUsr

		if axis == "s":
			nSeg = self.nSeg
			if self.nSeg == 0: nSeg = 1
			if self.segTC == "t":
				nSeg = nSeg - 1
			return nSeg

		if axis == "m":
			nMul = self.nMul
			if self.nMul == 0: nMul = 1
			if self.mulTC == "t":
				nMul = nMul - 1
			return nMul

		if axis == "c":
			nCos = self.nCos
			if self.nCos == 0: nCos = 1
			if self.cosTC == "t":
				nCos = nCos - 1
			return nCos

		if axis == "e":
			nErg = self.nErg
			if self.nErg == 0: nErg = 1
			if self.ergTC == "t":
				nErg = nErg - 1
			return nErg

		if axis == "t":
			nTim = self.nTim
			if self.nTim == 0: nTim = 1
			if self.timTC == "t":
				nTim = nTim - 1
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

	def __del__(self):
		self.mctalFile.close()

	def Read(self):
		"""This function calls the functions getHeaders and parseTally in order to read the entier MCTAL file."""

		if self.verbose:
			print "\n\033[1;34m[Parsing file: %s...]\033[0m" % self.mctalFileName

		self.getHeaders()
		if self.header.ntal != 0:
			self.getTallies()

		if self.thereAreNaNs and self.verbose:
			print >> sys.stderr, "\n \033[1;30mThe MCTAL file contains one or more tallies with NaN values. Flagged.\033[0m\n"
		return self.tallies

	def getHeaders(self):
		"""This function reads the first lines from the MCTAL file. We call "header" what is written from the beginning to the first "tally" keyword."""

		self.line = self.mctalFile.readline().split()

		if len(self.line) == 7:
			self.header.kod = self.line[0]
			self.header.ver = self.line[1]
			pID_date = self.line[2]
			self.header.probid.append(pID_date)
			pID_time = self.line[3]
			self.header.probid.append(pID_time)
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

		if len(self.line) == 4:
			self.header.npert = int(self.line[3])

		self.line = self.mctalFile.readline().split()

		while self.line[0].lower() != "tally":
			for l in self.line: self.header.ntals.append(int(l))
			self.line = self.mctalFile.readline().split()

	def getTallies(self):
		"""This function supervises the calls to parseTally() function. It will keep track of the position of cursor in the MCTAL file and stop execution when EOF is reached."""

		EOF = 0

		while EOF != 1:
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

		self.line = self.mctalFile.readline()
		line = self.line.split() # I must use this trick because some MCTAL files seem to omit
					 # the particle list and the code must be compatible with the 
					 # following part even if this line is missing, but I don't have
					 # the possibility to know in advance, so I must duplicate the
					 # read line.

		for p in line:
			if p.isdigit():
				v = int(p)
				tally.tallyParticles.append(v)

		if len(tally.tallyParticles) != 0: self.line = self.mctalFile.readline()

		while self.line[0].lower() != "f":
			tally.tallyComment.append(self.line[5:].rstrip())
			self.line = self.mctalFile.readline()

		self.line = self.line.split()

		tally.nCells = int(self.line[1])

		if len(self.line) > 2:
			tally.mesh = True
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

		while self.line[0].lower() != "m":
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
		nFld = 0
		tally.initializeValuesVectors()
		nCells = tally.nCells
		if tally.nCells == 0: nCells = 1
		nCora = tally.meshInfo[1]
		nCorb = tally.meshInfo[2]
		nCorc = tally.meshInfo[3]
		nDir = tally.nDir
		if tally.nDir   == 0: nDir   = 1
		nUsr = tally.nUsr
		if tally.nUsr   == 0: nUsr   = 1
		nSeg = tally.nSeg
		if tally.nSeg   == 0: nSeg   = 1
		nMul = tally.nMul
		if tally.nMul   == 0: nMul   = 1
		nCos = tally.nCos
		if tally.nCos   == 0: nCos   = 1
		nErg = tally.nErg
		if tally.nErg   == 0: nErg   = 1
		nTim = tally.nTim
		if tally.nTim   == 0: nTim   = 1
		for c in range(nCells):
			for d in range(nDir):
				for u in range(nUsr):
					for s in range(nSeg):
						for m in range(nMul):
							for a in range(nCos): # a is for Angle...forgive me
								for e in range(nErg):
									for t in range(nTim):
										for k in range(nCorc):
											for j in range(nCorb):
												for i in range(nCora):
													if (f > nFld): # f is for Field...again, forgive me
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
			return True
		elif "tally" in self.line:
			self.line = self.line.split()
			return False
