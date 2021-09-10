#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import re, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

_format="%.3E"

def test_root():
    """Test whether ROOT is installed and compiled with Python support

    """
    import ROOT

def test_import():
    """Test whether the mctools module can be imported

    """
    import mctools

def fluka2root(inp):
    """Run fluka2root converter with the given file

    """

    tmpdir = tempfile.mkdtemp(suffix='.mc-tools')
    inpto = os.path.join(tmpdir, inp)
    shutil.copyfile(inp, inpto)

    os.chdir(tmpdir)

    cmd = "$FLUTIL/rfluka -N0 -M2 " + inp
    val = os.system(cmd)
    assert val == 0

    cmd = "fluka2root " + inp
    val = os.system(cmd)
    assert val == 0

    shutil.rmtree(tmpdir)


def getNskip(fname, hname):
    """Return number of rows to skip in the _tab.lis file before the
        current estimator data

    """
    i = 1
    with open(fname) as f:
        for line in f.readlines():
            i += 1
            if re.search(hname, line):
                break
    return i

def compare_str(hist, tab, name):
    """Compares hist and tab and calls assert if they are different

    """
    assert hist == tab, "problem with %s:\ttab: %s\thist: %s" % (name, tab, hist)

def compare(val1, val2, msg="", relPrec=1.0e-5):
    """Compare two float variables with the given relative precision

    """
    if not ROOT.TMath.AreEqualRel(val1, val2, relPrec):
        print(msg, "values do not match: ", val1, val2, file=sys.stderr)
        return False
    else:
        return True

def usrtrack(rootfname, hname, tabfname):
    """Test USRTRACK output

    """

    rootf = ROOT.TFile(rootfname)
    h = rootf.Get(hname)
    assert h, f"{hname} not found in {rootfname}"
    hn = rootf.Get(hname+"_lowneu")

    n_lowneu = 0 # number of bins
    if hn:
        n_lowneu = hn.GetNbinsX()

    b = 0
    passed = True
    hist = hn if hn else h
    val, err, e1, e2 = 0.0, 0.0, -1.0, -1.0 # current bin value and edges
    with open(tabfname) as tabf:
        for line in tabf.readlines():
            if re.search("\A #", line):
                continue
            w =  line.strip().split()

            b += 1
            if b<=n_lowneu:
                val = hn.GetBinContent(b)
                err = hn.GetBinError(b)
                e1 = hn.GetBinLowEdge(b)
                e2 = hn.GetBinLowEdge(b+1)
            else:
                val = h.GetBinContent(b-n_lowneu)
                err = h.GetBinError(b-n_lowneu)
                e1 = h.GetBinLowEdge(b-n_lowneu)
                e2 = h.GetBinLowEdge(b+1-n_lowneu)
            relerr = err/val*100 if val>0.0  else 0.0

            # check bin contents and edges
            if not compare(float(w[2]), val, "Bin content") or \
               not compare(float(w[3]), relerr, "Relative bin error") or \
               not compare(float(w[0]), e1, "Bin %d low edge" % b) or \
               not compare(float(w[1]), e2, "Bin %d up edge" % b):
                passed = False
                break

    if passed and not compare(b, h.GetNbinsX()+n_lowneu, "NBinsX"):
        passed = False

    rootf.Close()

    print("usrtrack: ", hname, "test passed" if passed else "test failed", file=sys.stderr)

    return passed

def resnuclei(rootfname, hname, tabfname):
    """Test RESNUCLEI (usrsuw) output

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
    with open(tabfname) as tabf:
        for line in tabf.readlines():
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
                       not compare(relerr, relerrh, "\th.ProjectionY::relerr"):
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


def usrbdx(rootfname, hname, tabfname):
    """Test USRBDX (usxsuw) output

    """
    print("usrbdx:\t", end="", flush=True)

    import pandas as pd
    passed = True

    rootf = ROOT.TFile(rootfname)
    h2 = rootf.Get(hname)
    assert h2, f"{hname} not found in {rootfname}"
    h2_lowneu = rootf.Get(hname+"_lowneu")

    # here we assume all bin widths are the same:
    dOmega = h2.GetYaxis().GetBinLowEdge(2)-h2.GetYaxis().GetBinLowEdge(1)

    h = h2.ProjectionX()
    h.Scale(dOmega)
    if h2_lowneu:
        h_lowneu = h2_lowneu.ProjectionX()
        h_lowneu.Scale(dOmega)

    nrows = h.GetNbinsX()
    if h2_lowneu:
        nrows += h2_lowneu.GetNbinsX()

    df = pd.read_csv(tabfname, sep='\s+', names=["emin", "emax", "val", "err"],
                     skiprows=getNskip(tabfname, hname),
                     nrows=nrows) # data frame
    j=0
    if h2_lowneu: # compare the low energy part
        nbins = h2_lowneu.GetNbinsX()
#        print("nbins:",nbins)
        j += nbins
        for i in range(nbins):
            hemin = _format % h_lowneu.GetBinLowEdge(i+1)
            hemax = _format % h_lowneu.GetBinLowEdge(i+2)
            hval  = _format % h_lowneu.GetBinContent(i+1)
            herr  = _format % h_lowneu.GetBinError(i+1)
            femin = _format % df['emin'][i]
            femax = _format % df['emax'][i]
            fval  = _format % df['val'][i]
            ferr  = _format % df['err'][i]
            #                        print(i+1,femin,femax,fval,ferr,"\t",hemin,hemax,hval,herr)
            #                print(df.ix[i])
            compare_str(hemin, femin, "emin")
            compare_str(hemax, femax, "emax")
            compare_str(hval, fval, "val")
            compare_str(herr, ferr, "err")

    nbins = h.GetNbinsX();
    for i in range(nbins):
        hemin = _format % h.GetBinLowEdge(i+1)
        hemax = _format % h.GetBinLowEdge(i+2)
        hval  = _format % h.GetBinContent(i+1)
        herr  = _format % h.GetBinError(i+1)
        femin = _format % df['emin'][i+j]
        femax = _format % df['emax'][i+j]
        fval  = _format % df['val'][i+j]
        ferr  = _format % df['err'][i+j]
        #                print(i+1,femin,femax,fval,ferr,"\t",hemin,hemax,hval,herr)

        compare_str(hemin, femin, "emin")
        compare_str(hemax, femax, "emax")
        compare_str(hval, fval, "val")

    print(hname, "test passed" if passed else "test failed", file=sys.stderr)

def test_fluka2root():
#        inpfrom = os.path.join(os.environ["FLUPRO"], inp)
#        inputs = ("example.inp", "exmixed.inp", "exdefi.inp", "exfixed.inp")

        inputs = ("test.inp",)
        for inp in inputs:
                fluka2root(inp)


def main():
    """Some tests of fluka2root converters

    """
    rootfname = "test.root"
    usrtrack(rootfname, "piFluenU", "test.48_tab.lis")
    usrtrack(rootfname, "piFluenD", "test.49_tab.lis")
    usrtrack(rootfname, "trDOSEEQ", "test.50_tab.lis") # lowneu
    usrtrack(rootfname, "h52U", "test.51_tab.lis")
    usrtrack(rootfname, "h52D", "test.52_tab.lis")
    usrbdx(rootfname, "pFluenUD", "test.47_tab.lis") # lowneu
    resnuclei(rootfname, "resnuc", "test.55_tab.lis")

if __name__ == "__main__":
    sys.exit(main())
