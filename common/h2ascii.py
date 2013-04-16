#! /usr/bin/python

from sys import argv, exit
from ROOT import ROOT, TFile, TH1F


def main():
    fname = argv[1]
    hname = argv[2]

    f = TFile(fname)
    h = f.Get(hname)

    nbins = h.GetNbinsX()
    error = 0.0
#    print "#", h.GetName(), h.GetTitle()
#    print "#", h.GetXaxis().GetTitle()
#    print "#", h.GetYaxis().GetTitle()
    for bin in range(1, nbins+1):
#        print h.GetBinLowEdge(bin), h.GetBinLowEdge(bin+1), h.GetBinContent(bin), h.GetBinError(bin)/h.GetBinContent(bin)
        error = 0.0
        if h.GetBinContent(bin) != 0:
            error = h.GetBinError(bin) / h.GetBinContent(bin)

        print h.GetBinLowEdge(bin+1), h.GetBinContent(bin), error

if __name__ == "__main__":
    exit(main())
