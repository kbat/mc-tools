#!/usr/bin/env python3

import sys, argparse
from os import path
import numpy as np
from mctools import fluka
from mctools.fluka.flair import Data
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def graph(name, title, val, err):
    N = len(val)
    assert N == len(err), "graph: length of val and err differ"

    x = []
    y = []
    ey = []
    for i in range(N):
        if val[i] != 0.0 or err[i] != 0.0:
            x.append(i+1)
            y.append(val[i])
            ey.append(err[i]*val[i])

    ge = ROOT.TGraphErrors(len(x), np.array(x, dtype=float), np.array(y, dtype=float), np.array(ey, dtype=float)*0.0, np.array(ey, dtype=float))
    ge.SetNameTitle(name, title)

    return ge

def graphA(det, A, errA):
    return graph(det.name+"A", "Isotope yield as a function of mass number;A;Isotope yield [nuclei/cm^{3}/primary]", A, errA)

def graphZ(det, Z, errZ):
    return graph(det.name+"Z", "Isotope yield as a function of atomic number;Z;Isotope yield [nuclei/cm^{2}/primary]", Z, errZ)

def hist(det):
    """ Create histogram for the given detector """

    title = "Region: %d, Volume: %g cm^{3};Z;A" % (det.region, det.volume)

    return ROOT.TH2F(det.name, title, det.zhigh-1, 1, det.zhigh, det.mhigh-1, 1, det.mhigh)


def main():
    """ Converts usrsuw output into a ROOT TH2F histogram """

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
    b.readHeader(args.usrsuw) # data file closed here

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
        total, A, errA, Z, errZ, err, iso = b.readStat(i)
        err = Data.unpackArray(err)
        total = Data.unpackArray(total)
        A = Data.unpackArray(A)
        errA = Data.unpackArray(errA)
        Z = Data.unpackArray(Z)
        errZ = Data.unpackArray(errZ)
        # print("val:",val, len(val))
        # print("err:",err, len(err))
        # print("\ntotal:  ",total) # total response [n/cmc/pr]
        # print("sum(val):",sum(val))
        # print("\nIsotope Yield as a function of Mass Number")
        # print("A:", A, len(A), sum(A))
        # print("errA:", errA, len(errA))
        # print("\nIsotope Yield as a function of Atomic Number")
        # print("Z:", Z, len(Z), sum(Z))
        # print("errZ:", errZ, len(errZ))
        # print("iso:",iso)

        det = b.detector[i]
        print(det.nb, det.name, det.type, det.region, det.mhigh, det.zhigh, det.nmzmin)

        h = hist(det)

        grA = graphA(det, A, errA)
        grZ = graphZ(det, Z, errZ)
        s = 0.0

        for z in range(1,det.zhigh+1):
            for j in range(1,det.mhigh+1):
                gbin = z-1+(j-1)*(det.zhigh)
                if val[gbin]>0:
                    a = j+det.nmzmin+2*z
                    h.SetBinContent(z,a,val[gbin])
                    h.SetBinError(z,a,err[gbin]*val[gbin])

                    s += val[gbin]

#        print("test of total sum:",s-total[0]>1e-8)

        h.Write()
        grA.Write()
        grZ.Write()

    fout.Close()

if __name__=="__main__":
    sys.exit(main())
