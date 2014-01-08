#!/usr/bin/python -W all

import sys
import argparse
from nbmctal import MCTAL
from array import array
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser("Mctal to ROOT conversion script", epilog="Homepage: http://code.google.com/p/mc-tools", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('mctal_file', type=str, help='The name (and path) to the mctal file to be converted')
parser.add_argument('root_file', type=str, nargs='?', help='The name of the converted ROOT file', default="")
parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Explain what is being done')

arguments = parser.parse_args()

m = MCTAL(arguments.mctal_file,arguments.verbose)

T = m.Read()

if arguments.root_file == "":
	rootFileName = "%s%s" % (arguments.mctal_file,".root")
else:
	rootFileName = arguments.root_file

rootFile = ROOT.TFile(rootFileName,"RECREATE");

if arguments.verbose:
	print "\n\033[1m[Converting...]\033[0m"

for tally in T:

	usrAxis = []
	usrAxisCount = None
	cosAxis = []
	cosAxisCount = None
	ergAxis = []
	ergAxisCount = None
	timAxis = []
	timAxisCount = None

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

	if len(tally.usr) != 0:
		if tally.usrTC == "t":
			nUsr = nUsr - 1
		usrAxisCount = nUsr
		u = [0] + tally.usr
		usrAxis = array('d',u)

	if tally.segTC == "t":
		nSeg = nSeg - 1

	if tally.mulTC == "t":
		nMul = nMul - 1

	if len(tally.cos) != 0:
		if tally.cosTC == "t":
			nCos = nCos - 1
		cosAxisCount = nCos
		c = [0] + tally.cos
		cosAxis = array('d',c)

	if len(tally.erg) != 0:
		if tally.ergTC == "t":
			nErg = nErg - 1
		ergAxisCount = nErg
		e = [0] + tally.erg
		ergAxis = array('d',e) 

	if len(tally.tim) != 0:
		if tally.timTC == "t":
			nTim = nTim - 1
		timAxisCount = nTim
		t = [0] + tally.tim
		timAxis = array('d',t)

	bins    = array('i',[nCells,   nDir,   nUsr,   nSeg,   nMul,   nCos,   nErg,   nTim])
	binsMin = array('d',[0,        0,      0,      0,      0,      0,      0,      0])
	binsMax = array('d',[1,        1,      1,      1,      1,      1,      1,      1])

	hs = ROOT.THnSparseF("Tally_%d" % tally.tallyNumber,"Tally: %5d" % tally.tallyNumber,8,bins,binsMin,binsMax)

	#print "+-------------+------------------------------------------+"
	#print "| Tally:%5d | " % tally.tallyNumber + "%5d"*8 % tuple(bins) + " |"

	# Axes must be set here and not with the binsMin and binsMax variables because in case of logarithmic binnings
	# the division would be linear, loosing meaning.

	if len(usrAxis) != 0:
		hs.GetAxis(2).Set(usrAxisCount,usrAxis)

	if len(cosAxis) != 0:
		hs.GetAxis(5).Set(cosAxisCount,cosAxis)

        if len(ergAxis) != 0:
                hs.GetAxis(6).Set(ergAxisCount,ergAxis)

        if len(timAxis) != 0:
                hs.GetAxis(7).Set(timAxisCount,timAxis)

	# Here we store values

	for f in range(nCells):
		for d in range(nDir):
			for u in range(nUsr):
				for s in range(nSeg):
					for m in range(nMul):
						for c in range(nCos):
							for e in range(nErg):
								for t in range(nTim):
									val = tally.getValue(f,d,u,s,m,c,e,t,0)
									err = tally.getValue(f,d,u,s,m,c,e,t,1)
									hs.SetBinContent(array('i',[f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1]), val)
									hs.SetBinError(array('i',[f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1]), val*err)

	hs.Write()
	#rBins = [0,0,0,0,0,0,0,0]
	#for kkk in range(8):
	#	rBins[kkk] = hs.GetAxis(kkk).GetNbins()
	#print "|             | " + "%5d"*8 % tuple(rBins) + " |"
	
	if arguments.verbose:
		print " Tally %5d saved" % (tally.tallyNumber)

rootFile.Close()
print "\n\033[1mROOT file saved to: %s\033[0m\n" % (rootFileName)

