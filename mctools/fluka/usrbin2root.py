#! /usr/bin/python -W all

import sys, argparse
import numpy as np
from os import path
sys.path.append("/usr/local/flair")
sys.path.append("/usr/local/flair/lib")
from Data import *
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """ Converts USRBIN output into a ROOT histogram """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('usrbin', type=str, help='usrbin binary output')
    parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Print some output')
    
    args = parser.parse_args()

    if not path.isfile(args.usrbin):
        print >> sys.stderr, "usrbin2root: File %s does not exist." % args.usrbin
        return 1

    if args.root == "":
        rootFileName = "%s%s" % (args.usrbin,".root")
    else:
        rootFileName = args.root
    
    b = Usrbin()
    b.readHeader(args.usrbin)
    val = unpackArray(b.readData(0))
    err = unpackArray(b.readStat(0))

# for i in range(len(b.detector)):
    if args.verbose:
        b.sayHeader()
        b.say(0)

    bin = b.detector[0]

    x = bin.xlow
    xbins = []
    for i in range(bin.nx+1):
        xbins.append(x + i*bin.dx)

    y = bin.ylow
    ybins = []
    for i in range(bin.ny+1):
        ybins.append(y + i*bin.dy)

    z = bin.zlow
    zbins = []
    for i in range(bin.nz+1):
        zbins.append(z + i*bin.dz)

    print xbins
    print ybins
    print zbins
    
    h = ROOT.TH3F("h%d" % (bin.score), bin.name, bin.nx, np.array(xbins, dtype=float), bin.ny, np.array(ybins, dtype=float), bin.nz, np.array(zbins, dtype=float))
    h.Print("a")
    print h.GetTitle()

    for i in range(bin.nx):
        for j in range(bin.ny):
            for k in range(bin.nz):
                gbin = k + j*bin.ny + i * bin.ny * bin.nx
                h.SetBinContent(i+1, j+1, k+1, val[gbin])
                h.SetBinError(i+1, j+1, k+1, err[gbin])
    h.SaveAs(rootFileName)

if __name__=="__main__":
    sys.exit(main())
