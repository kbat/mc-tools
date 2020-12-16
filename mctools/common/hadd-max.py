#! /usr/bin/env python
#
# https://github.com/kbat/mc-tools
#

import argparse
import logging
from sys import exit
import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def getHistograms(fname):
    """ Return list of histograms found in the given file
    """
    logging.info("getHistograms")
    vhist = []
    f = ROOT.TFile(fname)
#    t = [key.GetName() for key in ROOT.gDirectory.GetListOfKeys()]
#    print(t)
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        if obj.Class().InheritsFrom(ROOT.TH1.Class()):
            obj.SetDirectory(0)
            vhist.append(obj)
    f.Close()

    return vhist

def getHist(vhist, hname, fname):
    """ Return the histogram from the vhist array with the given name
    """
    for h in vhist:
        if h.GetName() == hname:
            return h
    logging.error("%f contains a histogram %s which does not exist in vhist" % (fname, hname))
    return 0

def main():
    """ Merges files and writes histograms with max bin value in each pixel
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")

    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite',
                        help='overwrite the target output ROOT file')
    parser.add_argument('target', type=str, help='Target file')
    parser.add_argument('sources', type=str, help='Source files', nargs='+')

    args = parser.parse_args()

    if not args.overwrite and os.path.exists(args.target):
        logging.critical("File %s exists. Use -f to overwrite" % args.target)
        exit(1)

    vhist = getHistograms(args.sources[0])

    for fname in args.sources[1:]:
        f = ROOT.TFile(fname)
        for key in f.GetListOfKeys():
            h = getHist(vhist, key.GetName(), fname)
            hnew = key.ReadObj()
            for i in range(1, hnew.GetNbinsX()+1):
                for j in range(1, hnew.GetNbinsY()+1):
                    for k in range(1, hnew.GetNbinsZ()+1):
                        val = hnew.GetBinContent(i,j,k)
                        if val > h.GetBinContent(i,j,k):
                            h.SetBinContent(i,j,k,val)
                            h.SetBinError(i,j,k, hnew.GetBinError(i,j,k))

    f = ROOT.TFile(args.target, "RECREATE")
    for h in vhist:
        h.Write()
    f.Close()

if __name__ == "__main__":
    exit(main())
