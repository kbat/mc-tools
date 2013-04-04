#! /usr/bin/python -W all

import sys, re, string
from array import array
from ROOT import ROOT, TFile, TH1F, TObjArray, THnSparseF
from mctal import MCTAL

def main():
    """
    mctal2root - MCTAL to ROOT converter
    Usage: mctal2root.py mctal [output.root]
    ... many features are not yet supported!

    Homepage: http://code.google.com/p/mc-tools
    """

    fname_in = sys.argv[1]
    if len(sys.argv) == 3:
        fname_out = sys.argv[2]
    else:
        fname_out = re.sub("\....$", ".root", fname_in)
    if fname_in == fname_out:
        fname_out = fname_in + ".root"
    print "mctal2root: %s -> %s" % (fname_in, fname_out)


    mctal = MCTAL(fname_in)
    mctal.Read()
    mctal.Print(12)

if __name__ == '__main__':
    sys.exit(main())
