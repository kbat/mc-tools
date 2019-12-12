#! /usr/bin/python2 -W all

from __future__ import print_function
from sys import argv, exit
import argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """ Converts TH[12] and TGraphErrors into ASCII format"""

    parser = argparse.ArgumentParser
       (description=main.__doc__,epilog="Homepage: https://github.com/kbat/mc-tools")
       
    parser.add_argument('fname', type=str, help='ROOT file name')
    parser.add_argument('hname', type=str, help='Object name')

    args = parser.parse_args()

    fname = args.fname
    hname = args.hname

    f = ROOT.TFile(fname)
    h = f.Get(hname)
    print("#", h.GetName(), h.GetTitle())
    print("#", h.GetXaxis().GetTitle())
    print("#", h.GetYaxis().GetTitle())
    if h.InheritsFrom("TH1") or h.InheritsFrom("TH2"):
        print("#", h.GetZaxis().GetTitle())
        print("# xmin xmax y y_abs_error")
    elif h.InheritsFrom("TGraph"):
        print("# x x_abs_err y y_abs_err")

    if h.InheritsFrom("TH2"):
        nbinsx, nbinsy = h.GetNbinsX(), h.GetNbinsY()
#        print(nbinsx, nbinsy)
        for xbin in range(1, nbinsx+1):
            for ybin in range(1, nbinsy+1):
                error = 0.0
                val = h.GetBinContent(xbin, ybin)
                if val != 0:  error = h.GetBinError(xbin, ybin) 
                print(h.GetXaxis().GetBinLowEdge(xbin), h.GetXaxis().GetBinLowEdge(xbin+1), h.GetYaxis().GetBinLowEdge(ybin), h.GetYaxis().GetBinLowEdge(ybin+1), val, error)

    elif h.InheritsFrom("TH1"):
        nbins = h.GetNbinsX()
        error = 0.0
        for bin in range(1, nbins+1):
            #        print(h.GetBinLowEdge(bin), h.GetBinLowEdge(bin+1), h.GetBinContent(bin), h.GetBinError(bin)/h.GetBinContent(bin))
            error = 0.0
            if h.GetBinContent(bin) != 0:  error = h.GetBinError(bin) / h.GetBinContent(bin)
            print(h.GetBinLowEdge(bin), h.GetBinLowEdge(bin+1), h.GetBinContent(bin), error)
    elif h.InheritsFrom("TGraph"):
        n = h.GetN()
        for i in range(n):
            print(i, h.GetX()[i], h.GetEX()[i], h.GetY()[i], h.GetEY()[i])

if __name__ == "__main__":
    exit(main())
