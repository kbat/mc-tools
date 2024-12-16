#!/usr/bin/env python

import sys, argparse, struct
from os import path
import numpy as np
from mctools import fluka, getLogBins, getLinBins
from mctools.fluka.flair import Data
from mctools.fluka.flair import fortran
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class USRYIELD(Data.Usrxxx):
    def readHeader(self, filename):
        f = super().readHeader(filename)

        for _ in range(1):
            data = fortran.read(f)
            if data is None:
                break
            size = len(data)
            IJUSYL, JTUSYL, PUSRYL, SQSUYL, UUSRYL, VUSRYL, WUSRYL = struct.unpack("=2i5f", data)
            print(f"Projectile: {IJUSYL}, its lab. momentum: {PUSRYL}, lab. direction: {UUSRYL} {VUSRYL} {WUSRYL}")
            print("Target:",JTUSYL)
            print("CMS energy for Lorentz transformation:",SQSUYL)

        while True:
            data = fortran.read(f)
            if data is None:
                break
            size = len(data)
            if size != 70:
                break
            NYL,TITUYL,ITUSYL,IXUSYL,IDUSYL,NR1UYL,NR2UYL,USNRYL,SGUSYL,LLNUYL,EYLLOW,EYLHGH,NEYLBN,DEYLBN,AYLLOW,AYLHGH = struct.unpack("=i10s3i2i2fi2fif2f", data)
            TITUYL = TITUYL.decode('utf-8').strip()
            print("cross section kind: ",ITUSYL)
            print("distribution to be scored: ", IXUSYL)
            print("secondary distribution to be scored: ", IDUSYL)
            print(f"from region {NR1UYL} to region {NR2UYL}")
            print("normalisation factor:",USNRYL)
            print("normalisatoin cross section:",SGUSYL)
            print("low energy neutron scoring:",LLNUYL)
            print(f"min/max energies: {EYLLOW} {EYLHGH} GeV")
            print("number of energy or other quantity intervals:",NEYLBN)
            print("energy (or other) bin width:",DEYLBN)
            print(f"min/maxangles (or other): {AYLLOW} {AYLHGH} rad")


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

    b = USRYIELD()
    b.readHeader(args.usryield) # data file closed here

    for _ in range(1):
        b.readData(1)

    ND = len(b.detector)

    if args.verbose:
        b.sayHeader()
        print("\n%s %d %s found:" % ('*'*20, ND, "estimator" if ND==1 else "estimators"))
        for i in range(ND):
            b.say(i)
            print("")


if __name__=="__main__":
    sys.exit(main())
