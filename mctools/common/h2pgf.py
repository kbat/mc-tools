#! /usr/bin/python -W all
#

import sys, argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """ A script to convert 1D histogram into a pgfplot with error bars
    input: xmin xmax y ey
    output: x ex y ey
    ex = (xmax+xmin)/2
    """
    
    parser = argparse.ArgumentParser(description=main.__doc__, epilog='Homepage: https://github.com/kbat/mc-tools')
    parser.add_argument('root', type=str, help='ROOT file')
    parser.add_argument('hist', type=str, help='histogram name')
    args = parser.parse_args()

    f = ROOT.TFile(args.root)
    h = f.Get(args.hist)
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


if __name__ == "__main__":
    sys.exit(main())
