#! /usr/bin/python -W all

import sys, re, string
from phits import TallyOutputParser
from ROOT import ROOT, TH1F, TH2F, TFile


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
    print "sections: ", p.getSections()
#    print p.FixSectName("T - H e a t")
#    print p.has_section(" T - H e a t ")

    section = p.getSections()[0]
#    print "options: ", p.sections[section]

    xtitle = p.get(section, 'x')
    ytitle = p.get(section, 'y')
    ztitle = p.get(section, 'z')

    etype = p.get(section, 'e-type')
    print "e-type: ", etype

    title = p.get(section, "title")
    axis = p.get(section, 'axis')
    print "axis: ", axis

    if p.is_1d(section):
        # using axis[0] since the 1st letter is being used in 
        # 1-dimentional axes (eng, reg, x, y, z and r)
        xmin = float(p.get(section, "%smin" % axis[0]))
        xmax = float(p.get(section, "%smax" % axis[0]))
        nbins = int(p.get(section, "n%s" % axis[0]))
        
        print "1d:\t", nbins, xmin, xmax

        hist = TH1F("h", "%s;%s;%s" % (title, xtitle, ytitle), nbins, xmin, xmax)
        for i in range(nbins):
            val = p.data[i]
            print val
            hist.SetBinContent(i+1, val)
            if len(p.errors):
                err = p.errors[i]*val
                hist.SetBinError(i+1, err)

    elif p.is_2d(section):
        print "2d"
        xmin = float(p.get(section, "%smin" % axis[1]))
        xmax = float(p.get(section, "%smax" % axis[1]))
        ymin = float(p.get(section, "%smin" % axis[0]))
        ymax = float(p.get(section, "%smax" % axis[0]))
        nbinsx = int(p.get(section, "n%s" % axis[1]))
        nbinsy = int(p.get(section, "n%s" % axis[0]))
        print xmin, xmax, ymin, ymax, nbinsx, nbinsy
        hist = TH2F("h", "%s;%s;%s;%s" % (title, xtitle, ytitle, ztitle), nbinsx, xmin, xmax, nbinsy, ymin, ymax) # implement runtime code generation for [xyz]title here !!!
        for y in range(nbinsy-1, -1, -1):
            for x in range(nbinsx):
                d = p.data[x+(nbinsy-1-y)*nbinsx]
                hist.SetBinContent(x+1, y+1, d)
    else:
        print("neither 1D nor 2D axis -> exit")
        return 1

    
    fout = TFile(fname_out, "recreate")
    hist.Write()
    fout.Close()


if __name__ == "__main__":
    sys.exit(main())
