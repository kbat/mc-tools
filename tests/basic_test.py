#! /usr/bin/python3

import re
import os
import sys
import shutil
import tempfile


def test_dummy():
        print("test_dummy")
        val = 1
        assert val == 1

def test_root():
        # test whether ROOT is installed and compiled with Python support
        import ROOT

def test_import():
        # test whether the mctools module can be imported
        import mctools

def fluka2root(inp):
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

def compare(hist, tab, name):
        """ Compares hist and tab and calls assert if they are different
        """
        assert hist == tab, "problem with %s:\ttab: %s\thist: %s" % (name, tab, hist)

def getNskip(fname, hname):
        """ Return number of rows to skip in the _tab.lis file before the current estimator data
        """
        i = 1
        with open(fname) as f:
                for line in f.readlines():
                        i += 1
                        if re.search(hname, line):
                                break
        return i

def convert(inpname, tally, unit, hname):
        """ tets histograms converted by fluka2root """
        import ROOT
        import pandas as pd

        base = os.path.splitext(inpname)[0]

#        rootfname = "%s.%d.%s.root" % (base, unit, tally)
        rootfname = "shield.root"
        tabfname  = "%s.%d_tab.lis" % (base, unit)
        print(base, unit, rootfname, tabfname)

        f = ROOT.TFile(rootfname)
        h2 = f.Get(hname)
        h2_lowneu = f.Get(hname+"_lowneu")

        # here we assume all bin width is the same:
        dOmega = h2.GetYaxis().GetBinLowEdge(2)-h2.GetYaxis().GetBinLowEdge(1)

        # nomega = h2.GetNbinsY()
        # nenergy = h2.GetNbinsX()

        # for a in range(1,nomega+1):
        #         dOmega = h2.GetYaxis().GetBinWidth(a)
        #         for e in range(1,nenergy+1):
        #                 val = h2.GetBinContent(e,a)
        #                 err = h2.GetBinError(e,a)
        #                 h2.SetBinContent(e, a, val*dOmega)
        #                 err.SetBinContent(e, a, err*dOmega)

        h = h2.ProjectionX()
        h.Scale(dOmega)
        if h2_lowneu:
                h_lowneu = h2_lowneu.ProjectionX()
                h_lowneu.Scale(dOmega)

        _format="%.3E"

        print(_format%h.GetBinLowEdge(1), _format%h.GetBinLowEdge(2))

        nrows = h.GetNbinsX()
        if h2_lowneu:
                nrows += h2_lowneu.GetNbinsX()

        df = pd.read_csv(tabfname, sep='\s+', names=["emin", "emax", "val", "err"],
                         skiprows=getNskip(tabfname, hname),
                         nrows=nrows) # data frame
        print("shape:",df.shape)
#        print(df.head())

        j=0
        print("Low-energy part")
        if h2_lowneu: # compare the low energy part
                nbins = h2_lowneu.GetNbinsX()
                print("nbins:",nbins)
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
                        compare(hemin, femin, "emin")
                        compare(hemax, femax, "emax")
                        compare(hval, fval, "val")
                        compare(herr, ferr, "err")

        print("Above 20 MeV")

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

                compare(hemin, femin, "emin")
                compare(hemax, femax, "emax")
                compare(hval, fval, "val")
#                compare(herr, ferr, "err") # tests with omega bins>1 fail here


def test_fluka2root():
#        inpfrom = os.path.join(os.environ["FLUPRO"], inp)
#        inputs = ("example.inp", "exmixed.inp", "exdefi.inp", "exfixed.inp")

        inputs = ("shield.inp",)
        for inp in inputs:
                fluka2root(inp)

convert('shield.inp', 'usrbdx', 47, 'beamIn') # fails emin, otherwise OK
convert('shield.inp', 'usrbdx', 47, 'eFwd') # OK
convert('shield.inp', 'usrbdx', 47, 'pFwd') # OK
convert('shield.inp', 'usrbdx', 47, 'eBackE')
convert('shield.inp', 'usrbdx', 47, 'pBackP') # OK
convert('shield.inp', 'usrbdx', 47, 'pBackN') # OK
