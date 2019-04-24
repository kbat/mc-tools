#! /usr/bin/python2 -W all
import time
import subprocess
import tempfile
import os,sys,math
import numpy as np
from testsuite import FormatStrings
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
		self.precision = ("1.5e-3","1.5e-1","1")

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

			if tally.mesh == True and axis == "i":
				self.mctalOutFile.write("\n")
				for i in range(tally.meshInfo[1]+1):
					self.mctalOutFile.write(fs.binValuesLine % (tally.cora[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[1]:
						self.mctalOutFile.write("\n")

			if tally.mesh == True and axis == "j":
				self.mctalOutFile.write("\n")
				for i in range(tally.meshInfo[2]+1):
					self.mctalOutFile.write(fs.binValuesLine % (tally.corb[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[2]:
						self.mctalOutFile.write("\n")

			if tally.mesh == True and axis == "k":
				self.mctalOutFile.write("\n")
				for i in range(tally.meshInfo[3]+1):
					self.mctalOutFile.write(fs.binValuesLine % (tally.corc[i]))
					if i > 0 and (i+1) % 6 == 0 and i != tally.meshInfo[3]:
						self.mctalOutFile.write("\n")

			if axis == "u" or axis == "s" or axis == "c" or axis == "e" or axis == "t":
				self.mctalOutFile.write("\n")

			if axis == "s" and len(tally.seg) != 0:
				for i in range(len(tally.seg)):
					self.mctalOutFile.write(fs.binValuesLine % (tally.seg[i]))
					if i > 0 and (i+1) % 6 == 0 and (i+1) != len(tally.seg):
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

		nCells = tally.getNbins("f",False)
		nCora  = tally.getNbins("i",False)
		nCorb  = tally.getNbins("j",False)
		nCorc  = tally.getNbins("k",False)
		nDir   = tally.getNbins("d",False)
		nUsr   = tally.getNbins("u",False)
		nSeg   = tally.getNbins("s",False)
		nMul   = tally.getNbins("m",False)
		nCos   = tally.getNbins("c",False)
		nErg   = tally.getNbins("e",False)
		nTim   = tally.getNbins("t",False)

		tot = tally.getTotNumber(False)

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
		axes = (2,3,5,6,7,8,9,10) # These are the only bins that can have lists of values.

		while key:
			hs = key.ReadObj()

			objectName = hs.GetName()
			radio = False # By default we don't have either radiograph...
			mesh = False  # ...or mesh tallies
			if "tir" in objectName or "tic" in objectName or "pi" in objectName: # We have a radiograph tally
				radio = True
			elif "mesh" in objectName: # We have a mesh tally
				mesh = True

			tot = hs.GetNbins()
			nBins = [1,1,1,1,1,1,1,1,1,1,1]
			dims = hs.GetNdimensions()
			for a in range(dims):
				nBins[a] = hs.GetAxis(a).GetNbins()

			for a in axes:
				if a >= 8 and not mesh:
					break 
				axisValues = hs.GetAxis(a).GetXbins().GetArray()
				nB = nBins[a]
				if a >= 8 or (radio and (a == 3 or a == 5)):
					nB = nBins[a] + 1
				for k in range(nB):
					kk = k + 1
					if a >= 8 or (radio and (a == 3 or a == 5)):
						kk = k
					try:
						if k == 0: self.rootOutFile.write("\n")
						self.rootOutFile.write(fs.binValuesLine % axisValues[kk])
					except:
						if self.verbose:
							print >> sys.stderr, "\033[1;30m %s " % hs.GetTitle() + "k = %5d " % kk + "Index out of range for axis %3d. (Skipping without errors)\033[0m" % (a+1)
						break
					if (k+1) > 0 and (k+1) % 6 == 0 and (k+1) != nB:
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
														if dims == 11:
															val = hs.GetBinContent(np.array([f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1], dtype=np.dtype('i4')))
															absErr = hs.GetBinError(np.array([f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1], dtype=np.dtype('i4')))
														else:
															val = hs.GetBinContent(np.array([f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1], dtype=np.dtype('i4')))
															absErr = hs.GetBinError(np.array([f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1], dtype=np.dtype('i4')))
														relErr = 0
														if val != 0:
															relErr = math.fabs(absErr/val)
														self.rootOutFile.write(fs.valuesErrorsLine % (val,relErr))
														if (ii+1) % 4 == 0 and (ii+1) != tot:
															self.rootOutFile.write("\n")
														ii = ii + 1





			key = next()
			del nBins[:]


	def diffFiles(self):
		"""This function checks whether the files are equal or not."""

		f = open('./difflog.txt','a')
		f.write("Run: " + time.strftime("%d/%m/%Y") + " - " + time.strftime("%H:%M:%S") + "\n")
		f.flush()

		for i in range(3):
			if self.verbose or i == 2:
				if i == 2:
					pre_text = "\n\033[1;31m[* WARNING *]\033[0m\033[31m"
					post_text = " - \033[1;31mLOGGED to difflog.txt\033[0m\n\033[1;31m[* WARNING *] \033[0m\033[31mWith this precision the test will succeed anyway.\n"
				else:
					pre_text = "\033[33m"
					post_text = "\033[0m"
				print "%s Testing with relative error: %s%s" % (pre_text,self.precision[i],post_text)
				if i == 2:
					print >> sys.stderr,  "\033[1;31m Try:\033[0m\033[31m ndiff-2.00 --relative-error %s %s %s\033[0m\n" % (self.precision[1],self.mctalOutFile.name,self.rootOutFile.name)
					f.write("\tndiff-2.00 --relative-error %s %s %s\n" % (self.precision[1],self.mctalOutFile.name,self.rootOutFile.name))
					f.flush
			if not subprocess.call(['ndiff-2.00','--relative-error', self.precision[i], '--quiet', self.mctalOutFile.name, self.rootOutFile.name],shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT):
				if self.verbose:
					print "\n\033[1;32m[TEST PASSED]\033[0m\n"
				if i < 2:
					os.remove(self.mctalOutFile.name)
					os.remove(self.rootOutFile.name)
				f.close()
				return 0
		if self.verbose:
			print >> sys.stderr, "\n\033[1;31m[TEST FAILED]\033[0m"
			print >> sys.stderr,  "\033[1;31m Original MCTAL:\033[31m %s - \033[1;31mTest MCTAL:\033[31m %s\033[0m" % (self.mctalOutFile.name,self.rootOutFile.name)
			print >> sys.stderr,  "\033[1;31m Try:\033[31m ndiff-2.00 --relative-error %s %s %s\033[0m\n" % (self.precision[1], self.mctalOutFile.name,self.rootOutFile.name)
		else:
			print >> sys.stderr, "\033[1;31mFAILED FOR FILE: \033[0m%s" % (self.mctalOutFile.name)
			print >> sys.stderr,  "\033[1;31m Try:\033[0m\033[31m ndiff-2.00 --relative-error %s %s %s\033[0m\n" % (self.precision[1],self.mctalOutFile.name,self.rootOutFile.name)
		f.close()
		return 1
