#! /usr/bin/python
# $Id: ssw2root.py 250 2015-05-04 09:35:55Z batkov $
# $URL: https://github.com/kbat/mc-tools/blob/master/mcnp/ssw2root.py $

import sys, argparse
from ssw import SSW
# from ROOT import TFile, TTree, gROOT
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

ROOT.gROOT.ProcessLine(
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
    """
    Converts SSW binary to the ROOT format as a TTree object
    """

    allowed_splitlevels = (1, 99)
    parser = argparse.ArgumentParser(description=main.__doc__, epilog='Homepage: https://github.com/kbat/mc-tools')
    parser.add_argument('-splitlevel', dest='splitlevel', type=int, help='split level (see TTree::Branch documentation)', required=False, default=1, choices=allowed_splitlevels)
    parser.add_argument('wssa', type=str, help='ssw output file name')
    arguments = parser.parse_args()

    fin_name = arguments.wssa
    fout_name = fin_name + ".root"

    hits = ROOT.hit_t()

    ssw = SSW(fin_name)

    fout = ROOT.TFile(fout_name, "recreate", ssw.getTitle())
    T = ROOT.TTree("T", ssw.probs)
#    T.SetMaxTreeSize((Long64_t)1e+18)

    if arguments.splitlevel==99:
        T.Branch("hits", hits, "history:id:weight:energy:time:x:y:z:wx:wy:k")
    elif arguments.splitlevel == 1:
        T.Branch("history", ROOT.AddressOf(hits, 'history'), "history")
        T.Branch("id",      ROOT.AddressOf(hits, 'id'),      "id")
        T.Branch("weight",  ROOT.AddressOf(hits, 'weight'),  "weight")
        T.Branch("energy",  ROOT.AddressOf(hits, 'energy'),  "energy")
        T.Branch("time",    ROOT.AddressOf(hits, 'time'),    "time")
        T.Branch("x",       ROOT.AddressOf(hits, 'x'),       "x")
        T.Branch("y",       ROOT.AddressOf(hits, 'y'),       "y")
        T.Branch("z",       ROOT.AddressOf(hits, 'z'),       "z")
        T.Branch("wx",      ROOT.AddressOf(hits, 'wx'),      "wx")
        T.Branch("wy",      ROOT.AddressOf(hits, 'wy'),      "wy")
        T.Branch("k",       ROOT.AddressOf(hits, 'k'),       "k")

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
        
    sinfo = ROOT.TObjString("%d" % ssw.N); # number of incident particles for correct normalisation
    T.GetUserInfo().Add(sinfo);

    T.Print()
    T.SetAlias("theta", "TMath::RadToDeg()*(TMath::ATan2(x,y) > 0 ? TMath::ATan2(x,y) : 2*TMath::Pi()+TMath::ATan2(x,y))");
    T.SetAlias("i","TMath::Nint(TMath::Abs(id/1E+6))"); # tmp for particle type
    T.SetAlias("JGP","-TMath::Nint(i/200.0)");         # energy group
    T.SetAlias("JC","TMath::Nint(i/100.0) + 2*JGP");   #
    T.SetAlias("IPT","i-100*JC+200*JGP");              # particle type: 1=neutron, 2=photon, 3=electron
    T.SetAlias("wz", "TMath::Sqrt(TMath::Max(0, 1-wx*wx-wy*wy)) * id/TMath::Abs(id)") # z-direction cosine
    T.SetAlias("surface", "TMath::Abs(id) % 1000000") # surface crossed
    T.Write()
    fout.Purge()
    fout.Close()

if __name__ == "__main__":
	sys.exit(main())
