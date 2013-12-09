import subprocess
import tempfile
import os

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
		self.tallyInfoLine = "%5s" + "%5d"*2 # (A5,3I5)
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

class TestSuite:
	"""This class implements test methods to recreate an ASCII MCTAL file after it has been read."""

	def __init__(self,obj,verbose=False):
		self.mctalObject = obj
		self.outFile = None
		self.verbose = verbose

	def Test(self):
		"This function performs the test."""

		self.prepareMctalTestFile()
		self.writeHeader()
		for t in self.mctalObject.tallies:
			self.writeTally(t)
		self.outFile.close()
		return self.diffFiles()

	def prepareMctalTestFile(self):
		"""This function opens the test file for writing."""

		fname = os.path.basename(self.mctalObject.mctalFileName)

		self.outFile = tempfile.NamedTemporaryFile(prefix=fname,delete=False)

	def writeHeader(self):
		"""This function writes the header of the MCTAL file."""

                fs = FormatStrings()    
                
                headerLine = fs.headerLine_270
                
                if self.mctalObject.header.ver != "2.7.0": 
                        headerLine = fs.headerLine_250
                
                self.outFile.write(headerLine % (str(self.mctalObject.header.kod).ljust(8), 
						self.mctalObject.header.ver, 
						str(self.mctalObject.header.probid[0]).rjust(10) + str(self.mctalObject.header.probid[1]).rjust(9), 
						self.mctalObject.header.knod, 
						self.mctalObject.header.nps, 
						self.mctalObject.header.rnr))

                self.outFile.write("\n" + fs.titleLine % (self.mctalObject.header.title.ljust(79)))
                self.outFile.write("\n" + fs.ntalLine % ("ntal",self.mctalObject.header.ntal))

                if self.mctalObject.header.npert > 0:
                        self.outFile.write(fs.npertLine % ("npert",self.mctalObject.header.npert))

                self.outFile.write("\n")

                for i in range(len(self.mctalObject.header.ntals)):
                        self.outFile.write(fs.tallyNumbersLine % self.mctalObject.header.ntals[i])
                        if i > 0 and i % 16 == 0:
                                self.outFile.write("\n")

	def writeTally(self,tally):
		"""This function writes the tallies with all the data."""

		fs = FormatStrings()

		self.outFile.write(fs.tallyInfoLine % ("\ntally",tally.tallyNumber,tally.typeNumber))
		if tally.detectorType != None: self.outFile.write("%5d" % (tally.detectorType))

		#self.outFile.write("\n")

                for i in range(len(tally.tallyParticles)):
			if i == 0: self.outFile.write("\n")
                        self.outFile.write(fs.tallyParticlesLine % (tally.tallyParticles[i])) 
                        if i > 0 and (i+1) % 40 == 0: 
                                self.outFile.write("\n") 

		for i in range(len(tally.tallyComment)):
			self.outFile.write("\n" + fs.tallyCommentLine % (tally.tallyComment[i].ljust(75)))

		binIndexList = ["f","d","u","s","m","c","e","t"]
		binNumberList = [tally.nCells,tally.nDir,tally.nUsr,tally.nSeg,tally.nMul,tally.nCos,tally.nErg,tally.nTim]
		binList = dict(zip(binIndexList,binNumberList))

		for axis in binIndexList:

			axisCard = axis

			if axis == "u" and tally.usrTC != None:
				axisCard += tally.usrTC
			if axis == "s" and tally.segTC != None:
				axisCard += tally.segTC
			if axis == "m" and tally.mulTC != None:
				axisCard += tally.mulTC
			if axis == "c" and tally.cosTC != None:
				axisCard += tally.cosTC
			if axis == "e" and tally.ergTC != None:
				axisCard += tally.ergTC
			if axis == "t" and tally.timTC != None:
				axisCard += tally.timTC

			self.outFile.write("\n" + fs.axisCardLine % (axisCard.ljust(2),binList[axis]))

			if axis == "c" and tally.cosFlag != 0:
				self.outFile.write(fs.axisFOptionLine % (tally.cosFlag))
			if axis == "e" and tally.ergFlag != 0:
				self.outFile.write(fs.axisFOptionLine % (tally.ergFlag))
			if axis == "t" and tally.timFlag != 0:
				self.outFile.write(fs.axisFOptionLine % (tally.timFlag))

			if axis == "f" and tally.tallyNumber % 5 != 0:
				self.outFile.write("\n")
				for i in range(len(tally.cells)):
					self.outFile.write(fs.cellListLine % (tally.cells[i]))
					if i > 0 and (i+1) % 11 == 0 and (i+1) != len(tally.cells):
						self.outFile.write("\n")

			if axis == "u" and len(tally.usr) != 0:
				self.outFile.write("\n")
				for i in range(len(tally.usr)):
					self.outFile.write(fs.binValuesLine % (tally.usr[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.usr):
						self.outFile.write("\n")

			if axis == "c" and len(tally.cos) != 0:
				self.outFile.write("\n")
				for i in range(len(tally.cos)):
					self.outFile.write(fs.binValuesLine % (tally.cos[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.cos):
						self.outFile.write("\n")

			if axis == "e" and len(tally.erg) != 0:
				self.outFile.write("\n")
				for i in range(len(tally.erg)):
					self.outFile.write(fs.binValuesLine % (tally.erg[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.erg):
						self.outFile.write("\n")

			if axis == "t" and len(tally.tim) != 0:
				self.outFile.write("\n")
				for i in range(len(tally.tim)):
					self.outFile.write(fs.binValuesLine % (tally.tim[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.tim):
						self.outFile.write("\n")
				

		self.outFile.write("\n" + fs.valsLine %("vals\n"))

		i = 0
		tot = tally.getTotNumber()

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
		for f in range(nCells):
			for d in range(nDir):
				for u in range(nUsr):
					for s in range(nSeg):
						for m in range(nMul):
							for c in range(nCos):
								for e in range(nErg):
									for t in range(nTim):
										self.outFile.write(fs.valuesErrorsLine % (tally.getValue(f,d,u,s,m,c,e,t,0),tally.getValue(f,d,u,s,m,c,e,t,1)))
										if (i+1) % 4 == 0 and (i+1) != tot:
											self.outFile.write("\n")
										i = i + 1

		self.outFile.write("\n" + fs.tfcLine % tuple(tally.tfc_jtf))

		for i in range(len(tally.tfc_dat)):
			tfcValsLine = fs.tfcValsLineSmall
			if tally.tfc_dat[i][0] >= 1e11:
				tfcValsLine = fs.tfcValsLineSmall
			self.outFile.write("\n" + tfcValsLine % tuple(tally.tfc_dat[i]))


	def diffFiles(self):
		"""This function checks whether the files are equal or not."""

		p = subprocess.Popen("diff -b %s %s" % (self.mctalObject.mctalFileName,self.outFile.name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
		if len(p.stdout.readlines()) == 0:
			if self.verbose:
				print "\n\033[1m[TEST PASSED]\033[0m"
			return 0
		else:
			#for line in p.stdout.readlines():
			#	print line,
			#retval = p.wait()
			if self.verbose:
				print "\n\033[1m[TEST FAILED]\033[0m"
				print "\033[1mOriginal MCTAL:\033[0m %s - \033[1mTest MCTAL:\033[0m %s" % (self.mctalObject.mctalFileName,self.outFile.name)
				print "\033[1mTry:\033[0m diff -b %s %s\033[0m\n" % (self.mctalObject.mctalFileName,self.outFile.name)
			return 1

		
