#! /usr/bin/python3 -W all

import sys, argparse
from os import path
import numpy as np
from mctools import fluka
from mctools.fluka.flair import Data
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def getType(n):
    """ Decrypt what(1) of usrbdx """
    for i1 in (-2,-1,1,2):
        for i2 in (0,1):
            for i3 in (0,1):
                if (i1+10*i2+100*i3 == n):
                    return (i1,i2,i3) # i3 is irrelevant - use bin.fluence instead
    print("usrbdx2root: what(1) == %d undefined" % n, file=sys.stderr)
    sys.exit(1)

def isLogE(x):
    if x in (-2,-1):
        return True
    return False

def isLogA(x):
    if x in (-2,2):
        return True
    return False

def getAxesTitle(det,x):
    ztitle = "1/cm^{2}/GeV/sr"
    if int(det.dist) in (208,211): # differential energy fluence/current
        ztitle = "GeV/cm^{2}/GeV/sr"   # FLUKA manual page 247
    return {
        -2 : ";log10(Energy/GeV);log10(#Omega/rad);" + ztitle,
        -1 : ";log10(Energy/GeV);#Omega [rad];" + ztitle,
         1 : ";Energy [GeV];#Omega [rad];" + ztitle,
         2 : ";Energy [GeV];log10(#Omega/rad);" + ztitle,
        }[x]

def getLogBins(nbins, low, high):
    """ Return array of bins with log10 equal widths """

    x = float(low)
    dx = pow(high/low, 1.0/nbins);

    return np.array([x*pow(dx,i) for i in range(nbins+1)], dtype=float)

def getLinBins(nbins, low, high):
    """ Return array of bins with linearly equal widths """
    x = float(low)
    dx = float(high-low)/nbins

    return np.array([x+i*dx for i in range(nbins+1)], dtype=float)

def getNEbins(det):
    """ Return number of energy bins """
    nebins = det.ne
    if det.lowneu:
        nebins += det.ngroup
    return nebins

def getEbins(det, i):
    """ Return lin or log energy bins depending on the value of i """

    if isLogE(i):
        return getLogBins(det.ne, det.elow, det.ehigh)
    else:
        return getLinBins(det.ne, det.elow, det.ehigh)

def getAbins(det, i):
    """ Return lin or log angular bins depending on the value of i """

    if isLogA(i):
        return getLogBins(det.na, det.alow, det.ahigh)
    else:
        return getLinBins(det.na, det.alow, det.ahigh)

def getHistTitle(det,w1):
    """ Return histogram title """
    title = "%s %s #diamond reg %d %s %d #diamond %g cm^{2}" % (fluka.particle.get(det.dist, "undefined"), "fluence" if det.fluence else "current", det.reg1, "#leftrightarrow" if det.twoway else "#rightarrow", det.reg2, det.area)
    title += getAxesTitle(det,w1)
    return title

def hist(det):
    """ Create histogram for the given detector """

    w1 = getType(det.type)[0] # decrypted what(1)
    title = getHistTitle(det,w1)

    nebins = getNEbins(det)
    ebins = getEbins(det,w1)
    if det.lowneu:
        ebins = np.concatenate((np.array(det.egroup[::-1]), getEbins(det,w1)[1:]))

    return ROOT.TH2F(det.name, title, nebins, ebins, det.na, getAbins(det, w1))

# def histN(det):
#     """ Create histogram for the given detector with low energy neutrons """
#     w1 = getType(det.type)[0]
#     if det.lowneu:
#         name = det.name + "_lowneu"
#         title = "Low energy " + getHistTitle(det,w1)
#         return ROOT.TH2F(name, title, det.ngroup, np.array(det.egroup[::-1]), det.na, getAbins(det, w1))
#     else:
#         return 0


def main():
    """ Converts usxsuw output into a ROOT TH2F histogram """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('usrbdx', type=str, help='usxsuw binary output')
    parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')

    args = parser.parse_args()

    if not path.isfile(args.usrbdx):
        print("usrbdx2root: File %s does not exist." % args.usrbdx, file=sys.stderr)
        return 1

    if args.root == "":
        rootFileName = "%s%s" % (args.usrbdx,".root")
    else:
        rootFileName = args.root

    b = Data.Usrbdx()
    b.readHeader(args.usrbdx) # data file closed here

    ND = len(b.detector)

    if args.verbose:
        b.sayHeader()
        print("\n%s %d %s found:" % ('*'*20, ND, "estimator" if ND==1 else "estimators"))
        for i in range(ND):
            b.say(i)
            print("")

    fout = ROOT.TFile(rootFileName, "recreate")
    for i in range(ND):
        val1 = Data.unpackArray(b.readData(i))
        err1 = Data.unpackArray(b.readStat(i))
        det = b.detector[i]

        h = hist(det)

        val = val1[-det.ngroup:][::-1] + val1[0:det.ne]
        assert len(val1) == len(val)

        err = err1[-det.ngroup:][::-1] + err1[0:det.ne]
        assert len(err1) == len(err)

        nebins = getNEbins(det)
        for i in range(nebins):
            for j in range(det.na):
                    gbin = i + j * nebins
                    h.SetBinContent(i+1, j+1, val[gbin])
                    h.SetBinError(i+1, j+1, err[gbin]*15.91549)
        h.SetEntries(b.weight)
        h.Write()

    fout.Close()

if __name__=="__main__":
    sys.exit(main())
