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
		self.tfcLine = "%3s%5d" + "%8d"*8 # (A3,I5,8I8)
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
		self.tallyComment = None
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

		self.cos = []
		self.erg = []
		self.tim = []

		self.tfc_jtf = ["tfc",0,1,2,3,4,5,6,7,8]
		self.tfc_dat = []
		
		self.binIndexList = ["f","d","u","s","m","c","e","t"]

		self.valsErrors = [[[[[[[[[]]]]]]]]]


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

		self.valsErrors[c][d][u][s][m][a][e][t][f] = val

	def getValue(self,c,d,u,s,m,a,e,t,f,val):
		"""Return a value from tally."""

		return self.valsErrors[c][d][u][s][m][a][e][t][f]

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

		testFile.write("\n" + fs.tallyCommentLine % (self.tallyComment.ljust(75)))

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
					if i > 0 and i % 11 == 0:
						testFile.write("\n")

			if axis == "c" and len(self.cos) != 0:
				testFile.write("\n")
				for i in range(len(self.cos)):
					testFile.write(fs.binValuesLine % (self.cos[i]))
					if i > 0 and i % 6 == 0:
						testFile.write("\n")

			if axis == "e" and len(self.erg) != 0:
				testFile.write("\n")
				for i in range(len(self.erg)):
					testFile.write(fs.binValuesLine % (self.erg[i]))
					if i > 0 and i % 6 == 0:
						testFile.write("\n")

			if axis == "t" and len(self.tim) != 0:
				testFile.write("\n")
				for i in range(len(self.tim)):
					testFile.write(fs.binValuesLine % (self.tim[i]))
					if i > 0 and i % 6 == 0:
						testFile.write("\n")
				

		testFile.write("\n" + fs.valsLine %("vals"))

		i = 0

		for f in range(self.nCells):
			for d in range(self.nDir):
				for u in range(self.nUsr):
					for s in range(self.nSeg):
						for m in range(self.nMul):
							for c in range(self.nCos):
								for e in range(self.nErg):
									for t in range(self.nTim):
										testFile.write(fs.valuesErrorsLine % (self.vals[f][d][u][s][m][c][e][t][0],self.vals[f][d][u][s][m][c][e][t][1]))
										i = i + 1 
										if i % 4 == 0:
											testFile.write("\n")

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













