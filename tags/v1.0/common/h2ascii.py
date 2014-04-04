#! /usr/bin/python

from sys import argv, exit
from ROOT import ROOT, TFile, TH1, TH2, TH3


def main():
    """ See also the Print(TObject *) function in .rootalias"""
    fname = argv[1]
    hname = argv[2]

    f = TFile(fname)
    h = f.Get(hname)
    print "#", h.GetName(), h.GetTitle()
    print "#", h.GetXaxis().GetTitle()
    print "#", h.GetYaxis().GetTitle()
    print "#", h.GetZaxis().GetTitle()
    print "# xmin xmax y y_rel_error"

    if h.InheritsFrom("TH2"):
        nbinsx, nbinsy = h.GetNbinsX(), h.GetNbinsY()
#        print nbinsx, nbinsy
        for xbin in range(1, nbinsx+1):
            for ybin in range(1, nbinsy+1):
                error = 0.0
                val = h.GetBinContent(xbin, ybin)
                if val != 0:  error = h.GetBinError(xbin, ybin) / val
                print h.GetXaxis().GetBinLowEdge(xbin), h.GetXaxis().GetBinLowEdge(xbin+1), h.GetYaxis().GetBinLowEdge(ybin), h.GetYaxis().GetBinLowEdge(ybin+1), val, error
            
    elif h.InheritsFrom("TH1"):
        nbins = h.GetNbinsX()
        error = 0.0
        for bin in range(1, nbins+1):
            #        print h.GetBinLowEdge(bin), h.GetBinLowEdge(bin+1), h.GetBinContent(bin), h.GetBinError(bin)/h.GetBinContent(bin)
            error = 0.0
            if h.GetBinContent(bin) != 0:  error = h.GetBinError(bin) / h.GetBinContent(bin)
            print h.GetBinLowEdge(bin), h.GetBinLowEdge(bin+1), h.GetBinContent(bin), error

if __name__ == "__main__":
    exit(main())
