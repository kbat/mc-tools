#! /usr/bin/python -W all

from __future__ import print_function
from sys import argv, exit
import argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def h12ascii(h):
    """ Convert TH1 into text """
    print("#", h.GetXaxis().GetTitle())
    print("#", h.GetYaxis().GetTitle())
    print("#", h.GetZaxis().GetTitle())
    print("# xmin xmax val err")
    nbins = h.GetNbinsX()
    error = 0.0
    for bin in range(1, nbins+1):
        print(h.GetBinLowEdge(bin), h.GetBinLowEdge(bin+1), h.GetBinContent(bin), h.GetBinError(bin))

def h22ascii(h):
    """ Convert TH2 into text """
    print("#", h.GetXaxis().GetTitle())
    print("#", h.GetYaxis().GetTitle())
    print("#", h.GetZaxis().GetTitle())
    print("# xmin xmax ymin ymax val err")
    nbinsx, nbinsy = h.GetNbinsX(), h.GetNbinsY()
    for xbin in range(1, nbinsx+1):
        for ybin in range(1, nbinsy+1):
            x = h.GetXaxis()
            y = h.GetYaxis()
            print(x.GetBinLowEdge(xbin), x.GetBinLowEdge(xbin+1), y.GetBinLowEdge(ybin), y.GetBinLowEdge(ybin+1), h.GetBinContent(xbin, ybin), h.GetBinError(xbin, ybin))

def g2ascii(g):
    """ Convert TGraph and TGraphErrors into text """
    print("#", g.GetXaxis().GetTitle())
    print("#", g.GetYaxis().GetTitle())
    print("# x errx y erry")
    n = g.GetN()
    for i in range(n):
        print(g.GetX()[i], g.GetEX()[i], g.GetY()[i], g.GetEY()[i])

def sparse2ascii(h):
    """ Convert THnSparse into text """
    nbins = h.GetNbins()
    print("# bin val err")
    for b in range(1,nbins+1):
        print(b,h.GetBinContent(b),h.GetBinError(b))

def main():
    """ Converts ROOT objects into ASCII format """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                    epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('fname',   type=str, help='ROOT file name')
    parser.add_argument('objname', type=str, help='Object name')

    args = parser.parse_args()

    f = ROOT.TFile(args.fname)
    obj = f.Get(args.objname)

    if not obj:
        print("%s not found in %s" % (args.objname, args.fname))
        return 1

    print("#", obj.GetName(), obj.GetTitle())

    if obj.InheritsFrom("TH2"):
        h22ascii(obj)
    elif obj.InheritsFrom("TH1"):
        h12ascii(obj)
    elif obj.InheritsFrom("TGraph"):
        g2ascii(obj)
    elif obj.InheritsFrom("THnSparse"):
        sparse2ascii(obj)
    else:
        print("%s: class %s not supported" % (args.objname, obj.ClassName()))

if __name__ == "__main__":
    exit(main())
