#!/usr/bin/env python

import sys, argparse, struct
import logging
from os import path
import numpy as np
from mctools import fluka, getLogBins, getLinBins
from mctools.fluka.flair import Data, fortran
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

logger = logging.getLogger(__name__)

def getType(n):
    """ Decrypt what(1) of USRYIELD """
    for ie in range(-38,39):
        if ie == 0:
            continue
        for ia in range(1,39):
            for i4 in (-1,0,1):
                if (ie+100*ia+10000*i4 == n):
                    return (ie,ia,i4)
    print(f"usysuw2root: what(1) == {n} undefined", file=sys.stderr)
    sys.exit(1)

def getDistTitle(i, var1, var2):
    """
    Parse WHAT(6) and return the distribution title
    """

    x1 = var1[2] if len(var1) == 3 else "x_{1}"
    x2 = var2[2] if len(var2) == 3 else "x_{2}"

    ixa = i
    ixm = 0
    if i>100:
        ixa = i %  100
        ixm = i // 100

    val = "N"
    if ixa > 52:
        val = "#sigma"
        ixa = ixa - 50

    match ixa:
     case 1:
      return "#frac{d^{2}#sigma}{d%sd%s}" % (x1, x2)
     case 2:
      return "E#frac{d^{3}#sigma}{dp^{3}}"
     case 3:
      return "#frac{d^{2}%s}{d%sd%s}" % (val, x1, x2)
     case 4:
      return "#frac{d^{2}(%s%s)}{d%sd%s}" % (x2, val, x1, x2)
     case 5:
      return "#frac{d^{2}(%s%s)}{d%sd%s}" % (x1, val, x1, x2)
     case 6:
      return "#frac{1}{cos#theta} #frac{d^{2}%s}{d%sd%s}" % (val, x1, x2)
     case 7:
      return "#frac{d^{2}(%s^{2}%s)}{d%sd%s}" % (x2, val, x1, x2)
     case 8:
      return "#frac{d^{2}(%s^{2}%s)}{d%sd%s}" % (x1, val, x1, x2)
     case 9:
      return "#frac{d^{2}%s}{%sd%sd%s}" % (val, x2, x1, x2)
     case 10:
      return "#frac{d^{2}%s}{%sd%sd%s}" % (val, x1, x1, x2)
     case 11:
      return "#frac{d^{2}%s}{d(%s/%s)d%s}" % (val, x1, x2, x2)
     case 12:
      return "#frac{d^{2}(%s#sqrt{%s^{2}-%s^{2}}%s)}{d%sd%s}" % (x1, x1, val, x2, x1, x2)
     case 13:
      return "#frac{d^{2}((%s^{2}+%s^{2})%s)}{d%sd%s}" % (x1, x2, val, x1, x2)
     case 14:
      return "#frac{d^{2}((%s+%s^{2})%s)}{#pid%sd%s}" % (x1, x2, val, x1, x2)
     case 15:
      return "#frac{d^{2}((%s^{2}+%s)%s)}{#pid%sd%s}" % (x1, x2, val, x1, x2)
     case 16:
      return "#frac{1}{cos#theta} #frac{d^{2}(%s%s)}{d%sd%s}" % (x2, val, x1, x2)
     case 26:
      return "#frac{1}{cos#theta} #frac{d^{2}(%s%s)}{d%sd%s}" % (x1, val, x1, x2)
     case _:
      return "unknown title (not implemented)"

def getVarTitle(i):
    match abs(i):
     case 1:
      return ("Kinetic energy", "GeV", "E")
     case 2:
      return ("Total momentum", "GeV/c", "p")
     case 3:
      return ("Rapidity in the LAB frame", "", "w")
     case 4:
      return ("Rapidity in the CMS frame", "", "w")
     case 5:
      return ("Pseudo-rapidity in the LAB frame", "", "#eta")
     case 6:
      return ("Pseudo-rapidity in the CMS frame", "", "#eta")
     case 7:
      return ("Feynman-x in the LAB frame", "")
     case 8:
      return ("Feynman-x in the CMS frame", "")
     case 9:
      return ("Transverse momentum", "GeV/c")
     case 10:
      return ("Transverse mass", "GeV")
     case 11:
      return ("Longitudinal momentum in the LAB frame", "GeV/c")
     case 12:
      return ("Longitudinal momentum in the CMS frame", "GeV/c")
     case 13:
      return ("Total energy", "GeV")
     case 14:
      return ("Polar angle in the LAB frame", "rad", "#theta")
     case 15:
      return ("Polar angle in the CMS frame", "rad", "#theta")
     case 16:
      return ("Square transverse momentum", "(GeV/c)^{2}")
     case 17:
      return ("1/(2#pi sin#theta) weighted angle in the LAB frame", "")
     case 18:
      return ("1/(2#pi p_T) weighted transverse momentum", "GeV/c")
     case 19:
      return ("Rratio laboratory momentum to beam momentum", "")
     case 20:
      return ("Transverse kinetic energy", "")
     case 21:
      return ("Excitation energy", "")
     case 22:
      return ("Particle charge", "")
     case 23:
      return ("Particle LET", "")
     case 24:
      return ("Polar angle in the LAB frame", "deg", "#theta")
     case 25:
      return ("Polar angle in the CMS frame", "deg", "#theta")
     case 26:
      return ("Laboratory kinetic energy per nucleon", "")
     case 27:
      return ("Laboratory momentum per nucleon", "")
     case 28:
      return ("Particle baryonic charge", "")
     case 29:
      return ("Four-momentum transfer -t", "")
     case 30:
      return ("CMS longitudinal Feynman-x", "")
     case 31:
      return ("Excited mass squared", "")
     case 32:
      return ("Excited mass squared/s", "")
     case 33:
      return ("Time", "s", "t")
     case 34:
      return ("sin weighted angle in the LAB frame", "")
     case 35:
      return ("Total momentum in the CMS frame", "GeV/c")
     case 36:
      return ("Total energy in the CMS frame", "GeV/c")
     case _:
      return (f"Unknown: {i=}", "")

