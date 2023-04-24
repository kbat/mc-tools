#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import argparse
import logging
from sys import exit
import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def fixFirstHisto(h, errmax):
    """ Set bins values with relative errors above the given one to zero

        This function is designed to be used with the first histogram, which is compared with the others.
    """
    for i in range(1, h.GetNbinsX()+1):
        for j in range(1, h.GetNbinsY()+1):
            for k in range(1, h.GetNbinsZ()+1):
                val = h.GetBinContent(i,j,k)
                err = h.GetBinError(i,j,k)
                relerr = err/val if val != 0.0 else 0.0
                if relerr*100.0 > errmax:
                    h.SetBinContent(i,j,k, 0.0)
                    h.SetBinError(i,j,k, 0.0)


def getHistograms(fname, only, errmax):
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
            if only is None:
                vhist.append(obj)
            elif obj.GetName() == only:
                vhist.append(obj)

    f.Close()

    for h in vhist:
        fixFirstHisto(h, errmax)

    return vhist

def getHist(vhist, hname, fname):
    """ Return the histogram from the vhist array with the given name
    """
    for h in vhist:
        if h.GetName() == hname:
            return h
    logging.error("%s contains a histogram %s which does not exist in vhist" % (fname, hname))
    return 0

def checkAxes(h1, h2):
    """ Check if the axes of both histograms are the same
    """

    a1 = (h1.GetXaxis(), h1.GetYaxis(), h1.GetZaxis())
    a2 = (h2.GetXaxis(), h2.GetYaxis(), h2.GetZaxis())
    name = ('x', 'y', 'z')

    for i in range(3):
        n1 = a1[i].GetNbins()
        n2 = a2[i].GetNbins()
        if n1 != n2:
            print("Number of %s axis bins differ in %s: %d, %d" % (name[i], h1.GetName(), n1, n2))
            exit(1)
        # if a1[i].GetBinLowEdge[1] != a2[i].GetBinLowEdge[1]:
        #     print("Low edge of the first bins along the %s axis are different", name[i])
        #     exit(1)
        # if a1[i].GetBinLowEdge[n-1] != a2[i].GetBinLowEdge[n-1]:
        #     print("Low edge of the last bins along the %s axis are different", name[i])
        #     exit(1)

def main():
    """ Merges files and writes histograms with max bin value in each pixel
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")

    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite',
                        help='overwrite the target output ROOT file')
    parser.add_argument("-errmax",   type=float, dest='errmax', help='max relative error [percent] of bin content. If relative error of the bin is greater than this value, this bin is skipped',
                        default=1000.0, required=False)
    parser.add_argument("-only", type=str, default=None, help="take into account only the given histogram name")
    parser.add_argument('target', type=str, help='target file')
    parser.add_argument('sources', type=str, help='source files', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print the file names as they are processed')

    args = parser.parse_args()

    if not args.overwrite and os.path.exists(args.target):
        logging.critical("File %s exists. Use -f to overwrite" % args.target)
        exit(1)

    vhist = getHistograms(args.sources[0], args.only, args.errmax)

    if args.verbose:
        print(args.sources[0])

    for fname in args.sources[1:]:
        if args.verbose:
            print(fname)
        f = ROOT.TFile(fname)
        for key in f.GetListOfKeys():
            hnew = key.ReadObj()
            if not hnew.Class().InheritsFrom(ROOT.TH1.Class()):
                continue
            if args.only is not None and key.GetName() != args.only:
                continue;
            h = getHist(vhist, key.GetName(), fname)
            checkAxes(h, hnew)
            for i in range(1, hnew.GetNbinsX()+1):
                for j in range(1, hnew.GetNbinsY()+1):
                    for k in range(1, hnew.GetNbinsZ()+1):
                        val = hnew.GetBinContent(i,j,k)
                        err = hnew.GetBinError(i,j,k)
                        relerr = err/val if val != 0.0 else 0.0
                        if val > h.GetBinContent(i,j,k) and relerr*100.0 < args.errmax:
                            h.SetBinContent(i,j,k, val)
                            h.SetBinError(i,j,k, err)
        f.Close()

    f = ROOT.TFile(args.target, "RECREATE")
    for h in vhist:
        h.Write()
    f.Close()

if __name__ == "__main__":
    exit(main())
