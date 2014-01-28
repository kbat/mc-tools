#! /usr/bin/python -W all
import subprocess
import tempfile
import os, sys

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
		self.cellsLineMeshTally = "%2s%8d" + "%5d"*4 # (A2,I8,4I5)
		self.axisFOptionLine = "%4d" # (I4)
		self.cellListLine = "%7d" # (11I7) - For cells without macrobody facets
		self.cellListLineMB = "%5d.%1d" # (I5,1H.,I1) - For cells with macrobody facets
		self.binValuesLine = "%13.5E" # (1P6E13.5)
		self.valsLine = "%4s" # (A4)
		self.valuesErrorsLine = "%13.5E%7.4F" # (4(1PE13.5,0PF7.4))
		self.tfcLine = "tfc%5d" + "%8d"*8 # (A3,I5,8I8)
		self.tfcValsLineSmall = "%11d" + "%13.5E"*2 # (I11,1P3E13.5)
		self.tfcValsLineBig = "%11.5E" + "%13.5E"*2 # (1E11.5

#############################################################################################################################

class TestSuite:
	"""This class implements test methods to recreate an ASCII MCTAL file after it has been read."""

	def __init__(self,obj,verbose=False):
		self.mctalObject = obj
		self.outFile = None
		self.verbose = verbose

	def Test(self):
		"This function performs the test. * Supported MCNPX versions: 2.5.0, 2.7.0. *"""

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

		if self.mctalObject.header.ver != "2.7.0" and self.mctalObject.header.ver != "2.5.0" and self.mctalObject.header.ver != "":
			print "\033[1;31m[* WARNING *]\033[0m\033[31m This MCNPX version is not officially supported. Results could be wrong.\033[0m"

		if len(self.mctalObject.header.probid) == 0:
			probid = str("").rjust(19)
		else:
			probid = str(self.mctalObject.header.probid[0]).rjust(10) + str(self.mctalObject.header.probid[1]).rjust(9)
                
                self.outFile.write(headerLine % (str(self.mctalObject.header.kod).ljust(8), 
						self.mctalObject.header.ver, 
						probid, 
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
                        if i > 0 and (i+1) % 16 == 0 and (i+1) != len(self.mctalObject.header.ntals):
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

		for tc in tally.tallyComment:
			self.outFile.write("\n" + fs.tallyCommentLine % (tc.ljust(75)))

		binIndexList = ("f","d","u","s","m","c","e","t","i","j","k")
		binNumberList = (tally.nCells,tally.nDir,tally.nUsr,tally.nSeg,tally.nMul,tally.nCos,tally.nErg,tally.nTim,tally.meshInfo[1],tally.meshInfo[2],tally.meshInfo[3])
		binList = dict(zip(binIndexList,binNumberList))

		for axis in binIndexList:

			if axis == "i" or axis == "j" or axis == "k":
				continue

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

			if axis == "f" and tally.mesh:
				nCells = tally.meshInfo[1] * tally.meshInfo[2] * tally.meshInfo[3]
				tup = (axisCard.ljust(2),nCells) + tuple(tally.meshInfo)
				self.outFile.write("\n" + fs.cellsLineMeshTally % tup)
			else:
				self.outFile.write("\n" + fs.axisCardLine % (axisCard.ljust(2),binList[axis]))

			if axis == "c" and tally.cosFlag != 0:
				self.outFile.write(fs.axisFOptionLine % (tally.cosFlag))
			if axis == "e" and tally.ergFlag != 0:
				self.outFile.write(fs.axisFOptionLine % (tally.ergFlag))
			if axis == "t" and tally.timFlag != 0:
				self.outFile.write(fs.axisFOptionLine % (tally.timFlag))

			if axis == "f" and tally.tallyNumber % 5 != 0 and tally.mesh == False:
				self.outFile.write("\n")
				for i in range(len(tally.cells)):
					splitCell = str(tally.cells[i]).split(".")
					if len(splitCell) != 1:
						self.outFile.write(fs.cellListLineMB % (int(splitCell[0]),int(splitCell[1])))
					else:
						self.outFile.write(fs.cellListLine % (tally.cells[i]))
					if i > 0 and (i+1) % 11 == 0 and (i+1) != len(tally.cells):
						self.outFile.write("\n")

			if axis == "f" and tally.tallyNumber % 5 != 0 and tally.mesh == True:
				self.outFile.write("\n")
				for i in range(tally.meshInfo[1]+1):
					self.outFile.write(fs.binValuesLine % (tally.cora[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[1]:
						self.outFile.write("\n")
				self.outFile.write("\n")
				for i in range(tally.meshInfo[2]+1):
					self.outFile.write(fs.binValuesLine % (tally.corb[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[2]:
						self.outFile.write("\n")
				self.outFile.write("\n")
				for i in range(tally.meshInfo[3]+1):
					self.outFile.write(fs.binValuesLine % (tally.corc[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[3]:
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

		ii = 0
		tot = tally.getTotNumber()

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
		for f in range(nCells):
			for d in range(nDir):
				for u in range(nUsr):
					for s in range(nSeg):
						for m in range(nMul):
							for c in range(nCos):
								for e in range(nErg):
									for t in range(nTim):
										for k in range(nCorc):
											for j in range(nCorb):
												for i in range(nCora):
													self.outFile.write(fs.valuesErrorsLine % (tally.getValue(f,d,u,s,m,c,e,t,i,j,k,0),tally.getValue(f,d,u,s,m,c,e,t,i,j,k,1)))
													if (ii+1) % 4 == 0 and (ii+1) != tot:
														self.outFile.write("\n")
													ii = ii + 1

		if tally.mesh == False:
			self.outFile.write("\n" + fs.tfcLine % tuple(tally.tfc_jtf))

			for tfc_dat in tally.tfc_dat:
				tfcValsLine = fs.tfcValsLineSmall
				if tfc_dat[0] >= 1e11:
					tfcValsLine = fs.tfcValsLineSmall
				if len(tfc_dat) == 4:
					tfcValsLine += "%13.5E"
				self.outFile.write("\n" + tfcValsLine % tuple(tfc_dat))


	def diffFiles(self):
		"""This function checks whether the files are equal or not."""

		if not subprocess.call(['diff', '-bi', self.mctalObject.mctalFileName, self.outFile.name], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
			if self.verbose:
				print "\n\033[1;32m[TEST PASSED]\033[0m"
			os.remove(self.outFile.name)
			return 0
		else:
			if self.verbose:
				print >> sys.stderr, "\n\033[1;31m[TEST FAILED]\033[0m"
				print >> sys.stderr,  "\033[1;31mOriginal MCTAL:\033[0m\033[31m %s - \033[0m\033[1;31mTest MCTAL:\033[0m\033[31m %s\033[0m" % (self.mctalObject.mctalFileName,self.outFile.name)
				print >> sys.stderr,  "\033[1;31mTry:\033[0m\033[31m diff -b -i %s %s\033[0m\n" % (self.mctalObject.mctalFileName,self.outFile.name)
			else:
				print >> sys.stderr, "\033[1;31mFAILED FOR FILE: \033[0m\033[31m%s\033[0m" % (self.mctalObject.mctalFileName)
				print >> sys.stderr,  "\033[1;31mTry:\033[0m\033[31m diff -b -i %s %s\033[0m\n" % (self.mctalObject.mctalFileName,self.outFile.name)
			return 1

		