class USYSUW(Data.Usrxxx):
    """
    Read the usysuw binary output (USRYIELD average)
    """
    def setVerbose(self, val):
        self.verbose = val

    def say(self, i):
        det = self.detector[i]
        print(f"Detector {det.NYL}:\t{det.TITUYL}")
        print(" cross section kind: ",det.ITUSYL)
        print(f" distributions: {det.IXUSYL} {fluka.particle.get(det.IDUSYL)}")
        print(f" from region {det.NR1UYL} to region {det.NR2UYL}")
        print(" normalisation factor:",det.USNRYL)
        print(" normalisatoin cross section:",det.SGUSYL)
        print(" low energy neutron scoring:",det.LLNUYL)
        print(f" min/max energies: {det.EYLLOW} {det.EYLHGH} GeV")
        print(" number of energy or other quantity intervals:",det.NEYLBN)
        print(" first variable bin width:",det.DEYLBN)
        print(f" second variable min/max: {det.AYLLOW} {det.AYLHGH} rad")

    def getBins(self,det):
        """ Return lin or log energy bins depending on the value of i """
        ie, ia, i4 = getType(det.ITUSYL)
        if ie < 0:
            return getLogBins(det.NEYLBN, det.EYLLOW, det.EYLHGH)
        else:
            return getLinBins(det.NEYLBN, det.EYLLOW, det.EYLHGH)

    def hist(self,det):
        """ Create histogram for the given detector """
        if det.NEYLBN == 0:
            logger.warning(f"Not saving detector {det.name} into ROOT file since it has 0 energy bins: {det.elow} < E < {det.ehigh}")
            logger.warning("         This happens for neutron-contributing estimators if max scoring energy is below groupwise max energy, 20 MeV.")
            return None

        ie, ia, i4 = getType(det.ITUSYL)
        var1 = getVarTitle(ie)
        var2 = getVarTitle(ia)

        title = fluka.particle.get(det.IDUSYL, "undefined")
        title += " #diamond "
        if int(det.NR1UYL) == -1 and int(det.NR2UYL) == -2:
            if det.IDUSYL > -800.0: # see WHAT(2)
                title += "Emerging Inelastic yield"
            else:
                title += "Entering Inelastic yield"
        else:
            title += " reg %d #rightarrow %d " % (det.NR1UYL, det.NR2UYL)
        title += " #diamond "
        title += var2[0]
        title += f": {det.AYLLOW:.5g} to {det.AYLHGH:.5g} {var2[1]}"
        title += ";%s [%s]" % (var1[0:2])

        # y-axis
        title += ";" + getDistTitle(det.IXUSYL, var1, var2)


        return ROOT.TH1F(det.TITUYL, title, det.NEYLBN, self.getBins(det))


    def readHeader(self, filename):
        f = super().readHeader(filename)

        data = fortran.read(f)

        if data is None:
            logger.error("Invalid usrysuw file")
            sys.exit(1)

        size = len(data)
        logger.debug(f"{size=}")
        IJUSYL, JTUSYL, PUSRYL, SQSUYL, UUSRYL, VUSRYL, WUSRYL = struct.unpack("=2i5f", data)

        logger.info(f"Projectile: {IJUSYL}, its lab. momentum: {PUSRYL}, lab. direction: {UUSRYL} {VUSRYL} {WUSRYL}")
        logger.info(f"Target: {JTUSYL}")
        logger.info(f"CMS energy for Lorentz transformation: {SQSUYL} GeV")

        while True:
            data = fortran.read(f)
            if data is None:
                logger.debug("data = None -> break")
                break
            size = len(data)
            logger.debug(f"read while True: \t{size=}")
            if size == 70: # new detector
                logger.debug(f" Reading the header...\t{size=}")
                header = struct.unpack("=i10s3i2i2fi2fif2f", data)
                det = Data.Detector()
                det.NYL = header[0]
                det.TITUYL = header[1].decode('utf-8').strip() # detector title (sdum)
                det.ITUSYL = header[2] # what(1)
                det.IXUSYL = header[3] # what(6)
                det.IDUSYL = header[4]
                det.NR1UYL = header[5]
                det.NR2UYL = header[6]
                det.USNRYL = header[7]
                det.SGUSYL = header[8]
                det.LLNUYL = header[9]
                if det.LLNUYL == 1:
                    logger.error(f"{det.TITUYL}: No groupwise low energy neutron scoring is implemented yet. Adjust i4 in WHAT(1) in the USRYIELD cards.")
                    sys.exit(1)
                det.EYLLOW = header[10]
                det.EYLHGH = header[11]
                det.NEYLBN = header[12]
                det.DEYLBN = header[13]
                det.AYLLOW = header[14]
                det.AYLHGH = header[15]
                self.detector.append(det)
            elif size == 14: # and data.decode('utf8')[:10] == "STATISTICS":
                self.statpos = f.tell()
                break
                # logger.debug(f" Reading STATISTICS...\t{size=}")
                # for det in self.detector:
                #     data = Data.unpackArray(fortran.read(f))
                #     logger.debug(f"  detector {det.NYL}")
                    # det.total = data[0]
                    # det.totalerror = data[1]
                    # print("total:",det.total, det.totalerror)
                    #                    for j in range(6):
                    #                        fortran.skip(f)
            # elif size == det.NEYLBN*4:
            #     logger.debug(f" Reading the data block\t{size=}")
            # elif size == 8:
            #     det.total, det.totalerror = struct.unpack("=2f", data)
            #     logger.debug(f"{det.total=} {det.totalerror=}")
            # else:
            #     logger.debug(f"else {size=}")
            #     if det.LLNUYL: # low energy neutrons
            #         logger.debug(f"\t low energy neutrons")
            #         det.ngroup = struct.unpack("=i",data[:4])[0]
            #         det.egroup = struct.unpack("=%df"%(det.ngroup+1), data[4:])
            #         print(det.ngroup)
            #     else:
            #         det.ngroup = 0
            #         det.egroup = ()
                # size  = (det.ngroup+det.ne) * 4
                # if size != fortran.skip(f):
                #     raise IOError("Invalid USRTRACK file")
                # f.close()

    def readStat(self, i, lowneu):# almost the same as ustsuw2root. TODO: use a common base class
        """ Read detector # det statistical data """
        if self.statpos < 0:
            logger.warning(f"Negative statpos: {self.statpos=}")
            return None

        logger.debug(f"{self.statpos=}")

        with open(self.file,"rb") as f:
            f.seek(self.statpos)
            for _ in range(7*i+3):
                fortran.skip(f) # skip previous detectors
            data = fortran.read(f)

        return data

    def readData(self, i, lowneu): # almost the same as ustsuw2root. TODO: use a common base class
        """Read detector det data structure

        """
        with open(self.file,"rb") as f:
            fortran.skip(f) # Skip the header read by super()
            for _ in range(2*i+2):
                fortran.skip(f)     # Previous Detector Header & Data
            data = fortran.read(f)  # Current Detector Data

        return data


