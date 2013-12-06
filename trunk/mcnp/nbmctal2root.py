#!/usr/bin/python
#
# mctal reading script by Nicolo' Borghi
# Started on 04/12/2013 at ESS Lund
# based on scripts developed by the author,
# Dr. Gallmeier and Dr. Batkov
#
#

import sys, re, string
from array import array
#from mcnp import GetParticleNames

#############################################################################################################################

class FormatStrings:
	"""This class contins the string formats used by MCNPX to format the MCTAL file"""

	def __init__(self):
		self.headerLine_250 = "%8s"*2 + "%19s%5d%11d%15d" # (2A8,A19,I15,I11,I15)
		self.headerLine_270 = "%8s"*2 + "%19s%5d%13d%15d" # (2A8,A19,I15,I13,I15)
		self.titleLine = " %79s" # (1X,A79)
		self.ntalLine = "%4s%6d" # (A4,I6)
		self.npertLine = " %5s%6d" # (1X,A5,I6)
		self.tallyNumbersLine = "%5d" # (16I5)
		self.tallyInfoLine = "%5s" + "%5d"*3 # (A5,3I5)
		self.tallyParticlesLine = "%2d" # (40I12)
		self.tallyCommentLine = " "*5 + "%75s" # (5X,A75)
		self.axisCardLine = "%2s%8d" # (A2,I8)
		self.axisFOptionLine = "%4d" # (I4)
		self.cellListLine = "%7d" # (11I7)
		self.binValuesLine = "%13.5E" # (1P6E13.5)
		self.valsLine = "%4s" # (A4)
		self.valuesErrorsLine = "%13.5E%7.4F" # (4(1PE13.5,0PF7.4))
		self.tfcLine = "tfc%5d" + "%8d"*8 # (A3,I5,8I8)
		self.tfcValsLineSmall = "%11d" + "%13.5E"*3 # (I11,1P3E13.5)
		self.tfcValsLineBig = "%11.5E" + "%13.5E"*3 # (1E11.5

#############################################################################################################################

class Header:
	"""This class contains header information from MCTAL file"""

	def __init__(self):
		self.kod = 0		# Name of the code, MCNPX
		self.ver = 0		# Code version
		self.probid = []	# Date and time when the problem was run
		self.knod = 0		# The dump number
		self.nps = 0		# Number of histories that were run
		self.rnr = 0		# Number of pseudoradom numbers that were used
		self.title = None	# Problem identification line
		self.ntal = 0		# Number of tallies
		self.ntals = []		# Array of tally numbers
		self.npert = 0		# Number of perturbations

	def Print(self):
	        """Prints the class members"""

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

	def Test(self,fName):
		"""This function writes the header of the test MCTAL file to be compared with the original one. This will be the only function to use the "w" option for the file. All the other functions will use "a". """

		testFile = open(fName, "w")

		fs = FormatStrings()

		headerLine = fs.headerLine_270

		if self.ver == "2.5.0":
			headerLine = fs.headerLine_250

		testFile.write(headerLine % (str(self.kod).ljust(8), self.ver, str(self.probid[0]).rjust(10) + str(self.probid[1]).rjust(9), self.knod, self.nps, self.rnr))
		testFile.write("\n" + fs.titleLine % (self.title.ljust(79)))
		testFile.write("\n" + fs.ntalLine % ("ntal",self.ntal))

		if self.npert > 0:
			testFile.write(fs.npertLine % ("npert",self.npert))

		testFile.write("\n")

		for i in range(len(self.ntals)):
			testFile.write(fs.tallyNumbersLine % self.ntals[i])
			if i > 0 and i % 16 == 0:
				testFile.write("\n")

		testFile.close()

#############################################################################################################################

