#! /usr/bin/python2 -W all
#
# https://github.com/kbat/mc-tools
#

from __future__ import print_function
import re, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def compare(val1, val2, msg="", relPrec=1.0e-5):
    """ Compare two float variables with the given relative precision
    """
    if not ROOT.TMath.AreEqualRel(val1, val2, relPrec):
        print(msg, "values do not match: ", val1, val2, file=sys.stderr)
        return False
    else:
        return True

def usrtrack(rootfname, hname, lisfname):
    """ Test USRTRACK output
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

    print(hname, "usrtrack test passed" if passed else "test failed", file=sys.stderr)

    return passed
    

def main():
    """Some tests of the FLUKA converters
    """
    rootfname = "test.root"
    usrtrack(rootfname, "piFluenU", "test.48_tab.lis")
    usrtrack(rootfname, "piFluenD", "test.49_tab.lis")

if __name__ == "__main__":
    sys.exit(main())
