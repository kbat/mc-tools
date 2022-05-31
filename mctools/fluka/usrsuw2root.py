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
    n = len(val)
    assert n == len(err), "graph: length of val and err differ"

    N = np.count_nonzero(val) # number of points in the graph

    ge = ROOT.TGraphErrors(N)
    j = 0 # ge point index
    for i in range(n):
        x = i+1
        y = val[i]
        ey = err[i]*val[i]
        if y>0.0:
            ge.SetPoint(j, x, y)
            ge.SetPointError(j, 0.0, ey)
            j = j+1

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

    nz = det.zhigh-1
    na = det.mhigh+det.nmzmin+det.zhigh
    return ROOT.TH2F(det.name, title, nz, 1, nz+1, na, 1, na+1)


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
        total, A, errA, Z, errZ, err, iso = map(Data.unpackArray, stat)
#        print(i,iso) - isomers(?)

        det = b.detector[i]
#        print(det.nb, det.name, det.type, det.region, det.mhigh, det.zhigh, det.nmzmin)

        h = hist(det)

        grA = graphA(det, A, errA)
        grZ = graphZ(det, Z, errZ)

        for z in range(1,det.zhigh+1):
            for j in range(1,det.mhigh+1):
                gbin = z-1+(j-1)*(det.zhigh)
                if val[gbin]>0.0:
                    # See the RDRESN program from the RESNUCLEi section of the Manual
                    a = j+det.nmzmin+2*z
                    h.SetBinContent(z,a,val[gbin])
                    h.SetBinError(z,a,err[gbin]*val[gbin])

        h.Write()
        grA.Write()
        grZ.Write()

    fout.Close()

if __name__=="__main__":
    sys.exit(main())
