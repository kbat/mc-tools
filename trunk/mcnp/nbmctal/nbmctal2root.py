#!/usr/bin/python -W all

import sys, argparse, string
from nbmctal import MCTAL
from array import array
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description="A mctal to ROOT conversion script.", 
				 epilog="Homepage: http://code.google.com/p/mc-tools")
parser.add_argument('mctal_file', type=str, help='the name of the mctal file to be converted')
parser.add_argument('root_file', type=str, nargs='?', help='the name of the output ROOT file', default="")
parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

arguments = parser.parse_args()

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

	nCells = tally.getNbins("f")

	coraAxis = tally.getAxis("i")
	nCora = tally.getNbins("i") # Is set to 1 even when mesh tallies are not present

	corbAxis = tally.getAxis("j")
	nCorb = tally.getNbins("j") # Is set to 1 even when mesh tallies are not present

	corcAxis = tally.getAxis("k")
	nCorc = tally.getNbins("k") # Is set to 1 even when mesh tallies are not present

	nDir = tally.getNbins("d")

	usrAxis = tally.getAxis("u")
	nUsr = tally.getNbins("u")

	nSeg = tally.getNbins("s")

	nMul = tally.getNbins("m")

	cosAxis = tally.getAxis("c")
	nCos = tally.getNbins("c")

	ergAxis = tally.getAxis("e")
	nErg = tally.getNbins("e")

	timAxis = tally.getAxis("t")
	nTim = tally.getNbins("t")

	if tally.mesh == True:

		bins    = array('i', (nCells,   nDir,   nUsr,   nSeg,   nMul,   nCos,   nErg,   nTim,   nCora,   nCorb,   nCorc))
		binsMin = array('d', (0,        0,      0,      0,      0,      0,      0,      0,      0,       0,       0))
		binsMax = array('d', (1,        1,      1,      1,      1,      1,      1,      1,      1,       1,       1))

		hs = ROOT.THnSparseF("f%d" % tally.tallyNumber, string.join(tally.tallyComment).strip(), 11, bins, binsMin, binsMax)

	else:

		bins    = array('i', (nCells,   nDir,   nUsr,   nSeg,   nMul,   nCos,   nErg,   nTim))
		binsMin = array('d', (0,        0,      0,      0,      0,      0,      0,      0))
		binsMax = array('d', (1,        1,      1,      1,      1,      1,      1,      1))

		hs = ROOT.THnSparseF("f%d" % tally.tallyNumber, string.join(tally.tallyComment).strip(), 8, bins, binsMin, binsMax)



	if len(usrAxis) != 0:
		hs.GetAxis(2).Set(nUsr,usrAxis)

	if len(cosAxis) != 0:
		hs.GetAxis(5).Set(nCos,cosAxis)

	if len(ergAxis) != 0:
		hs.GetAxis(6).Set(nErg,ergAxis)

	if len(timAxis) != 0:
		hs.GetAxis(7).Set(nTim,timAxis)

	if tally.mesh == True:
		hs.GetAxis(8).Set(len(coraAxis)-1,coraAxis)
		hs.GetAxis(9).Set(len(corbAxis)-1,corbAxis)
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
												if tally.mesh == True:
													hs.SetBinContent(array('i',[f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1]), val)
													hs.SetBinError(array('i',[f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1]), val*err)
												else:
													hs.SetBinContent(array('i',[f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1]), val)
													hs.SetBinError(array('i',[f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1]), val*err)



	for i, name in enumerate(tally.binIndexList):
		if i >= 8 and tally.mesh == False:
			break
		hs.GetAxis(i).SetNameTitle(name, name)

	hs.Write()

	if arguments.verbose:
		print " \033[33mTally %5d saved\033[0m" % (tally.tallyNumber)


rootFile.Close()
print "\n\033[1;34mROOT file saved to:\033[1;32m %s\033[0m\n" % (rootFileName)

