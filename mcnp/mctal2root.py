#!/usr/bin/python -W all

import sys, argparse, string
from os import path
from mctal import MCTAL
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
sys.path.insert(1, '@pythondir@')

parser = argparse.ArgumentParser(description="A mctal to ROOT conversion script.", 
				 epilog="Homepage: http://code.google.com/p/mc-tools")
parser.add_argument('mctal_file', type=str, help='the name of the mctal file to be converted')
parser.add_argument('root_file', type=str, nargs='?', help='the name of the output ROOT file', default="")
parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

arguments = parser.parse_args()

if not path.isfile(arguments.mctal_file):
	print >> sys.stderr, "mctal2root: File %s does not exist." % arguments.mctal_file
	sys.exit(1)

m = MCTAL(arguments.mctal_file,arguments.verbose)

T = m.Read()

if m.thereAreNaNs:
	print >> sys.stderr, " \033[1;30mOne or more tallies contain NaN values. Conversion will succeed anyway.\033[0m"

if arguments.root_file == "":
	rootFileName = "%s%s" % (arguments.mctal_file,".root")
else:
	rootFileName = arguments.root_file

rootFile = ROOT.TFile(rootFileName,"RECREATE");

if arguments.verbose:
	print "\n\033[1;34m[Converting...]\033[0m"

for tally in T:

	tallyLetter = "f"
	if tally.radiograph:
		tallyLetter = tally.getDetectorType(True) # Here the argument set to True enables the short version of the tally type
	if tally.mesh:
		tallyLetter = tally.getDetectorType(True)

	nCells = tally.getNbins("f",False)

	nCora = tally.getNbins("i",False) # Is set to 1 even when mesh tallies are not present

	nCorb = tally.getNbins("j",False) # Is set to 1 even when mesh tallies are not present

	nCorc = tally.getNbins("k",False) # Is set to 1 even when mesh tallies are not present

	nDir = tally.getNbins("d",False)

	usrAxis = tally.getAxis("u")
	nUsr = tally.getNbins("u",False)

	segAxis = tally.getAxis("s")
	nSeg = tally.getNbins("s",False)

	nMul = tally.getNbins("m",False)

	cosAxis = tally.getAxis("c")
	nCos = tally.getNbins("c",False)

	ergAxis = tally.getAxis("e")
	nErg = tally.getNbins("e",False)

	timAxis = tally.getAxis("t")
	nTim = tally.getNbins("t",False)

	if tally.mesh == True:

		bins    = np.array( [nCells,   nDir,   nUsr,   nSeg,   nMul,   nCos,   nErg,   nTim,   nCora,   nCorb,   nCorc], dtype=np.dtype('i4') )
		binsMin = np.array( [0.,        0.,      0.,      0.,      0.,      0.,      0.,      0.,      0.,       0.,       0.] )
		binsMax = np.array( [1.,        1.,      1.,      1.,      1.,      1.,      1.,      1.,      1.,       1.,       1.] )

		hs = ROOT.THnSparseF("%s%d" % (tallyLetter, tally.tallyNumber), string.join(tally.tallyComment.tolist()).strip(), 11, bins, binsMin, binsMax)

	else:

		bins    = np.array( [nCells,   nDir,   nUsr,   nSeg,   nMul,   nCos,   nErg,   nTim], dtype=np.dtype('i4'))
		binsMin = np.array( [0,        0,      0,      0,      0,      0,      0,      0], dtype=float)
		binsMax = np.array( [1,        1,      1,      1,      1,      1,      1,      1], dtype=float)

		hs = ROOT.THnSparseF("%s%d" % (tallyLetter, tally.tallyNumber), string.join(tally.tallyComment.tolist()).strip(), 8, bins, binsMin, binsMax)



	if len(usrAxis) != 0:
		hs.GetAxis(2).Set(nUsr,usrAxis)

	if len(segAxis) != 0:
		hs.GetAxis(3).Set(nSeg,segAxis)

	if len(cosAxis) != 0:
		hs.GetAxis(5).Set(nCos,cosAxis)

	if len(ergAxis) != 0:
		hs.GetAxis(6).Set(nErg,ergAxis)

	if len(timAxis) != 0:
		hs.GetAxis(7).Set(nTim,timAxis)

	if tally.mesh == True:
		coraAxis = tally.getAxis("i")
		hs.GetAxis(8).Set(len(coraAxis)-1,coraAxis)

		corbAxis = tally.getAxis("j")
		hs.GetAxis(9).Set(len(corbAxis)-1,corbAxis)

		corcAxis = tally.getAxis("k")
		hs.GetAxis(10).Set(len(corcAxis)-1,corcAxis)

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
												val = tally.getValue(f,d,u,s,m,c,e,t,i,j,k,0)
												err = tally.getValue(f,d,u,s,m,c,e,t,i,j,k,1)

												#print "%5d - %5d - %5d - %5d - %5d - %5d - %5d - %5d - %5d - %5d - %5d - %13.5E" % (f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1,val)

												if tally.mesh == True:
													hs.SetBinContent(np.array([f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1],dtype=np.dtype('i4')), val)
													hs.SetBinError(np.array([f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1],dtype=np.dtype('i4')), val*err)
												else:
													hs.SetBinContent(np.array([f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1],dtype=np.dtype('i4')), val)
													hs.SetBinError(np.array([f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1],dtype=np.dtype('i4')), val*err)


	for i, name in enumerate(tally.binIndexList):
		if i >= 8 and tally.mesh == False:
			break
		hs.GetAxis(i).SetNameTitle(name, name)

	hs.Write()

	if arguments.verbose:
		print " \033[33mTally %5d saved\033[0m" % (tally.tallyNumber)


rootFile.Close()
print "\n\033[1;34mROOT file saved to:\033[1;32m %s\033[0m\n" % (rootFileName)