def main():
    """ Converts usysuw output into a ROOT TH2F histogram """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('usryield', type=str, help='usysuw binary output')
    parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')

    args = parser.parse_args()

    loglevel = logging.INFO if args.verbose else logging.WARNING

    logging.basicConfig(
        encoding='utf-8',
        level=loglevel,
        format="{levelname}: {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )#, filename='usysuw2root.log')

    logger.warning("The USRYIELD converter is not thoroughly tested yet. Compare the ROOT histograms (both values and errors) with the FLUKA-generated %s." % args.usryield.replace(".usryield", "_tab.lis"))

    if not path.isfile(args.usryield):
        logger.error("File %s does not exist." % args.usryield)
        return 1

    if args.root == "":
        rootFileName = "%s%s" % (args.usryield,".root")
    else:
        rootFileName = args.root

    logger.debug(rootFileName)

    b = USYSUW()
    b.setVerbose(args.verbose)
    b.readHeader(args.usryield) # data file closed here

    ND = len(b.detector)

    if args.verbose:
        b.sayHeader()
        logger.info("%s %d %s found:" % ('*'*20, ND, "estimator" if ND==1 else "estimators"))
        for i in range(ND):
            b.say(i)
            print("")

    fout = ROOT.TFile(rootFileName, "recreate")
    for i in range(ND):
        det = b.detector[i]
        val = Data.unpackArray(b.readData(i,det.LLNUYL))
        logger.debug(f"{val=}")
        err = Data.unpackArray(b.readStat(i,det.LLNUYL))
        logger.debug(f"{err=}")

        assert len(val) == len(err), "val and err length are different: %d %d" % (len(val), len(err))

        h = b.hist(det)

        if h:
            n = h.GetNbinsX()
            for i in range(n):
                h.SetBinContent(i+1, val[i])
                h.SetBinError(i+1, err[n-i-1]*val[i])
            h.SetEntries(b.weight)
            h.Write()

if __name__=="__main__":
    sys.exit(main())
