#!/usr/bin/env python3

import os
import sys
import glob
import argparse
import tempfile
import numpy as np
from mctools.fluka import line
from math import log10
from shutil import which
from contextlib import redirect_stdout
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def inp(projectile, material, energy, include):
    """ Prints a single input file """
    print("TITLE")
    print("FLUKA cross section generator")
    line("DEFAULTS",sdum="PRECISIO")
    line("BEAM",w1=f"-{energy:.4f}",sdum=projectile)
    line("BEAMPOS",w2="5.0e4",w5="1.0")
    line("GEOBEGIN",sdum="COMBNAME")
    print("""0    0          Sphere
SPH sphere 0.0 0.0 0.0 1.0e-8
END
Target     1  +sphere
Out        3  -sphere
END
GEOEND
ASSIGNMA    BLCKHOLE       Out""")
    line("ASSIGNMA",material,"Target")

    if include:
        with open(include) as f:
            for l in f:
                l = l.strip()
                if len(l)>0:
                    print(l)

    line("RANDOMIZ", w1=1.0, w2=1.0)
    line("START", w1=1.0)
    line("STOP")

def generateInputs(args,tmp):
    """ Generate input files """
    step = (log10(args.emax) - log10(args.emin))/(args.npoints-1)
    elist = np.arange(log10(args.emin), log10(args.emax), step).tolist()
    elist.append(log10(args.emax))
    for i, e in enumerate(elist):
        E = pow(10, e)
        fname = f"sigma-{i:0>3}.inp"
        fname = os.path.join(tmp,fname);
        with open(fname, "w") as f:
            with redirect_stdout(f):
                inp(args.projectile, args.material, E, args.include)

def run(tmp):
    assert which("parallel"), "GNU parallel is not installed"

    command = f"cd {tmp} && parallel --bar $FLUPRO/flutil/rfluka -N0 -M1 ::: sigma*inp"
    return_value = os.system(command)

def parse(fname, material):
    """ Parse the given FLUKA output file """
    E0 = -1.0 # negative = not set
    inTable = False
    d = {}
    with open(fname) as f:
        for line in f:
            line = line.strip()
            if E0<0.0 and line.find("*****   BEAM ")>0:
                w = line.split()
                E0 = -float(w[6])
            if line.find("== Material composition")>0:
                inTable = True
            if inTable and line.find(material)>0:
                w = line.split()
                d[str(E0)] = w[2:]
                return d

def fixEmin(args):
    emin = args.emin
    if args.projectile == "PROTON":
        emin = max(args.emin, 1e-4) # 100 keV
    elif args.projectile == "ELECTRON":
        emin = max(args.emin, 7e-5) # 70 keV
    elif args.projectile == "PHOTON":
        emin = max(args.emin, 1e-6) # 1 keV

    if emin>args.emin:
        print(f"Warning: emin has been reduced to the min primary energy of {emin} GeV",file=sys.stderr)
        print("         Press Enter to continue",file=sys.stderr)
        input()

    return emin

def main():
    """ A simple FLUKA cross section plotter """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('projectile',  type=str,  help='Incident particle')
    parser.add_argument('material', type=str, help='Material')
    parser.add_argument('npoints',  type=int,  help='Number of energy evaluation points (log. equal intervals between Emin and Emax are assumed)')
    parser.add_argument('emin',  type=float,  help='Min energy [GeV]')
    parser.add_argument('emax',  type=float,  help='Max energy [GeV]')
    parser.add_argument('-include', default=None, dest='include', help='FLUKA deck to include (e.g. with custom material definition)', required=False)
    parser.add_argument('-o', default=None, dest='out', help='Output file name (root, xml, txt, tex, pdf, png, etc)', required=False)

    args = parser.parse_args()

    args.emin = fixEmin(args)

    assert args.emin < args.emax, "emin > emax"
    assert args.npoints > 1, "Number of energy points is too small"

    data = {}
    with tempfile.TemporaryDirectory(prefix="sigma.") as tmp:
        generateInputs(args,tmp)
        run(tmp)
        outputs = os.path.join(tmp,"*.out")
        for out in glob.glob(outputs):
            d = parse(out, args.material)
            data.update(d)

    energies = list(data.keys())
    energies.sort()
    d = {e: data[e] for e in energies}

    grIn = ROOT.TGraph()
    grIn.SetTitle("Inelastic;Energy [GeV]")
    grIn.SetMarkerStyle(ROOT.kFullCircle)
    grIn.SetMarkerColor(ROOT.kGreen+1)

    grEl = ROOT.TGraph()
    grEl.SetTitle("Elelastic;Energy [GeV]")
    grEl.SetMarkerStyle(ROOT.kFullCircle)
    grEl.SetMarkerColor(ROOT.kRed)

    grX0 = ROOT.TGraph()
    grX0.SetTitle("X0;Energy [GeV]")
    grX0.SetMarkerStyle(ROOT.kFullCircle)
    grX0.SetMarkerColor(ROOT.kBlue)

    grTotal = ROOT.TGraph()
    grTotal.SetTitle("Inel+El;Energy [GeV]")
    grTotal.SetMarkerStyle(ROOT.kFullCircle)
    grTotal.SetMarkerColor(ROOT.kBlack)

    for e in d:
        E0 = float(e)
        data = d[e]
        A,rho = map(float, data[1:3])
        sigma_in, sigma_el, sigma_X0 = (A/(float(data[i])*ROOT.TMath.Na()*rho) * 1.0e24 for i in (3,4,5))
        grIn.AddPoint(E0, sigma_in);
        grEl.AddPoint(E0, sigma_el);
        grX0.AddPoint(E0, sigma_X0);
        grTotal.AddPoint(E0, sigma_in+sigma_el);

    mg = ROOT.TMultiGraph("mg", f"{args.projectile} on {args.material};Energy [GeV];#sigma [barn]")
    leg = ROOT.TLegend(0.903, 0.78, 0.99, 0.9)
    mg.Add(grTotal, "p")
    mg.Add(grIn, "p")
    mg.Add(grEl, "p")
    leg.AddEntry(grTotal, grTotal.GetTitle())
    leg.AddEntry(grIn, grIn.GetTitle())
    leg.AddEntry(grEl, grEl.GetTitle())

    mg.Draw("ap")
    leg.Draw()
    ROOT.gPad.SetGrid()
    ROOT.gPad.Update()

    if args.out:
        if args.out.endswith(".root") or args.out.endswith(".xml") or args.out.endswith(".C"):
            mg.SaveAs(args.out)
        elif args.out.endswith(".txt"):
            with open(args.out, "w") as f:
                for e in d:
                    print(e, " ".join(map(str, d[e])), file=f)
        else:
            ROOT.gPad.Print(args.out)

    input()

if __name__ == "__main__":
    sys.exit(main())
