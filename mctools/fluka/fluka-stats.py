#!/usr/bin/env python

import argparse
from sys import exit
from glob import glob
import re
from math import sqrt, log10, floor
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def Print(vals, ttype, nps):
    data = np.array(vals)
    n = len(data)
    scale = n/nps
    print("%s: %.5g ± %.5g sec" % (ttype, np.average(data)*scale, np.std(data)/sqrt(n)*scale))

def get(fname, ttype):
    if ttype == "average":
        sss = "Average CPU time used to follow a primary particle:"
    elif ttype == "maximum":
        sss = "Maximum CPU time used to follow a primary particle:"
    elif ttype == "total":
        sss = "Total CPU time used to follow all primary particles:"
    elif ttype == "nps":
        sss = "Total number of primaries run"
    else:
        raise NameError(f"Unknown ttype argument: {ttype}")

    with open(fname) as f:
        val = -1.0
        for line in reversed(list(f)):
        #for line in f:
            l = line.strip()
            if re.search(f"\A{sss}", l):
                w = l.split()
                if ttype == "nps":
                    val = w[5]
                else:
                    val = w[-3]
                try:
                    val = float(val)
                    return val
                except ValueError:
                    print(f"Can't convert \"{val}\" to float")
                    raise
    return None

def main():
    """ Print/draw the CPU time statistics based on the FLUKA output files"""

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('out', type=str, nargs="+", help='List of FLUKA output file(s)')
    parser.add_argument('-o', dest="pdf", type=str, default=None, help='optional output PDF file name', required=False)
    parser.add_argument('-n', dest="N", type=int, default=10, help='number of histogram bins (make sense with the -o option only)', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

    args = parser.parse_args()

    if args.pdf and not args.pdf.endswith(".pdf"):
        print(f"Error: PDF file name is expected: {args.pdf}")
        return 1

    avals = []
    mvals = []
    nps = 0
    for fname in args.out:
        aval = get(fname, "average")
        if aval is not None:
            mval = get(fname, "maximum")
            if mval is not None:
                n = get(fname, "nps")
                avals.append(aval*n)
                mvals.append(mval*n)
                nps += n

    Print(avals, "Average", nps)
    Print(mvals, "Maximum", nps)
    print(f"nps:     {nps:e}")

    if args.pdf:

        ha = ROOT.TH1F("ha", "Average;Time [s];Number of runs", args.N, min(avals)*0.99, max(avals)*1.01)
        hm = ROOT.TH1F("hm", "Maximum;Time [s];Number of runs", args.N, min(mvals)*0.99, max(mvals)*1.01)

        for v in avals:
            ha.Fill(v)

        for v in mvals:
            hm.Fill(v)

        ha.Draw("hist e")
        ROOT.gPad.Print("%s(" % args.pdf)

        hm.Draw("hist e")
        ROOT.gPad.Print("%s)" % args.pdf)

if __name__ == "__main__":
    exit(main())
