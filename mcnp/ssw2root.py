#! /usr/bin/python
# $Id$

import sys
from ssw import SSW
# from ROOT import TFile, TTree, gROOT
from ROOT import *

gROOT.ProcessLine(
"struct hit_t {\
   Float_t history;\
   Float_t id;\
   Float_t weight;\
   Float_t energy;\
   Float_t time;\
   Float_t x;\
   Float_t y;\
   Float_t z;\
   Float_t wx;\
   Float_t wy;\
   Float_t k;\
};" );


def main():
    """ Converts SSW binary to the ROOT format as a TTree object"""
    if len(sys.argv) != 2:
        print "Usage: ssw2root.py rssa"
        sys.exit(1)

    fin_name = sys.argv[1]
    fout_name = fin_name + ".root"

    hits = hit_t()

    ssw = SSW(fin_name)

    fout = TFile(fout_name, "recreate")
    T = TTree("T", ssw.getTitle())
    T.Branch("hits", hits, "history:id:weight:energy:time:x:y:z:wx:wy:k")

    print "Number of hits:", ssw.nevt
    for i in range(ssw.nevt):
        ssb = ssw.readHit()
#        print >>fout,  " ".join(map(str, ssb))
        hits.history = ssb[0]
	hits.id = ssb[1]
	hits.weight = ssb[2]
	hits.energy = ssb[3]
	hits.time = ssb[4]
	hits.x = ssb[5]
	hits.y = ssb[6]
	hits.z = ssb[7]
	hits.wx = ssb[8]
	hits.wy = ssb[9]
	hits.k = ssb[10]
	T.Fill()

    T.Print()
    T.SetAlias("theta", "TMath::RadToDeg()*(TMath::ATan2(x,z) > 0 ? TMath::ATan2(x,z) : 2*TMath::Pi()+TMath::ATan2(x,z))");
    T.SetAlias("ID","int(abs(id/1E+6))");
    T.Write()


if __name__ == "__main__":
	sys.exit(main())
