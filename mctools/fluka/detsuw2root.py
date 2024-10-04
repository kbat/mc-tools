#!/usr/bin/env python3

import sys, argparse, struct
from os import path
# from mctools import fluka
from math import sqrt
from mctools.fluka.flair import fortran
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class DETECT:
    def __init__(self, fname):
        print(fname)
        self.f = open(fname, 'rb')

        data = fortran.read(self.f)
        size = len(data)
        self.runtit, self.runtim, self.wctot, self.nctot, self.mctot = struct.unpack("=80s32sf2i", data)
        self.runtit = self.runtit.decode('utf-8').strip()
        self.runtim = self.runtim.decode('utf-8').strip()
        assert self.runtim == "********    Sum file    ********"

    def __del__(self):
        self.f.close()

    def read(self):
        data = fortran.read(self.f)
        if data is None:
            return False
        size = len(data)
        ndet,chname,nbin,emin,ebin,ecut = struct.unpack("=i10si3f", data)
        chname = chname.decode('utf-8').strip()
        print(ndet,chname,nbin,emin,ebin,ecut)

        data = fortran.read(self.f)
        size = len(data)
        iv = struct.unpack("=%ii" % nbin, data)
        for i in range(nbin):
            ebnmin = emin + i * ebin
            ebnmax = emin + (i+1) * ebin
            weibin = iv[i] / (self.nctot + 1e9*self.mctot)
            weierr = 1.0/sqrt(max(iv[i],1))
            print(ebnmin,ebnmax,weibin,weierr*100)
        return True

def main():
    """Convert detsuw output into a ROOT TH2F histogram

    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('detsuw', type=str, help='detsuw binary output')
    parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Explain what is being done')

    args = parser.parse_args()

    if not path.isfile(args.detsuw):
        print("detsuw2root: File %s does not exist." % args.detsuw, file=sys.stderr)
        return 1

    if args.root == "":
        rootFileName = "%s%s" % (args.detsuw,".root")
    else:
        rootFileName = args.root

    d = DETECT(args.detsuw)
    while d.read():
        pass


if __name__=="__main__":
    sys.exit(main())
