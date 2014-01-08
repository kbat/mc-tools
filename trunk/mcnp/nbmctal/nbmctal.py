#!/usr/bin/python -W all
#
# mctal reading script by Nicolo' Borghi
# Started on 04/12/2013 at ESS Lund
# based on scripts developed by the author,
# Dr. Gallmeier and Dr. Batkov
#
#

import sys, re, string
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
		self.tallyParticles = []   # List of 0/1 entries indicating which particle types are used by the tally
		self.tallyComment = []     # The FC card lines
		self.nCells = 0            # Number of cell, surface or detector bins
		self.mesh = False          # True if the tally is a mesh tally
		self.meshInfo = []         # Mesh binning information in the case of a mesh tally
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

		self.tfc_jtf = []          # List of numbers in the tfc line
		self.tfc_dat = []          # Tally fluctuation chart data (NPS, tally, error, figure of merit)
		
		self.binIndexList = ["f","d","u","s","m","c","e","t"]

		self.isInitialized = False
		self.valsErrors = []       # Array of values and errors


	def initializeValuesVectors(self):
		"""This function initializes the 9-D matrix for the storage of values and errors."""

		tmpV = []
		tmpT = []
		tmpE = []
		tmpC = []
		tmpM = []
		tmpS = []
		tmpU = []
		tmpD = []

                nCells = self.nCells
                if self.nCells == 0: nCells = 1
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

		self.valsErrors = [[[[[[[[[[] for _ in range(2)] for _ in range(nTim)] for _ in range(nErg)] for _ in range(nCos)] for _ in range(nMul)] for _ in range(nSeg)] for _ in range(nUsr)] for _ in range(nDir)] for _ in xrange(nCells)]

		self.isInitialized = True
		

	def Print(self, option=[]):
		"""Tally printer. Options: title. Verbose flag on class initialization must be set to True."""

		if self.verbose:
			print "To be implemented. Not essential for now.\n"

	def getTotNumber(self):
		"""Return the total number of bins."""

                nCells = self.nCells
                if self.nCells == 0: nCells = 1
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
                
                tot = nCells * nDir * nUsr * nSeg * nMul * nCos * nErg * nTim

                return tot

	def insertCell(self,cN):
		"""Insert cell number."""

		if len(self.cells) <= self.nCells:
			self.cells.append(cN)
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

	def insertValue(self,c,d,u,s,m,a,e,t,f,val):
		"""Insert tally value."""

		if self.isInitialized == False:
			self.initializeValuesVectors()

		self.valsErrors[c][d][u][s][m][a][e][t][f] = val

	def getValue(self,f,d,u,s,m,c,e,t,v):
		"""Return a value from tally."""

		return self.valsErrors[f][d][u][s][m][c][e][t][v]

#############################################################################################################################

class MCTAL:
	"""This class parses the whole MCTAL file."""

	def __init__(self,fname,verbose=False):
		self.verbose = verbose
		self.tallies = []
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
			print "\n\033[1m[Parsing file: %s%3s]\033[0m" % (str(self.mctalFileName),"...")

		self.getHeaders()
		if self.header.ntal != 0:
			self.getTallies()

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
			print " Parsing tally: %5d" % (tally.tallyNumber)

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
			tally.meshInfo.append(int(self.line[2])) # Unknown number
			tally.meshInfo.append(int(self.line[3])) # number of cora bins
			tally.meshInfo.append(int(self.line[4])) # number of corb bins
			tally.meshInfo.append(int(self.line[5])) # number of corc bins

		self.line = self.mctalFile.readline()

		while self.line[0].lower() != "d": # CELLS
			if tally.mesh:
				for c in self.line.split():
					exitCode = tally.insertCell(float(c))
					if exitCode == 0:
						print " Too many cells." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
				#print >> sys.stderr, " Mesh tally. Skipping (for now) this tally. TEST WILL FAIL. " + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
				#sys.exit(4)
			elif "." in self.line and "E" not in self.line:
				for c in self.line.split():
					exitCode = tally.insertCell(float(c))
					if exitCode == 0:
						print " Too many cells." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
				#print >> sys.stderr, " Macrobodies found." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
				#sys.exit(5)
			else:
				for c in self.line.split():
					exitCode = tally.insertCell(int(c))
					if exitCode == 0: # This means that for some reason you are trying to
							  # insert mre cells than the number stated in f
						print " Too many cells." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
						sys.exit(1) 

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
				exitCode = tally.insertUsr(float(u))
				if exitCode == 0:
					print >> sys.stderr, "Too many USR bins." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
					sys.exit(1)
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
				exitCode = tally.insertCos(float(c))
				if exitCode == 0:
					print >> sys.stderr, "Too many COS bins." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
					sys.exit(1)
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
				exitCode = tally.insertErg(float(e))
				if exitCode == 0:
					print >> sys.stderr, "Too many ERG bins." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
					sys.exit(1)
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
				exitCode = tally.insertTim(float(t))
				if exitCode == 0:
					print >> sys.stderr, "Too many TIME bins." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
					sys.exit(1)
			self.line = self.mctalFile.readline()

		# VALS
		f = 1
		nFld = 0
		tally.initializeValuesVectors()
		nCells = tally.nCells
		if tally.nCells == 0: nCells = 1
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
										if (f > nFld): # f is for Field...again, forgive me
											self.line = self.mctalFile.readline().strip()
											Fld = self.line.split()
											nFld = len(Fld) - 1
											f = 0

										#print self.line

										if self.line[0:3] != "tfc":
											#print "%4d"*8 % (c,d,u,s,m,a,e,t) #+ "%13.5E" % (float(Fld[f]))
											tally.insertValue(c,d,u,s,m,a,e,t,0,float(Fld[f]))
											tally.insertValue(c,d,u,s,m,a,e,t,1,float(Fld[f+1]))

											f += 2

		if tally.mesh == False:
			# TFC JTF
			while self.line[0] != "tfc":
				self.line = self.mctalFile.readline().strip().split()

			del self.line[0]
			self.line = [int(i) for i in self.line]

			exitCode = tally.insertTfcJtf(self.line)
			if exitCode == 0:
				print "Wrong number of TFC jtf elements."


			# TFC DAT
			self.line = self.mctalFile.readline().strip()
			while "tally" not in self.line and len(self.line) != 0:
				self.line = self.line.split()
			
				tfcDat = []

				tfcDat.append(int(self.line[0]))
				tfcDat.append(float(self.line[1]))
				tfcDat.append(float(self.line[2]))
				if len(self.line) == 4:
					tfcDat.append(float(self.line[3]))

				exitCode = tally.insertTfcDat(tfcDat)

				if exitCode == 0:
					print >> sys.stderr, "Wrong number of elements in TFC data line." + self.mctalFileName + " - Tally n.:%5d" % tally.tallyNumber
					sys.exit(1)

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




























