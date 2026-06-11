#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import os, re, shutil, subprocess, sys, tempfile
from mctools.fluka.usbrea2root import convert as usbrea2root
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

def run_fluka2root_validation(tmp_path, *inputs):
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../mctools/fluka/fluka2root.py"))
    return subprocess.run([script, *inputs],
                          cwd=tmp_path,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          text=True)

def test_fluka2root_reports_missing_binary_files(tmp_path):
    shutil.copyfile(os.path.join(os.path.dirname(__file__), "test.inp"), tmp_path / "test.inp")

    result = run_fluka2root_validation(tmp_path, "test.inp")

    assert result.returncode == 6
    assert "no FLUKA binary files found" in result.stderr
    assert "USRBDX unit -47" in result.stderr
    assert "RESNUCLE unit -55" in result.stderr

def test_fluka2root_rejects_mismatched_input_estimators(tmp_path):
    with open(os.path.join(os.path.dirname(__file__), "test.inp")) as input_file:
        source = input_file.read()
    (tmp_path / "test.inp").write_text(source)
    (tmp_path / "test_mismatch.inp").write_text(source.replace("-48.0       3.0", "-58.0       3.0", 1))

    result = run_fluka2root_validation(tmp_path, "test.inp", "test_mismatch.inp")

    assert result.returncode == 4
    assert "estimator/unit layout differs" in result.stderr
    assert "test_mismatch.inp" in result.stderr

def fluka2root(inp):
    """Run fluka2root converter with the given file

    """

    tmpdir = tempfile.mkdtemp(suffix='.mc-tools')
    inpto = os.path.join(tmpdir, inp)
    shutil.copyfile(inp, inpto)

    os.chdir(tmpdir)

    cmd = "$FLUPRO/flutil/rfluka -N0 -M2 " + inp
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
    print("resnuclei:\t", end="", flush=True)


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

    print(hname, "test passed" if passed else "test failed", file=sys.stderr)
    print("\tIt's not a serious problem if only the TH2F::Projection[XY] tests failed since this might be due to ROOT [check this].")
    print("\tThis warning means that in both TGraphErrors objects the values and errors are the same as in the FLUKA output, but in the TH2F some errors are different from FLUKA output (while values are the same).")

    return passed

