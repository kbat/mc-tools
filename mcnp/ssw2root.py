#! /usr/bin/python
# $Id$
# $URL$

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

    fout = TFile(fout_name, "recreate", ssw.getTitle())
    T = TTree("T", ssw.probs)
#    T.SetMaxTreeSize((Long64_t)1e+18)
    splitlevel = 1
    if splitlevel==99:
        T.Branch("hits", hits, "history:id:weight:energy:time:x:y:z:wx:wy:k")
    elif splitlevel == 1:
        T.Branch("history", AddressOf(hits, 'history'), "history")
        T.Branch("id", AddressOf(hits, 'id'), "id")
        T.Branch("weight", AddressOf(hits, 'weight'), "weight")
        T.Branch("energy", AddressOf(hits, 'energy'), "energy")
        T.Branch("time", AddressOf(hits, 'time'), "time")
        T.Branch("x", AddressOf(hits, 'x'), "x")
        T.Branch("y", AddressOf(hits, 'y'), "y")
        T.Branch("z", AddressOf(hits, 'z'), "z")
        T.Branch("wx", AddressOf(hits, 'wx'), "wx")
        T.Branch("wy", AddressOf(hits, 'wy'), "wy")
        T.Branch("k", AddressOf(hits, 'k'), "k")



    for i in range(ssw.nevt):
        ssb = ssw.readHit()
        hits.history = ssb[0] # >0 = with collision, <0 = without collision
        hits.id = ssb[1] # surface + particle type + multigroup problem info
        hits.weight = ssb[2]
        hits.energy = ssb[3] # [MeV]
        hits.time = ssb[4] # [shakes]
        hits.x = ssb[5] # [cm]
        hits.y = ssb[6] # [cm]
        hits.z = ssb[7] # [cm]
        hits.wx = ssb[8]
        hits.wy = ssb[9]
        hits.k = ssb[10] # cosine of angle between track and normal to surface jsu (in MCNPX it is called cs)
        T.Fill()

    T.Print()
    T.SetAlias("theta", "TMath::RadToDeg()*(TMath::ATan2(x,z) > 0 ? TMath::ATan2(x,z) : 2*TMath::Pi()+TMath::ATan2(x,z))");
    T.SetAlias("i","TMath::Nint(TMath::Abs(id/1E+6))"); # tmp for particle type
    T.SetAlias("JGP","-TMath::Nint(i/200.0)");         # energy group
    T.SetAlias("JC","TMath::Nint(i/100.0) + 2*JGP");   #
    T.SetAlias("IPT","i-100*JC+200*JGP");              # particle type: 1=neutron, 2=photon, 3=electron
    T.SetAlias("wz", "TMath::Sqrt(TMath::Max(0, 1-wx*wx-wy*wy)) * id/TMath::Abs(id)") # z-direction cosine
    T.SetAlias("surface", "TMath::Abs(id)-1000000") # surface crossed
    T.Write()


if __name__ == "__main__":
	sys.exit(main())
