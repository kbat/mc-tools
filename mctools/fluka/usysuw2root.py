#!/usr/bin/env python

import sys, argparse
from os import path
import numpy as np
from mctools import fluka, getLogBins, getLinBins
from mctools.fluka.flair import Data
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """ Converts usysuw output into a ROOT TH2F histogram """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('usryield', type=str, help='usysuw binary output')
    parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')

    args = parser.parse_args()

    if not path.isfile(args.usryield):
        print("usysuw2root: File %s does not exist." % args.usryield, file=sys.stderr)
        return 1

    if args.root == "":
        rootFileName = "%s%s" % (args.usryield,".root")
    else:
        rootFileName = args.root

    b = Data.Usrxxx()
    b.readHeader(args.usryield) # data file closed here

    ND = len(b.detector)

    if args.verbose:
        b.sayHeader()
        print("\n%s %d %s found:" % ('*'*20, ND, "estimator" if ND==1 else "estimators"))
        for i in range(ND):
            b.say(i)
            print("")


if __name__=="__main__":
    sys.exit(main())
