#! /usr/bin/python -W all

import sys, re, string
from array import array
from phits import TallyOutputParser
from ROOT import ROOT, TH1F, TH2F, TFile, TObjArray

"""
def isData(line):
    words = line.strip()
#    print words
    for w in words:
        try:
            float(w)
        except ValueError:
            return False
    return True
"""

class Angel:
    fname = None
    title  = None
    xtitle = None
    ytitle = None
    ztitle = None
    lines = []
    histos = TObjArray()
    ihist = 0 # histogram number
    fname_out = None
    def __init__(self, fname):
        self.fname = fname
        file = open(fname)
        self.lines = tuple(file.readlines())
        file.close()

        self.fname_out = re.sub("\....$", ".root", fname)
        if fname == self.fname_out:
            self.fname_out = fname + ".root"

        ipage = -1

        for iline, line in enumerate(self.lines, 0):
            line.strip()
            if re.search("newpage:", line):
                ipage += 1
                print "page: ", ipage
            elif re.search("^x:", line):
                words = line.split()
                self.xtitle = string.join(words[1:])
                print self.xtitle
            elif re.search("^y:", line):
                words = line.split()
                self.ytitle = string.join(words[1:])
                print self.ytitle
            elif re.search("^z:", line):
                print "new graph"
            elif re.search("^h:", line):
                print "one dimentional graph section"
                self.Read1DHist(iline)
            elif re.search("^h[2dc]:", line):
                print "two dimentional plot section"
                
        fout = TFile(self.fname_out, "recreate")
        self.histos.Write()
        fout.Close()


    def GetNhist(self, line):
        """
        Analyzes the section header and return the number of histograms in the section data
        """
        words = line.split()
        if re.search("^n", words[1]) and re.search("^x", words[2]) and re.search("^y", words[3]) and re.search("^n", words[4]):
            print "Section Header: 1D histo"
            return 1

    def Read1DHist(self, iline):
        nhist = self.GetNhist(self.lines[iline])
        xarray = []
        xmax = None
        data = []
        errors = []
        for line in self.lines[iline+1:]:
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            if nhist == 1: # a single histogram
                xarray.append(float(words[0]))
                xmax =        float(words[1])
                data.append(  float(words[2]))
                errors.append(float(words[3]))
        xarray.append(xmax)
        nbins = len(xarray)-1
        
        if nhist == 1:
            h = TH1F("h%d" % self.ihist, ";%s;%s" % (self.xtitle, self.ytitle), nbins, array('f', xarray))
            self.ihist += 1
            for i in range(nbins):
                val = data[i]
                err = errors[i] * val
                h.SetBinContent(i+1, val)
                h.SetBinError(i+1, err)
            self.histos.Add(h)

            del xarray[:]
            del data[:]
            del errors[:]

def main():
    """
    angel2root - ANGEL to ROOT converter
    """
    verbose = '-v' in sys.argv
    if verbose:
        sys.argv.remove("-v")

    fname_in = sys.argv[1]
    fname_out = re.sub("\....$", ".root", fname_in)
    if fname_in == fname_out:
        fname_out = fname_in + ".root"
    print fname_out

    angel = Angel(fname_in)

    sys.exit(0)
    


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

        for ihist in range(2):
            print p.xarray[ihist]
            hist = TH1F("h%d" % ihist, "%s (%s);%s;%s" % (title, p.subtitle[ihist], xtitle, ytitle), nbins, array('f', p.xarray[ihist]))
            for i in range(nbins):
                val = p.data[ihist][i]
                print val
                hist.SetBinContent(i+1, val)
                if len(p.errors[ihist]):
                    err = p.errors[ihist][i]*val
                    hist.SetBinError(i+1, err)
            hists.Add(hist)

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
                d = p.data[0][x+(nbinsy-1-y)*nbinsx]
                hist.SetBinContent(x+1, y+1, d)
        hists.Add(hist)
    else:
        print("neither 1D nor 2D axis -> exit")
        return 1

    
    fout = TFile(fname_out, "recreate")
    hists.Write()
    fout.Close()


if __name__ == "__main__":
    sys.exit(main())