class Tally:
	"""This class is aimed to store all the information contained in a tally."""

	def __init__(self,tN):
		self.tallyNumber = tN
		self.typeNumber = 0
		self.detectorType = 0
		self.tallyParticles = []
		self.tallyComment = [] 
		self.nCells = 0
		self.nDir = 0
		self.nUsr = 0
		self.usrTC = None
		self.nSeg = 0
		self.segTC = None
		self.nMul = 0
		self.mulTC = None
		self.nCos = 0
		self.cosTC = None
		self.cosFlag = 0
		self.nErg = 0
		self.ergTC = None
		self.ergFlag = 0
		self.nTim = 0
		self.timTC = None
		self.timFlag = 0

		self.cells = []

		self.usr = []
		self.cos = []
		self.erg = []
		self.tim = []

		self.tfc_jtf = []
		self.tfc_dat = []
		
		self.binIndexList = ["f","d","u","s","m","c","e","t"]

		self.isInitialized = 0
		self.valsErrors = []


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

		self.isInitialized = 1
		

	def Print(self, option=[]):
		"""Tally printer. Options: title."""

		print "To be implemented. Not essential for now.\n"

	def getTallyNumber(self):
		"""Return the name (number) of the tally."""

		return self.tallyNumber

	def getTypeNumber(self):
		"""Return the particle type (if > 0) or the number of involved particles (if < 0)."""

		return self.typeNumber

	def getDetectorType(self):
		"""Return the detector type."""

		return self.detectorType

	def getTallyParticles(self):
		"""Returns the list of particles in the tally."""

		return self.tallyParticles

	def getTallyComment(self):
		"""Return tally comment."""

		return self.tallyComment

	def getNumbers(self,index):
		"""Return the number of the bins for one axis from (f,d,u,s,m,c,e,t) depending on the requested index."""

		binNumberList = [self.nCells,self.nDir,self.nUsr,self.nSeg,self.nMul,self.nCos,self.nErg,self.nTim]

		binList = dict(zip(self.binIndexList,binNumberList))

		return binList[index]

	def getTotNumber(self):
		"""Return the total number of bins."""

		tot = self.nCells * self.nDir * self.nUsr * self.nSeg * self.nMul * self.nCos * self.nErg * self.nTim

		return tot

	def insertCell(self,cN):
		"""Insert cell number."""

		if len(self.cells) <= self.nCells:
			self.cells.append(cN)
			return 1 
		else:
			return 0

	def insertUsr(self,uB):
		"""Insert usr bins."""

		if len(self.usr) <= self.nUsr:
			self.usr.append(uB)
			return 1
		else:
			return 0

	def insertCos(self,cB):
		"""Insert cosine bin."""

		if len(self.cos) <= self.nCos:
			self.cos.append(cB)
			return 1
		else:
			return 0

	def insertErg(self,eB):
		"""Insert energy bin."""

		if len(self.erg) <= self.nErg:
			self.erg.append(eB)
			return 1
		else:
			return 0

	def insertTim(self,tB):
		"""Insert time bin."""

		if len(self.tim) <= self.nTim:
			self.tim.append(tB)
			return 1
		else:
			return 0

	def insertTfcJtf(self,jtf):
		"""Insert TFC jtf list."""

		if len(jtf) == 9:
			self.tfc_jtf = jtf
			return 1
		else:
			return 0

	def getTfcJtf(self):
		"""Return jtf information about TFC."""

		return self.tfc_jtf

	def insertTfcDat(self,dat):
		"""Insert TFC values."""

		if len(dat) == 4:
			self.tfc_dat.append(dat)
			return 1
		else:
			return 0

	def getTfcDat(self):
		"""Return TFC values."""

		return self.tfc_dat

	def insertValue(self,c,d,u,s,m,a,e,t,f,val):
		"""Insert tally value."""

		if self.isInitialized == 0:
			self.initializeValuesVectors()

		#print "%4d"*9 % (c,d,u,s,m,a,e,t,f) + "%13.5E" % val
		self.valsErrors[c][d][u][s][m][a][e][t][f] = val
		#print "    "*9 + "%13.5E" % self.getValue(c,d,u,s,m,a,e,t,f)

	def getValue(self,f,d,u,s,m,c,e,t,v):
		"""Return a value from tally."""

		#print "FI: " + "%4d"*9 % (f,d,u,s,m,c,e,t,v) + "%13.5E" % self.valsErrors[f][d][u][s][m][c][e][t][v]
		return self.valsErrors[f][d][u][s][m][c][e][t][v]

	def Test(self,fName):
		"""This function writes the header of the test MCTAL file to be compared with the original one. This function appends contents at the end of the file created by the Header.Test() function."""

		fs = FormatStrings()

		testFile = open(fName, "a")

		testFile.write(fs.tallyInfoLine % ("\ntally",self.tallyNumber,self.typeNumber,self.detectorType))

		testFile.write("\n")

                for i in range(len(self.tallyParticles)): 
                        testFile.write(fs.tallyParticlesLine % (self.tallyParticles[i])) 
                        if i > 0 and i % 40 == 0: 
                                testFile.write("\n") 

		for i in range(len(self.tallyComment)):
			testFile.write("\n" + fs.tallyCommentLine % (self.tallyComment[i].ljust(75)))

		binNumberList = [self.nCells,self.nDir,self.nUsr,self.nSeg,self.nMul,self.nCos,self.nErg,self.nTim]
		binList = dict(zip(self.binIndexList,binNumberList))

		for axis in self.binIndexList:

			axisCard = axis

			if axis == "u" and self.usrTC != None:
				axisCard += self.usrTC
			if axis == "s" and self.segTC != None:
				axisCard += self.segTC
			if axis == "m" and self.mulTC != None:
				axisCard += self.mulTC
			if axis == "c" and self.cosTC != None:
				axisCard += self.cosTC
			if axis == "e" and self.ergTC != None:
				axisCard += self.ergTC
			if axis == "t" and self.timTC != None:
				axisCard += self.timTC

			testFile.write("\n" + fs.axisCardLine % (axisCard.ljust(2),binList[axis]))

			if axis == "c" and self.cosFlag != 0:
				testFile.write(fs.axisFOptionLine % (self.cosFlag))
			if axis == "e" and self.ergFlag != 0:
				testFile.write(fs.axisFOptionLine % (self.ergFlag))
			if axis == "t" and self.timFlag != 0:
				testFile.write(fs.axisFOptionLine % (self.timFlag))

			if axis == "f" and self.tallyNumber % 5 != 0:
				testFile.write("\n")
				for i in range(len(self.cells)):
					testFile.write(fs.cellListLine % (self.cells[i]))
					if i > 0 and (i+1) % 11 == 0 and (i+1) != len(self.cells):
						testFile.write("\n")

			if axis == "u" and len(self.usr) != 0:
				testFile.write("\n")
				for i in range(len(self.usr)):
					testFile.write(fs.binValuesLine % (self.usr[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(self.usr):
						testFile.write("\n")

			if axis == "c" and len(self.cos) != 0:
				testFile.write("\n")
				for i in range(len(self.cos)):
					testFile.write(fs.binValuesLine % (self.cos[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(self.cos):
						testFile.write("\n")

			if axis == "e" and len(self.erg) != 0:
				testFile.write("\n")
				for i in range(len(self.erg)):
					testFile.write(fs.binValuesLine % (self.erg[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(self.erg):
						testFile.write("\n")

			if axis == "t" and len(self.tim) != 0:
				testFile.write("\n")
				for i in range(len(self.tim)):
					testFile.write(fs.binValuesLine % (self.tim[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(self.tim):
						testFile.write("\n")
				

		testFile.write("\n" + fs.valsLine %("vals\n"))

		i = 0
		tot = self.getTotNumber()

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
		for f in range(nCells):
			for d in range(nDir):
				for u in range(nUsr):
					for s in range(nSeg):
						for m in range(nMul):
							for c in range(nCos):
								for e in range(nErg):
									for t in range(nTim):
										testFile.write(fs.valuesErrorsLine % (self.getValue(f,d,u,s,m,c,e,t,0),self.getValue(f,d,u,s,m,c,e,t,1)))
										if (i+1) % 4 == 0 and (i+1) != tot:
											testFile.write("\n")
										i = i + 1

		testFile.write("\n" + fs.tfcLine % tuple(self.tfc_jtf))

		for i in range(len(self.tfc_dat)):
			tfcValsLine = fs.tfcValsLineSmall
			if self.tfc_dat[i][0] >= 1e11:
				tfcValsLine = fs.tfcValsLineSmall
			testFile.write("\n" + tfcValsLine % tuple(self.tfc_dat[i]))

		testFile.close()


#############################################################################################################################

class MCTAL:
	"""This class parses the whole MCTAL file."""

	def __init__(self,fname):
		self.tallies = [] # This list will contain all the instances of the Tally class.
		self.header = Header()
		self.mctalFileName = fname
		self.mctalTestFileName = fname + "_testFile"
		self.mctalFile = open(self.mctalFileName, "r")
		self.line = None # This variable will contain the read lines one by one, but it is
				 # important to keep it global because the last value from getHeaders()
				 # must be already available as first value for parseTally(). This will
				 # also apply to successive calls to parseTally().

	def __del__(self):
		self.mctalFile.close()

	def Test(self):
		self.header.Test(self.mctalTestFileName)
		for tally in self.tallies:
			tally.Test(self.mctalTestFileName)
		

	def Read(self):
		"""This function calls the functions getHeaders and parseTally in order to read the entier MCTAL file."""

		self.getHeaders()
		self.getTallies()

	def getHeaders(self):
		"""This function reads the first lines from the MCTAL file. We call "header" what is written from the beginning to the first "tally" keyword."""

		self.line = self.mctalFile.readline().split()

		self.header.kod = self.line[0]
		self.header.ver = self.line[1]
		pID_date = self.line[2]
		self.header.probid.append(pID_date)
		pID_time = self.line[3]
		self.header.probid.append(pID_time)
		self.header.knod = int(self.line[4])
		self.header.nps = int(self.line[5])
		self.header.rnr = int(self.line[6])

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

		tally = Tally(int(self.line[1]))

		print "Parsing tally: %5d" % (tally.tallyNumber)

		tally.typeNumber = int(self.line[2])
		tally.detectorType = int(self.line[3])

		self.line = self.mctalFile.readline().split()

		for p in self.line:
			tally.tallyParticles.append(int(p))

		self.line = self.mctalFile.readline()

		while self.line[0].lower() != "f":
			tally.tallyComment.append(self.line[5:].rstrip())
			self.line = self.mctalFile.readline()

		self.line = self.line.split()

		tally.nCells = int(self.line[1])

		self.line = self.mctalFile.readline()

		while self.line[0].lower() != "d": # CELLS
			for c in self.line.split():
				exitCode = tally.insertCell(int(c))
				if exitCode == 0: # This means that for some reason you are trying to
						  # insert more cells than the number stated in f
					print "Too many cells."
					break 
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
					print "Too many bins."
					break
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
					print "Too many bins."
					break
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
					print "Too many bins."
					break
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
					print "Too many bins."
					break
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
											#print "%4d"*8 % (c,d,u,s,m,a,e,t) + "%13.5E" % (float(Fld[f]))
											tally.insertValue(c,d,u,s,m,a,e,t,0,float(Fld[f]))
											tally.insertValue(c,d,u,s,m,a,e,t,1,float(Fld[f+1]))

											f += 2

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
			tfcDat.append(float(self.line[3]))

			exitCode = tally.insertTfcDat(tfcDat)

			if exitCode == 0:
				print "Wrong number of elements in TFC data line."
				break

			self.line = self.mctalFile.readline().strip()

		self.tallies.append(tally)

		if self.line == "":
			return 1
		elif "tally" in self.line:
			self.line = self.line.split()
			return 0




























