#!/usr/bin/env python3
# https://github.com/kbat/mc-tools
#

import sys, argparse
from mctools.mcnp.ssw import SSW
# from ROOT import TFile, TTree, gROOT
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

ROOT.gROOT.ProcessLine(
"struct fhit_t {\
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

ROOT.gROOT.ProcessLine(
"struct ihit_t {\
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
   Int_t k;\
};" );


def main():
    """
    Converts SSW binary to the ROOT format as a TTree object
    """

    allowed_splitlevels = (1, 99)
    parser = argparse.ArgumentParser(description=main.__doc__, epilog='Homepage: https://github.com/kbat/mc-tools')
    parser.add_argument('-splitlevel', dest='splitlevel', type=int, help='split level (see TTree::Branch documentation)', required=False, default=1, choices=allowed_splitlevels)
    parser.add_argument('wssa', type=str, help='ssw output file name')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')
    parser.add_argument('-d', '--debug', action='store_true', default=False, dest='debug', help='print debug messages')
    args = parser.parse_args()

    fin_name = args.wssa
    fout_name = fin_name + ".root"

    ssw = SSW(fin_name, args.verbose, args.debug)

    if ssw.mcnp6 and ssw.isMacroBody:
        hits = ROOT.fhit_t()
    else:
        hits = ROOT.ihit_t()

    fout = ROOT.TFile(fout_name, "recreate", ssw.getTitle())
    T = ROOT.TTree("T", ssw.probs)
#    T.SetMaxTreeSize((Long64_t)1e+18)

    if args.splitlevel==99:
        if ssw.mcnp6:
            if ssw.isMacroBody:
                T.Branch("hits", hits, "history:id:weight:energy:time:x:y:z:wx:wy:surface")
            else:
                T.Branch("hits", hits, "history:id:weight:energy:time:x:y:z:wx:wy:surface/I")
        else:
            T.Branch("hits", hits, "history:id:weight:energy:time:x:y:z:wx:wy:k")
    elif args.splitlevel == 1:
        T.Branch("history", ROOT.addressof(hits, 'history'), "history")
        T.Branch("id",      ROOT.addressof(hits, 'id'),      "id")
        T.Branch("weight",  ROOT.addressof(hits, 'weight'),  "weight")
        T.Branch("energy",  ROOT.addressof(hits, 'energy'),  "energy")
        T.Branch("time",    ROOT.addressof(hits, 'time'),    "time")
        T.Branch("x",       ROOT.addressof(hits, 'x'),       "x")
        T.Branch("y",       ROOT.addressof(hits, 'y'),       "y")
        T.Branch("z",       ROOT.addressof(hits, 'z'),       "z")
        T.Branch("wx",      ROOT.addressof(hits, 'wx'),      "wx")
        T.Branch("wy",      ROOT.addressof(hits, 'wy'),      "wy")
        if ssw.mcnp6:
            if ssw.isMacroBody:
                T.Branch("surface", ROOT.addressof(hits, 'k'),"surface")
            else:
                T.Branch("surface", ROOT.addressof(hits, 'k'),"surface/I")
        else:
            T.Branch("k",       ROOT.addressof(hits, 'k'),       "k")

    for i in range(ssw.getNTracks()):
        ssb = ssw.readHit()
        hits.history = ssb[0] # >0 = with collision, <0 = without collision
        hits.id = ssb[1] # if not ssw.mcnp6: surface + particle type + multigroup problem info; if ssw.mcnp6: packed variable 'b' in la-ur-16-20109 (z-direction sign+particle type), see section 4.7
        hits.weight = ssb[2]
        hits.energy = ssb[3] # [MeV]
        hits.time = ssb[4] # [shakes]
        hits.x = ssb[5] # [cm]
        hits.y = ssb[6] # [cm]
        hits.z = ssb[7] # [cm]
        hits.wx = ssb[8]
        hits.wy = ssb[9]
        if ssw.mcnp6:
            if ssw.isMacroBody:
                hits.k = ssb[10]
            else:
                hits.k = round(ssb[10])
        else:
            hits.k = ssb[10] # if not ssw.mcnp6: cosine of angle between track and normal to surface jsu (in MCNPX it is called cs); if ssw.mcnp6: surface number (see section 4.7 in la-ur-16-20109)
        T.Fill()
#        print(hits.history, hits.id, hits.weight, hits.energy, hits.wx)

    ssw.file.close()

    sinfo = ROOT.TObjString("%d" % ssw.N); # number of incident particles for correct normalisation
    T.GetUserInfo().Add(sinfo);

#    T.Print()
    T.SetAlias("theta", "TMath::RadToDeg()*(TMath::ATan2(x,y) > 0 ? TMath::ATan2(x,y) : 2*TMath::Pi()+TMath::ATan2(x,y))");
    T.SetAlias("wz", "TMath::Sqrt(TMath::Max(0.0, 1.0-wx*wx-wy*wy)) * ((id>0)-(id<0))") # z-direction cosine, ((id>0)-(id<0)) = sign(id)
    if ssw.mcnp6:
        T.SetAlias("particle", "TMath::Nint(TMath::Abs(id/8))") # sec 4.7 in la-ur-16-20109
    else:
        T.SetAlias("surface", "TMath::Abs(id) % 1000000")  # surface crossed
        T.SetAlias("i","TMath::Nint(TMath::Abs(id/1E+6))");# tmp variable
        T.SetAlias("JGP","-TMath::Nint(i/200.0)");         # energy group
        T.SetAlias("JC","TMath::Nint(i/100.0) + 2*JGP");   #
        T.SetAlias("particle","i-100*JC+200*JGP"); # particle type: 1=neutron, 2=photon, 3=electron
    T.Write()
    fout.Purge()
    fout.Close()

if __name__ == "__main__":
        sys.exit(main())