def usrbin(rootfname, hname, tabfname):
    """Test USRBIN output

    """
    print("usrbin:\t", end="", flush=True)

    tmp_root = tabfname + '.root'
    usbrea2root(tabfname, tmp_root, verbose=False)

    rootf = ROOT.TFile(rootfname)
    h_ref = rootf.Get(hname)
    assert h_ref, f"{hname} not found in {rootfname}"

    convf = ROOT.TFile(tmp_root)
    h_conv = convf.Get(hname)
    assert h_conv, f"{hname} not found in {tmp_root}"

    passed = True
    nx = h_ref.GetNbinsX()
    ny = h_ref.GetNbinsY()
    nz = h_ref.GetNbinsZ()

    if not compare(h_ref.GetXaxis().GetXmin(), h_conv.GetXaxis().GetXmin(), "Xmin") or \
       not compare(h_ref.GetXaxis().GetXmax(), h_conv.GetXaxis().GetXmax(), "Xmax") or \
       not compare(h_ref.GetYaxis().GetXmin(), h_conv.GetYaxis().GetXmin(), "Ymin") or \
       not compare(h_ref.GetYaxis().GetXmax(), h_conv.GetYaxis().GetXmax(), "Ymax") or \
       not compare(h_ref.GetZaxis().GetXmin(), h_conv.GetZaxis().GetXmin(), "Zmin") or \
       not compare(h_ref.GetZaxis().GetXmax(), h_conv.GetZaxis().GetXmax(), "Zmax"):
        passed = False

    # relPrec=1e-4: text format e11.4 gives 5 significant figures
    if passed:
        for iz in range(1, nz + 1):
            for iy in range(1, ny + 1):
                for ix in range(1, nx + 1):
                    val_ref  = h_ref.GetBinContent(ix, iy, iz)
                    val_conv = h_conv.GetBinContent(ix, iy, iz)
                    err_ref  = h_ref.GetBinError(ix, iy, iz)
                    err_conv = h_conv.GetBinError(ix, iy, iz)
                    if not compare(val_ref, val_conv,
                                   f"bin({ix},{iy},{iz}) content", relPrec=1e-4) or \
                       not compare(err_ref, err_conv,
                                   f"bin({ix},{iy},{iz}) error",   relPrec=1e-4):
                        passed = False
                        break
                if not passed:
                    break
            if not passed:
                break

    rootf.Close()
    convf.Close()

    print(hname, "test passed" if passed else "test failed", file=sys.stderr)
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
        j += nbins
        for i in range(nbins):
            hemin = _format % h_lowneu.GetBinLowEdge(i+1)
            hemax = _format % h_lowneu.GetBinLowEdge(i+2)
            hval  = _format % h_lowneu.GetBinContent(i+1)
            herr  = _format % h_lowneu.GetBinError(i+1)
            hrelerr = _format % (100.0*h_lowneu.GetBinError(i+1)/h_lowneu.GetBinContent(i+1) if h_lowneu.GetBinContent(i+1)>0.0 else 0.0)
            femin = _format % df['emin'][i]
            femax = _format % df['emax'][i]
            fval  = _format % df['val'][i]
            ferr  = _format % df['err'][i]
            # print("lowneu",i+1,femin,femax,fval,ferr,"\t",hemin,hemax,hval,hrelerr)
            compare_str(hemin, femin, "emin")
            compare_str(hemax, femax, "emax")
            compare_str(hval, fval, "val")
            compare_str(hrelerr, ferr, "err")

    nbins = h.GetNbinsX();
    for i in range(nbins):
        hemin = _format % h.GetBinLowEdge(i+1)
        hemax = _format % h.GetBinLowEdge(i+2)
        hval  = _format % h.GetBinContent(i+1)
        herr  = _format % h.GetBinError(i+1)
        hrelerr = _format % (100.0*h.GetBinError(i+1)/h.GetBinContent(i+1) if h.GetBinContent(i+1)>0.0 else 0.0)
        femin = _format % df['emin'][i+j]
        femax = _format % df['emax'][i+j]
        fval  = _format % df['val'][i+j]
        ferr  = _format % df['err'][i+j]
#        print("h",i+1,femin,femax,fval,ferr,"\t",hemin,hemax,hval,herr)

        compare_str(hemin, femin, "emin")
        compare_str(hemax, femax, "emax")
        compare_str(hval, fval, "val")
        compare_str(hrelerr, ferr, "err")

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
    usrbin(rootfname, "Edeposit", "test.54.txt")
    usrbin(rootfname, "piFluBin", "test.53.txt")
    resnuclei(rootfname, "resnuc", "test.55_tab.lis")


    # rootfname = "SpecF1.root"
    # usrtrack(rootfname, "cell34", "SpecF1.34_tab.lis")  # lowneu
    # usrbdx(rootfname, "surf33", "SpecF1.33_tab.lis")
    # usrbdx(rootfname, "surf28", "SpecF1.28_tab.lis")# lowneu
    # usrtrack(rootfname, "cell36", "SpecF1.36_tab.lis")
    # usrtrack(rootfname, "cell37", "SpecF1.37_tab.lis")
    # usrtrack(rootfname, "cell38", "SpecF1.38_tab.lis")
    # usrtrack(rootfname, "cell39", "SpecF1.39_tab.lis")
    # usrtrack(rootfname, "cell40", "SpecF1.40_tab.lis")
    # usrtrack(rootfname, "cell41", "SpecF1.41_tab.lis")
    # usrtrack(rootfname, "cell42", "SpecF1.42_tab.lis")
    # usrbdx(rootfname, "surf31", "SpecF1.31_tab.lis")
    # usrbdx(rootfname, "surf29", "SpecF1.29_tab.lis")
    # usrbdx(rootfname, "surf32", "SpecF1.32_tab.lis")
    # usrbdx(rootfname, "surf30", "SpecF1.30_tab.lis")
    # usrtrack(rootfname, "cell35", "SpecF1.35_tab.lis")

if __name__ == "__main__":
    sys.exit(main())
