#!/usr/bin/env python3

import sys, argparse
from os import path
import numpy as np
from mctools import fluka
from mctools.fluka.flair import Data
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def getType(det):
    """Return printable type of products to be scored

    """
    if int(det.type) == 1:
        return "Spallation products"
    elif int(det.type) == 2:
        return "Low-energy neutron products"
    elif int(det.type) == 3:
        return "All residual nuclei"
    else:
        return "unknown RESNUCLEI detector type"

def graph(name, title, val, err):
    N = len(val)
    assert N == len(err), "graph: length of val and err differ"

    ge = ROOT.TGraphErrors(N)
    for i in range(N):
        # if val[i] > 0.0 or err[i] > 0.0:
        x = i+1
        y = val[i]
        ey = err[i]*val[i]
        ge.SetPoint(i, x, y)
        ge.SetPointError(i, 0, ey)

    ge.SetNameTitle(name, title)

    return ge

def graphA(det, A, errA):
    return graph(det.name+"A", getType(det)+": Isotope yield as a function of mass number;A;Isotope yield [nuclei/cm^{3}/primary]", A, errA)

def graphZ(det, Z, errZ):
    return graph(det.name+"Z", getType(det)+": Isotope yield as a function of atomic number;Z;Isotope yield [nuclei/cm^{2}/primary]", Z, errZ)

def getRegion(det):
    """ Return printable scoring region number or name """
    if det.region == -1:
        return "all regions"
    else:
        return "region = %d" % det.region

def hist(det):
    """Create histogram for the given detector

    """

    title = "%s: %s, volume = %g cm^{3};Z;A;Isotope yield [nuclei/cm^{2}/primary]" % (getType(det), getRegion(det), det.volume)

    return ROOT.TH2F(det.name, title, det.zhigh-1, 1, det.zhigh, det.mhigh-1, 1, det.mhigh)


def main():
    """Convert usrsuw output into a ROOT TH2F histogram

    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('usrsuw', type=str, help='usrsuw binary output')
    parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')

    args = parser.parse_args()

    if not path.isfile(args.usrsuw):
        print("usrsuw2root: File %s does not exist." % args.usrsuw, file=sys.stderr)
        return 1

    if args.root == "":
        rootFileName = "%s%s" % (args.usrsuw,".root")
    else:
        rootFileName = args.root

    b = Data.Resnuclei()
    b.readHeader(args.usrsuw) # data file is closed here

    ND = len(b.detector)

    if args.verbose:
        b.sayHeader()
        print("\n%s %d %s found:" % ('*'*20, ND, "estimator" if ND==1 else "estimators"))
        for i in range(ND):
            b.say(i)
            print("")

    fout = ROOT.TFile(rootFileName, "recreate")
    for i in range(ND):
        val = Data.unpackArray(b.readData(i))
        stat = b.readStat(i)
        total, A, errA, Z, errZ, err = map(Data.unpackArray, stat[:-1])

        iso = stat[-1]
        if iso:
            print("isomeric:",iso)

        det = b.detector[i]
#        print(det.nb, det.name, det.type, det.region, det.mhigh, det.zhigh, det.nmzmin)

        h = hist(det)

        grA = graphA(det, A, errA)
        grZ = graphZ(det, Z, errZ)

        for z in range(1,det.zhigh+1):
            for j in range(1,det.mhigh+1):
                gbin = z-1+(j-1)*(det.zhigh)
                if val[gbin]>0.0:
                    a = j+det.nmzmin+2*z
                    h.SetBinContent(z,a,val[gbin])
                    h.SetBinError(z,a,err[gbin]*val[gbin])

        h.Write()
        grA.Write() # same as h.ProjectionY()
        grZ.Write() # same as h.ProjectionX()

    fout.Close()

if __name__=="__main__":
    sys.exit(main())
