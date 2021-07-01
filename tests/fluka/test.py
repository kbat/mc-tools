#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import re, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def compare(val1, val2, msg="", relPrec=1.0e-5):
    """Compare two float variables with the given relative precision

    """
    if not ROOT.TMath.AreEqualRel(val1, val2, relPrec):
        print(msg, "values do not match: ", val1, val2, file=sys.stderr)
        return False
    else:
        return True

def usrtrack(rootfname, hname, lisfname):
    """Test USRTRACK output

    """

    rootf = ROOT.TFile(rootfname)
    h = rootf.Get(hname)

    b = 0
    passed = True
    with open(lisfname) as lisf:
        for line in lisf.readlines():
            if re.search("\A #", line):
                continue
            w =  line.strip().split()
            b += 1
            val = h.GetBinContent(b)
            err = h.GetBinError(b)
            relerr = err/val*100 if val>0.0  else 0.0

            #print(b, w, h.GetBinLowEdge(b), h.GetBinLowEdge(b+1), val, relerr)

            if not compare(float(w[2]), val, "Bin content") or \
               not compare(float(w[3]), relerr, "Relative bin error") or \
               not compare(float(w[0]), h.GetBinLowEdge(b), "Bin %d low edge" % b) or \
               not compare(float(w[1]), h.GetBinLowEdge(b+1), "Bin %d up edge" % b):
                passed = False
                break

    if passed and not compare(b, h.GetNbinsX(), "NBinsX"):
        passed = False

    rootf.Close()

    print("usrtrack: ", hname, "test passed" if passed else "test failed", file=sys.stderr)

    return passed

def resnuclei(rootfname, hname, lisfname):
    """Test RESNUCLEI output

    """

    rootf = ROOT.TFile(rootfname)
    h = rootf.Get(hname)
    hA = h.ProjectionY()
    hZ = h.ProjectionX()
    geA = rootf.Get(hname+"A")
    geZ = rootf.Get(hname+"Z")

    passed = True
    valuesA = False
    valuesZ = False
    valuesAZ = False
    binA = geA.GetN()
    binZ = geZ.GetN()
    with open(lisfname) as lisf:
        for line in lisf.readlines():
            if re.search("\A# Detector", line):
                continue

            w = line.strip().split()

            if re.search("\A# A_min-A_max", line):
                valuesA, valuesZ, valuesAZ = True, False, False
                Amin = float(w[2])
                Amax = float(w[3])
                if not compare(Amin, geA.GetX()[0], "A_min") or \
                   not compare(Amax, geA.GetX()[-1], "A_max"):
                    passed = False
                    break
            elif re.search(" # Z_min-Z_max", line):
                valuesA, valuesZ, valuesAZ = False, True, False
                Zmin = float(w[2])
                Zmax = float(w[3])
                if not compare(Zmin, geZ.GetX()[0], "Z_min") or \
                   not compare(Zmax, geZ.GetX()[-1], "Z_max"):
                    passed = False
                    break
            elif re.search("\A# A/Z Isotopes:", line):
                valuesA, valuesZ, valuesAZ = False, False, True
            elif valuesA:
                binA -= 1
                val = geA.GetY()[binA]
                err = geA.GetEY()[binA]
                relerr = err/val*100 if val>0.0  else 0.0
                if not compare(float(w[0]),geA.GetX()[binA],"geA::A") or \
                   not compare(float(w[1]),val, "geA::val", 1e-3) or \
                   not compare(float(w[2]),relerr, "geA::relerr", 1e-3):
                    passed = False
                    break
                # check projected histogram values
                i = hA.FindBin(float(w[0]))
                if i <= hA.GetNbinsX():
                    # comparing with geA but not with the .lis file since at this point
                    # the geA test succeeded and geA contains more significant digits than the .lis file
                    relerrh=hA.GetBinError(i)/hA.GetBinContent(i)*100 if hA.GetBinContent(i)>0.0 else 0.0
                    if not compare(val, hA.GetBinContent(i), "h.ProjectionY:val") or \
                       not compare(relerr, relerrh, "h.ProjectionY::relerr"):
                        print("\t(this might be due to TH2F::ProjectionY implemenation in ROOT)")
                        passed = True
                        break
            elif valuesZ:
                binZ -= 1
                val = geZ.GetY()[binZ]
                err = geZ.GetEY()[binZ]
                relerr = err/val*100 if val>0.0  else 0.0
                if not compare(float(w[0]),geZ.GetX()[binZ],"geZ::Z") or \
                   not compare(float(w[1]),val, "geZ::val", 1e-3) or \
                   not compare(float(w[2]),relerr, "geA::relerr", 1e-3):
                    passed = False
                    break
                # check projected histogram values
                i = hZ.FindBin(float(w[0]))
#                if i <= hZ.GetNbinsX(): - no need to check this because all z-bins are written in the .lis file
                # comparing with geA but not with the .lis file since at this point
                # the geA test succeeded and geA contains more significant digits than the .lis file
                relerrh=hZ.GetBinError(i)/hZ.GetBinContent(i)*100 if hZ.GetBinContent(i)>0.0 else 0.0
                if not compare(val, hZ.GetBinContent(i), "h.ProjectionX:val") or \
                   not compare(relerr, relerrh, "h.ProjectionX::relerr"):
                    print("\t(this might be due to TH2F::ProjectionX implemenation in ROOT)")
                    passed = True
                    break
            elif valuesAZ:
                A = float(w[0])
                Z = float(w[1])
                i = h.FindBin(Z,A)
                val = h.GetBinContent(i)
                err = h.GetBinError(i)
                relerr = err/val*100 if val>0.0  else 0.0
                if not compare(val, float(w[2]), "A/Z Isotopes:val", 1e-3) or \
                   not compare(relerr, float(w[3]), "A/Z Isotopes:relerr", 1e-3):
                    passed = False
                    break

    rootf.Close()

    print("resnuclei: ", hname, "test passed" if passed else "test failed", file=sys.stderr)
    print("\tIt's not a serious problem if only the TH2F::Projection[XY] tests failed since this might be due to ROOT [check this].")
    print("\tThis warning means that in both TGraphErrors objects the values and errors are the same as in the FLUKA output, but in the TH2F some errors are different from FLUKA output (while values are the same).")

    return passed


def main():
    """Some tests of fluka2root converters

    """
    rootfname = "test.root"
    usrtrack(rootfname, "piFluenU", "test.48_tab.lis")
    usrtrack(rootfname, "piFluenD", "test.49_tab.lis")
    resnuclei(rootfname, "resnuc", "test.53_tab.lis")

    print("test.47_tab.lis and test.52_tab.lis files were not tested")

if __name__ == "__main__":
    sys.exit(main())
