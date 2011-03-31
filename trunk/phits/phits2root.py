#! /usr/bin/python -W all

import sys, re, string
from phits import TallyOutputParser
from ROOT import ROOT, TH1F, TFile


def main():
    verbose = '-v' in sys.argv
    if verbose:
        sys.argv.remove("-v")

    fname_in = sys.argv[1]
    fname_out = re.sub("\....$", ".root", fname_in)
    if fname_in == fname_out:
        fname_out = fname_in + ".root"
    print fname_out
        
    p = TallyOutputParser(fname_in)
    print p.getSections()
#    print p.FixSectName("T - H e a t")
#    print p.has_section(" T - H e a t ")

    section = p.getSections()[0]
    title = p.get(section, "title")
    xtitle = p.get(section, 'x')
    ytitle = p.get(section, 'y')
    xmin = float(p.get(section, "emin"))
    xmax = float(p.get(section, "emax"))
    nbins = int(p.get(section, "ne"))

    hist = TH1F("h", "%s;%s;%s" % (title, xtitle, ytitle), nbins, xmin, xmax)
    for i in range(nbins):
        val = p.data[i]
        err = p.errors[i]*val
        hist.SetBinContent(i+1, val)
        hist.SetBinError(i+1, err)

    fout = TFile(fname_out, "recreate")
    hist.Write()
    fout.Close()


if __name__ == "__main__":
    sys.exit(main())
