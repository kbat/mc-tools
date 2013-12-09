import sys
from nbmctal import MCTAL
from array import array
from ROOT import ROOT, THnSparse, THnSparseF, TFile, TCanvas, TApplication

if len(sys.argv) == 3 and sys.argv[2] == "-v":
        verbose = True
else:
        verbose = False

m = MCTAL(sys.argv[1],verbose)

T = m.Read()

rootT = []
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

	bins = array('i',[nCells,nDir,nUsr,nSeg,nMul,nCos,nErg-1,nTim-1])
	binsMin = array('d',[0,0,0,0,0,0,0,0])
	binsMax = array('d',[nCells-1,nDir-1,nUsr-1,nSeg-1,nMul-1,nCos-1,nErg-2,nTim-2])

	hs = THnSparseF("Tally_%d" % tally.tallyNumber,"Tally: %5d" % tally.tallyNumber,8,bins,binsMin,binsMax)

	hs.GetAxis(6).Set(nErg-2,array('d',tally.erg))
	hs.GetAxis(7).Set(nTim-2,array('d',tally.tim))

	for f in range(nCells):
		for d in range(nDir):
			for u in range(nUsr):
				for s in range(nSeg):
					for m in range(nMul):
						for c in range(nCos):
							for e in range(nErg-1):
								for t in range(nTim-1):
									hs.SetBinContent(array('i',[f,d,u,s,m,c,e,t]), tally.getValue(f,d,u,s,m,c,e,t,0))


	hs.SaveAs(sys.argv[1] + "tally_%d.root" % tally.tallyNumber)


