#!/usr/bin/env python3

import sys, argparse, struct
from os import path
import numpy as np
from math import isclose
from mctools import fluka, getLogBins, getLinBins
from mctools.fluka.flair import Data, fortran
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def getAxesTitle(det):
    # differential energy fluence/current
    # FLUKA manual: USRTRACK section
    energy = (208, 211) # ENERGY or EM-ENERGY
    ytitle = fluka.particle.get(det.dist, "undefined")
    if int(det.dist) in energy:
        ytitle += " tracklength [cm]" if isclose(det.volume, 1.0) else " energy fluence [cm^{-2}]"
    else:
        ytitle += " tracklength [cm/GeV]" if isclose(det.volume, 1.0) else " fluence [1/GeV/cm^{2}]"

    return ";Energy [GeV];" + ytitle

def getEbins(det):
    """ Return lin or log energy bins depending on the value of i """

    if det.type == -1:
        return getLogBins(det.ne, det.elow, det.ehigh)
    else:
        return getLinBins(det.ne, det.elow, det.ehigh)

def hist(det):
    """ Create histogram for the given detector """

    if det.ne == 0:
        print(f"WARNING: Not saving detector {det.name} into ROOT file since it has 0 energy bins: {det.elow} < E < {det.ehigh}")
        print("         This happens for neutron-contributing estimators if max scoring energy is below groupwise max energy, 20 MeV.")
        return None

    title = fluka.particle.get(det.dist, "undefined")
    title += " #diamond "
    title += "all regions" if int(det.reg) == -1 else "reg %d" % det.reg
    title += " #diamond "
    title += "%g cm^{3}" % det.volume
    title += " #diamond "
    title += "%g < E < %g GeV" % (det.elow, det.ehigh)
    title += getAxesTitle(det)

    return ROOT.TH1F(det.name, title, det.ne, getEbins(det))

def histN(det):
    """Create histogram for the given detector with low energy neutrons

    """
    if det.lowneu:
        name = det.name + "_lowneu"
        title = name + getAxesTitle(det)
        return ROOT.TH1F(name, title, det.ngroup, np.array(det.egroup[::-1]))
    else:
        return 0

class Usrtrack(Data.Usrxxx):
    """ Reads the ustsuw binary output
        (USRTRACK / USRCOLL estimators)
    """
    def readHeader(self, filename):
        """ Reads the file header info
            Based on Data.Usrbdx
        """
        f = super().readHeader(self, filename)
#        self.sayHeader()

        while True:
            data = fortran.read(f)
            if data is None: break
            size = len(data)
#            print("size: ", size)

            if size == 14 and data.decode('utf8')[:10] == "STATISTICS":
                self.statpos = f.tell()
                for det in self.detector:
                    data = Data.unpackArray(fortran.read(f))
                    det.total = data[0]
                    det.totalerror = data[1]
#                    for j in range(6):
#                        fortran.skip(f)
                break

            if size != 50: raise IOError("Invalid USRTRACK/USRCOLL file %d " % size)

            header = struct.unpack("=i10siiififfif", data)

            det = Data.Detector()
            det.nb = header[0]
            det.name = header[1].decode('utf8').strip() # titutc - track/coll name
            det.type = header[2] # itustc - type of binning: 1 - linear energy etc
            det.dist = header[3] # idustc = distribution to be scored
            det.reg  = header[4] # nrustc = region
            det.volume = header[5] # vusrtc = volume (cm**3) of the detector
            det.lowneu = header[6] # llnutc = low energy neutron flag
            det.elow = header[7] # etclow = minimum energy [GeV]
            det.ehigh = header[8] # etchgh = maximum energy [GeV]
            det.ne = header[9] # netcbn = number of energy intervals
            det.de = header[10] # detcbn = energy bin width

            self.detector.append(det)

            if det.lowneu:
                data = fortran.read(f)
                det.ngroup = struct.unpack("=i",data[:4])[0]
                det.egroup = struct.unpack("=%df"%(det.ngroup+1), data[4:])
                print(f"{det.name}: Low energy neutrons scored with {det.ngroup} groups")
            else:
                det.ngroup = 0
                det.egroup = ()

            size  = (det.ngroup+det.ne) * 4
            if size != fortran.skip(f):
                raise IOError("Invalid USRTRACK file")
        f.close()

    def printHeader(self, i):
        """ Prints the header """
        det = self.detector[i]
        print("Detector:", det.name)
        print(" binning type: ", det.type)
        print(" distribution to be scored:", det.dist)
        print(" region:", det.reg)
        print(" volume:", det.volume)
        print(" low energy neutrons:", det.lowneu)
        print(" %g < E < %g GeV / %d bins; bin width: %g" % (det.elow, det.ehigh, det.ne, det.de))

    def readStat(self, det,lowneu):
        """ Read detector # det statistical data """
        if self.statpos < 0: return None
        with open(self.file,"rb") as f:
            f.seek(self.statpos)
            for i in range(det+3): # check that 3 gives correct errors with 1 USRTRACK detector
                fortran.skip(f) # skip previous detectors
            data = fortran.read(f)
        return data

    def readData(self, det,lowneu):
        """Read detector det data structure

        """
        f = open(self.file,"rb")
        fortran.skip(f) # Skip header
        for i in range(2*det):
            fortran.skip(f)     # Detector Header & Data
        fortran.skip(f)         # Detector Header
        if lowneu:
            fortran.skip(f) # skip low enery neutron data
        data = fortran.read(f)
        f.close()
        return data

def main():
    """ Converts ustsuw output into a ROOT TH1F histogram """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('usrtrack', type=str, help='ustsuw binary output')
    parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')

    args = parser.parse_args()

    if not path.isfile(args.usrtrack):
        print("ustsuw2root: File %s does not exist." % args.usrtrack, file=sys.stderr)
        return 1

    if args.root == "":
        rootFileName = "%s%s" % (args.usrtrack,".root")
    else:
        rootFileName = args.root

    b = Usrtrack()
    b.readHeader(args.usrtrack)

    ND = len(b.detector)
    # print("ND:",ND)

    if args.verbose:
        #b.sayHeader()
        for i in range(ND):
            b.printHeader(i)
            print("")

    fout = ROOT.TFile(rootFileName, "recreate")
    for i in range(ND):
        det = b.detector[i]
        val = Data.unpackArray(b.readData(i, det.lowneu))
        err = Data.unpackArray(b.readStat(i, det.lowneu))

        # print("val",val, len(err))
        # print("err",err, len(err))
        assert len(val) == len(err), "val and err length are different: %d %d" % (len(val), len(err))

        h = hist(det)
        hn = histN(det) # filled only if det.lowneu

        if h:
            n = h.GetNbinsX()
            assert n == det.ne, "n != det.ne"

            # print(i,n, len(val))
            for i in range(n):
                h.SetBinContent(i+1, val[i])
                h.SetBinError(i+1,   err[n-i-1]*val[i])

            h.SetEntries(b.weight)
            h.Write()

# not implemented - bugs with theINFN FLUKA, but it seems works with the CERN FLUKA
        if det.lowneu:
            # val_lowneu = val[det.ne::][::-1]
            # err_lowneu = err[det.ne::][::-1]
            n = hn.GetNbinsX()
            assert n == det.ngroup, "n != det.ngroup"
            # print(n, len(val_lowneu), len(err_lowneu))
            for i in range(n):
                hn.SetBinContent(i+1, val[-i-1])
                hn.SetBinError(i+1,   err[-i-1]*val[-i-1])

            hn.SetEntries(b.weight)
            hn.Write()

    fout.Close()

if __name__=="__main__":
    sys.exit(main())
