import sys
import time
from nbmctal import MCTAL
from array import array
from ROOT import ROOT, THnSparse, THnSparseF, TFile

if len(sys.argv) == 3 and sys.argv[2] == "-v":
        verbose = True
else:
        verbose = False

m = MCTAL(sys.argv[1],verbose)

T = m.Read()

rootFileName = "%s_%s-%s%s" % (sys.argv[1],time.strftime("%Y%m%d"),time.strftime("%H%M%S"),".root")

rootFile = TFile(rootFileName,"RECREATE");

i = 0

usrAxis = []
usrAxisCount = None
cosAxis = []
cosAxisCount = None
ergAxis = []
ergAxisCount = None
timAxis = []
timAxisCount = None


if verbose:
	print "\n\033[1m[Converting...]\033[0m"

for tally in T:
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
		usrAxisCount = nUsr - 1
		usrAxis = array('d',tally.usr)

	if tally.segTC == "t":
		nSeg = nSeg - 1

	if tally.mulTC == "t":
		nMul = nMul - 1

	if len(tally.cos) != 0:
		if tally.cosTC == "t":
			nCos = nCos - 1
		cosAxisCount = nCos - 1
		cosAxis = array('d',tally.cos)

	if len(tally.erg) != 0:
		if tally.ergTC == "t":
			nErg = nErg - 1
		ergAxisCount = nErg - 1
		ergAxis = array('d',tally.erg) 

	if len(tally.tim) != 0:
		if tally.timTC == "t":
			nTim = nTim - 1
		timAxisCount = nTim - 1
		timAxis = array('d',tally.tim)

	bins    = array('i',[nCells,   nDir,   nUsr,   nSeg,   nMul,   nCos,   nErg,   nTim])
	binsMin = array('d',[0,        0,      0,      0,      0,      0,      0,      0])
	binsMax = array('d',[nCells-1, nDir-1, nUsr-1, nSeg-1, nMul-1, nCos-1, nErg-1, nTim-1])

	hs = THnSparseF("Tally_%d" % tally.tallyNumber,"Tally: %5d" % tally.tallyNumber,8,bins,binsMin,binsMax)

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
									hs.SetBinContent(array('i',[f,d,u,s,m,c,e,t]), tally.getValue(f,d,u,s,m,c,e,t,0))


	hs.Write()
	if verbose:
		print " Tally %5d saved" % (tally.tallyNumber)
	i = i + 1

rootFile.Close()
print "\n\033[1mROOT file saved to: %s\033[0m\n" % (rootFileName)

