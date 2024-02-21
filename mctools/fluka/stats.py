#!/usr/bin/env python

import argparse
from sys import exit
from glob import glob
import re
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def Print(vals, ttype):
    data = np.array(vals)
    print("%s: %.5g stdev: %.5g" % (ttype, np.average(data), np.std(data)))

def get(fname, ttype):
    if ttype == "average":
        sss = "Average CPU time used to follow a primary particle:"
    elif ttype == "maximum":
        sss = "Maximum CPU time used to follow a primary particle:"
    elif ttype == "total":
        sss = "Total CPU time used to follow all primary particles:"
    else:
        raise NameError(f"Unknown ttype argument: {ttype}")

    with open(fname) as f:
        val = -1.0
        for line in reversed(list(f)):
        #for line in f:
            l = line.strip()
            if re.search(f"\A{sss}", l):
                w = l.split()
                val = w[-3]
                try:
                    val = float(val)
                    return val
                except ValueError:
                    print(f"Can't convert \"{val}\" to float")
                    raise
    raise NameError(f"String \"{sss}\" not found in {fname}")

def main():
    """ Print/draw the CPU time statistics based on the FLUKA output files"""

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-o', dest="out", type=str, default=None, help='optional output file name', required=False)
    parser.add_argument('-n', dest="N", type=int, default=10, help='number of histogram bins (make sense with the -o option only)', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

    args = parser.parse_args()

    avals = []
    mvals = []

    for fname in glob("*.out"):
        avals.append(get(fname, "average"))
        mvals.append(get(fname, "maximum"))

    Print(avals, "Average")
    Print(mvals, "Maximum")
    print("TODO: take into account weight reported in Total number of primaries run")

    if args.out:

        ha = ROOT.TH1F("ha", "Average;Time [s];Number of runs", args.N, min(avals)*0.99, max(avals)*1.01)
        hm = ROOT.TH1F("hm", "Maximum;Time [s];Number of runs", args.N, min(mvals)*0.99, max(mvals)*1.01)
        hm.SetLineColor(ROOT.kRed)

        for v in avals:
            ha.Fill(v)

        for v in mvals:
            hm.Fill(v)

        ha.Draw("hist e")
        ROOT.gPad.Print("%s(" % args.out)

        hm.Draw("hist e")
        ROOT.gPad.Print("%s)" % args.out)

if __name__ == "__main__":
    exit(main())
