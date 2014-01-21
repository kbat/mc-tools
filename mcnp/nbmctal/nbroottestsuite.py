#! /usr/bin/python -W all
import subprocess
import tempfile
import os,sys,numpy
from array import array
from nbtestsuite import FormatStrings
import ROOT

#############################################################################################################################

class RootTest:
	"""This class implements test methods to recreate and ASCII file from a converted ROOT file."""

	def __init__(self,obj,rootFile,verbose=False):
		self.mctalObject = obj
		self.rootFileName = rootFile
		self.mctalOutFile = None
		self.rootOutFile = None
		self.verbose = verbose

	def Test(self):
		"""This function performs the test."""

		self.prepareTestFiles()
		for t in self.mctalObject.tallies:
			self.writeMctalVals(t)
		self.writeRootVals()
		self.mctalOutFile.close()
		self.rootOutFile.close()
		return self.diffFiles()

	def prepareTestFiles(self):
		"""This function opens the test files for writing."""

		mFname = os.path.basename(self.mctalObject.mctalFileName)
		self.mctalOutFile = tempfile.NamedTemporaryFile(prefix=mFname,delete=False)

		rFname = os.path.basename(self.rootFileName)
		self.rootOutFile = tempfile.NamedTemporaryFile(prefix=rFname, delete=False)

	def writeMctalVals(self,tally):
		"""This function writes only mctal values (bins and tally values) without any header."""

		fs = FormatStrings()

		binIndexList = ("f","d","u","s","m","c","e","t","i","j","k")
		binNumberList = (tally.nCells,tally.nDir,tally.nUsr,tally.nSeg,tally.nMul,tally.nCos,tally.nErg,tally.nTim,tally.meshInfo[1],tally.meshInfo[2],tally.meshInfo[3])
		binList = dict(zip(binIndexList,binNumberList))

		for axis in binIndexList:

			if axis == "i" or axis == "j" or axis == "k":
				continue

			axisCard = axis

			if axis == "f" and tally.tallyNumber % 5 != 0 and tally.mesh == True:
				self.mctalOutFile.write("\n")
				for i in range(tally.meshInfo[1]+1):
					self.mctalOutFile.write(fs.binValuesLine % (tally.cora[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[1]:
						self.mctalOutFile.write("\n")
				self.mctalOutFile.write("\n")
				for i in range(tally.meshInfo[2]+1):
					self.mctalOutFile.write(fs.binValuesLine % (tally.corb[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[2]:
						self.mctalOutFile.write("\n")
				self.mctalOutFile.write("\n")
				for i in range(tally.meshInfo[3]+1):
					self.mctalOutFile.write(fs.binValuesLine % (tally.corc[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[3]:
						self.mctalOutFile.write("\n")

			if axis == "u" or axis == "c" or axis == "e" or axis == "t":
				self.mctalOutFile.write("\n")

			if axis == "u" and len(tally.usr) != 0:
				for i in range(len(tally.usr)):
					self.mctalOutFile.write(fs.binValuesLine % (tally.usr[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.usr):
						self.mctalOutFile.write("\n")

			if axis == "c" and len(tally.cos) != 0:
				for i in range(len(tally.cos)):
					self.mctalOutFile.write(fs.binValuesLine % (tally.cos[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.cos):
						self.mctalOutFile.write("\n")

			if axis == "e" and len(tally.erg) != 0:
				for i in range(len(tally.erg)):
					self.mctalOutFile.write(fs.binValuesLine % (tally.erg[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.erg):
						self.mctalOutFile.write("\n")

			if axis == "t" and len(tally.tim) != 0:
				for i in range(len(tally.tim)):
					self.mctalOutFile.write(fs.binValuesLine % (tally.tim[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.tim):
						self.mctalOutFile.write("\n")

		self.mctalOutFile.write("\n")

		ii = 0

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

		if len(tally.usr) != 0:
			if tally.usrTC == "t":
				nUsr = nUsr - 1

		if tally.segTC == "t":
			nSeg = nSeg - 1

		if tally.mulTC == "t":
			nMul = nMul - 1

		if len(tally.cos) != 0:
			if tally.cosTC == "t":
				nCos = nCos - 1

		if len(tally.erg) != 0:
			if tally.ergTC == "t":
				nErg = nErg - 1

		if len(tally.tim) != 0:
			if tally.timTC == "t":
				nTim = nTim - 1

		tot = nCells*nDir*nUsr*nSeg*nMul*nCos*nErg*nTim*nCora*nCorb*nCorc

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
													self.mctalOutFile.write(fs.valuesErrorsLine % (tally.getValue(f,d,u,s,m,c,e,t,i,j,k,0),tally.getValue(f,d,u,s,m,c,e,t,i,j,k,1)))
													if (ii+1) % 4 == 0 and (ii+1) != tot:
														self.mctalOutFile.write("\n")
													ii = ii + 1

	def writeRootVals(self):
		"""This function writes the bin and tally values extracted from the ROOT file provided."""

		fs = FormatStrings()

		rF = ROOT.TFile(self.rootFileName)
		tallyList = rF.GetListOfKeys()

		next = ROOT.TIter(tallyList)
		key = next()
		axes = (0,2,5,6,7) # These are the only bins that can have lists of values.
		precision = 1e-9

		while key:
			hs = key.ReadObj()
			tot = hs.GetNbins()
			nBins = [0,0,0,0,0,0,0,0,0,0,0]
			#print "%d" % tot
			for a in range(11):
				nBins[a] = hs.GetAxis(a).GetNbins()


			for a in axes:
				if a == 0 and (nBins[8] > 1 or nBins[9] > 1 or nBins[10] > 1):
					for corABC in range(3):
						axisValues = hs.GetAxis(8 + corABC).GetXbins().GetArray()
						l = 0
						for k in range(nBins[8 + corABC]+1):
							try:
								if k == 0: self.rootOutFile.write("\n")
								self.rootOutFile.write(fs.binValuesLine % axisValues[k])
							except:
								if self.verbose:
									print >> sys.stderr, "%s " % hs.GetTitle() + "k = %5d " % k + "Index out of range for axis %3d. (Skipping without errors)" % (a+1)
							if (l+1) > 0 and (l+1) % 6 == 0 and (l+1) != nBins[8 + corABC]+1:
								self.rootOutFile.write("\n")
							l = l + 1
				else:
					axisValues = hs.GetAxis(a).GetXbins().GetArray()
					for k in range(nBins[a]):
						try:
							if k == 0: self.rootOutFile.write("\n")
							self.rootOutFile.write(fs.binValuesLine % axisValues[k+1])
						except:
							if self.verbose:
								print >> sys.stderr, "%s " % hs.GetTitle() + "k = %5d " % k + "Index out of range for axis %3d. (Skipping without errors)" % (a+1)
						if (k+1) > 0 and (k+1) % 6 == 0 and (k+1) != nBins[a]:
							self.rootOutFile.write("\n")

			self.rootOutFile.write("\n")
			ii = 0


			for f in range(nBins[0]):
				for d in range(nBins[1]):
					for u in range(nBins[2]):
						for s in range(nBins[3]):
							for m in range(nBins[4]):
								for c in range(nBins[5]):
									for e in range(nBins[6]):
										for t in range(nBins[7]):
											for k in range(nBins[10]):
												for j in range(nBins[9]):
													for i in range(nBins[8]):
														val = hs.GetBinContent(array('i',[f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1]))
														absErr = hs.GetBinError(array('i',[f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1]))
														relErr = 0
														if val != 0:
															relErr = absErr/val
														self.rootOutFile.write(fs.valuesErrorsLine % (val,relErr))
														if (ii+1) % 4 == 0 and (ii+1) != tot:
															self.rootOutFile.write("\n")
														ii = ii + 1





			key = next()
			del nBins[:]


	def diffFiles(self):
		"""This function checks whether the files are equal or not."""

		precision = '1.5e-1'

		#f = open('./difflog.txt','a')

		#f.write("\n\n############################################################\n")
		#f.write("ndiff-2.00 --relative-error 1.5e-1 %s %s\n" % (self.mctalOutFile.name,self.rootOutFile.name))
		#f.flush()

		if not subprocess.call(['ndiff-2.00','--relative-error', precision, '--quiet', self.mctalOutFile.name, self.rootOutFile.name],shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
			if self.verbose:
				print "\n\033[1m[TEST PASSED]\033[0m"
			os.remove(self.mctalOutFile.name)
			os.remove(self.rootOutFile.name)
			#f.close()
			return 0
		else:
			if self.verbose:
				print >> sys.stderr, "\n\033[1m[TEST FAILED]\033[0m"
				print >> sys.stderr,  "\033[1mOriginal MCTAL:\033[0m %s - \033[1mTest MCTAL:\033[0m %s" % (self.mctalOutFile.name,self.rootOutFile.name)
				print >> sys.stderr,  "\033[1mTry:\033[0m ndiff-2.00 --relative-error %s %s %s\033[0m\n" % (precision, self.mctalOutFile.name,self.rootOutFile.name)
			else:
				print >> sys.stderr, "\033[1mFAILED FOR FILE: \033[0m%s" % (self.mctalOutFile.name)
				print >> sys.stderr,  "\033[1mTry:\033[0m ndiff-2.00 --relative-error %s %s %s\033[0m\n" % (precision,self.mctalOutFile.name,self.rootOutFile.name)
			#f.close()
			return 1
