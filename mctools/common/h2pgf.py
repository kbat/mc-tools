#! /usr/bin/python -W all
#

import sys, argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def h2pgf(h):
    """ Convert TH1 into pgfplot data with error bars
    input: xmin xmax y ey
    output: x ex y ey
    ex = (xmax+xmin)/2
    """
    nbins = h.GetNbinsX()

#    print "# \\begin{axis}"
#    print "# \\addplot[const plot mark mid, black, solid, no markers, error bars/.cd, y dir=both, y explicit, error mark=none]"
#    print " coordinates {"
    print "x ex y ey"
    for b in range(1, nbins+1):
        x = h.GetBinCenter(b)
        ex = h.GetBinWidth(b)/2.0
        y = h.GetBinContent(b)
        ey = h.GetBinError(b)
# print x,ex,y,ey
        if y>0.0:
            print x, ex, y, ey

def g2pgf(h):
    """ Convert TGraph into pgfplot data """

    N = h.GetN()

    print "\\begin{axis}"
    print "\\addplot[ultra thick]"
    print " coordinates {"
    print "x ex y ey"
    for b in range(N):
        x = h.GetX()[b]
        y = h.GetY()[b]
        print x, y
    print "};"
    print "\\addlegendentry{TGraph};"

def main():
    """ A script to convert TH1 and TGraph into a pgfplot format """

    parser = argparse.ArgumentParser(description=main.__doc__, epilog='Homepage: https://github.com/kbat/mc-tools')
    parser.add_argument('root', type=str, help='ROOT file')
    parser.add_argument('hist', type=str, help='histogram name')
    args = parser.parse_args()

    f = ROOT.TFile(args.root)
    f.ls()
    h = f.Get(args.hist)

    if h.InheritsFrom("TH1"):
        h2pgf(h)
    elif h.InheritsFrom("TGraph"):
        g2pgf(h)


if __name__ == "__main__":
    sys.exit(main())
