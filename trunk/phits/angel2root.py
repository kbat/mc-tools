#! /usr/bin/python -W all
#
# A script to convert ANGEL (PHITS) output to the ROOT format
#  Author: Konstantin Batkov
# Contact: kbat.phits ((at)) lizardie.com
#
# Usage: angel2root.py file.out [file.root]
#

import sys, re, string
from array import array
from phits import TallyOutputParser
from ROOT import ROOT, TH1F, TH2F, TFile, TObjArray, TGraphErrors

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

#        SUBT = re.compile('prot*')
SUBT = re.compile("""
\(
(?P<subtitle>.*)\s*?
\)
""", re.VERBOSE)

DEBUG = True # False

def is_float(s):
    """
    Return True if s is float. Otherwise return False
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


class Angel:
    fname = None
    title  = None
    subtitles = []
    xtitle = None
    ytitle = None
    ztitle = None
    mesh = None
    axis = None
    output = None
    output_title = None # commented part of output line - for z-title
    unit = None
    unit_title = None # commented part of the unit line - for z-title
    part = [] # list of particles
    lines = []
    return_value = 0

# this group of variables is used to convert a set of 1D histograms to 2D (if necessary):
    dict_nbins = {} # dictionary of number of bins - to guess if 2D histo is needed
    last_nbins_read = None # last name of binning read (ne, nt, na, ...)
    dict_edges_array = {} # dictionary of arrays with bin edges

    histos = TObjArray()
    ihist = 0 # histogram number - must start from ZERO
    fname_out = None
    def __init__(self, fname_in, fname_out):
#        global DEBUG
        self.fname = fname_in
        file = open(self.fname)
        self.lines = tuple(file.readlines())
        file.close()

        self.fname_out = fname_out

        ipage = -1

        for iline, line in enumerate(self.lines, 0):
            line.strip()
            if re.search("title = ", line):
                words = line.split()
                self.title = string.join(words[2:])
                continue
            if re.search("mesh = ", line):
                words = line.split()
                self.mesh = words[2]
                continue
            if re.search("axis = ", line):
                self.axis = line.split()[2]
                if DEBUG: print "axis: ", self.axis
                continue
            if re.search("^n[eartxyz] = ", line.strip()): # !!! make sence if we specify number of bins but not the bin's width
                words = line.split()
                self.dict_nbins[words[0]] = int(words[2])
                self.last_nbins_read = words[0]
                if DEBUG: print "dict_nbins:", self.dict_nbins
                continue
            if re.search("#    data = ", line):
                self.dict_edges_array[self.last_nbins_read] = self.GetBinEdges(iline)
                continue
            if re.search("part = ", line):
                words = line.split()
# this loop is needed in case we define particles in separate lines as shown on page 121 of the Manual. Otherwise we could have used 'self.part = words[2:]'
                for w in words[2:]: self.part.append(w)
                if DEBUG: print "particles:", self.part
                continue
            if re.search("output = ", line):
                words = line.split()
                self.output = words[2]
                self.output_title = string.join(words[4:])
                if self.unit_title != None: self.ztitle = self.output_title + " " + self.unit_title
                continue
            if re.search("unit = ", line):
                words = line.split()
                self.unit = words[2]
                self.unit_title = string.join(words[6:])
                if self.output_title != None: self.ztitle = self.output_title + " " + self.unit_title
                continue
            if re.search("newpage:", line):
                ipage += 1
#                if DEBUG: print "page: ", ipage
                continue
            elif re.search("^x:", line):
                words = line.split()
                self.xtitle = string.join(words[1:])
                if DEBUG: print "xtitle:", self.xtitle
                continue
            elif re.search("^y:", line):
                words = line.split()
                self.ytitle = string.join(words[1:])
                if DEBUG: print "ytitle:", self.ytitle
                continue
            elif re.search("^z:", line):
                print "new graph - not yet implemented"
                continue
            elif re.search("^h:", line):
                if re.search("^h: n", line): # !!! We are looking for 'h: n' instead of 'h' due to rz-plots.
                    if DEBUG: print "one dimentional graph section"
                    self.Read1DHist(iline)
                    continue
                elif re.search("h:              x", line):
                    self.Read1DGraphErrors(iline)
                    continue
                elif re.search("^h[2dc]:", line):
                    if DEBUG:
                        if re.search("^h2", line): print "h2: two dimentional contour plot section"
                        if re.search("^hd", line): print "hd: two dimentional cluster plot section"
                        if re.search("^hc", line): print "hc: two dimentional colour cluster plot section"
                    self.Read2DHist(iline)
                    continue
                elif self.axis == "reg": # line starts with 'h' and axis is 'reg' => 1D histo in region mesh. For instance, this is whe case with [t-deposit] tally and mesh = reg.
                    self.Read1DHist(iline)
                    continue
            elif re.search("'no. = ", line): # subtitles of 2D histogram
                self.subtitles.append(string.join(line.split()[3:]).replace("\'", '').strip())

#        print self.dict_edges_array
        if self.is1D():
            if DEBUG: print "1D"
        else:
            if DEBUG: print "2D"
#            self.Make2Dfrom1D()


        if self.histos.GetEntries():
            fout = TFile(self.fname_out, "recreate")
            self.histos.Write()
            fout.Close()
            self.return_value = 0
        else:
            print "Have not found any histograms/graphs in this file"
            self.return_value = 1

    def is1D(self):
        """
        Trying to guess if we have many 1D histograms which actually form a 2D one.
        """
        nn1 = 0 # number of cases when number of bins is not 1
        for key in self.dict_nbins:
            if int(self.dict_nbins[key])>1: nn1 += 1
        if DEBUG: print "nn1:", nn1
        
        if nn1 <= 1:
            return True
        else:
            return False

    # def GetBinEdgesOrig(self, iline):
    #     print "iline:", iline
    #     edges = []
    #     for line in self.lines[iline+1:]:
    #         print "line: ", line
    #         if line[0] == '#':
    #             words =  line[1:].split()
    #             print words
    #             for w in words:
    #                 edges.append(w)
    #         else: break
    #     if len(edges)-1 != self.dict_nbins[self.last_nbins_read]:
    #         print "ERROR in GetBinEdges: wrong edge or bin number:", len(edges)-1, self.dict_nbins[self.last_nbins_read]
    #         sys.exit(1)
    #    # print 'edges:', edges
    #     return tuple(edges)


    def GetBinEdges(self, iline):
        edges = []
        for line in self.lines[iline+1:]:
            words =  line.split()
            if line[0] == '#': # if the distribution type is 1 or 2 then '#' is used
                if DEBUG: print words[1:]
                for w in words[1:]:
                    edges.append(w)
            elif is_float(words[0]):
                for w in words: # if the distribution type is 3 then there is no "#"
                    edges.append(w)
            else: break
        if len(edges)-1 != self.dict_nbins[self.last_nbins_read]:
            print "ERROR in GetBinEdges: wrong edge or bin number:", len(edges)-1, self.dict_nbins[self.last_nbins_read]
            sys.exit(1)
       # print 'edges:', edges
        return tuple(edges)

    def GetNhist(self, line):
        """
        Analyzes the section header and return the number of histograms in the section data
        (but not in the entire file!)
        """
# Let's remove all spaces between ')'. For some reason line.replace('\s*)', ')') does not work
# so we do it in this weird way:
        line1 = None
        while line1 != line:
            line1 = line
            line = line.replace(' )', ')')

        words = line.split()
        nhists = 0
        for w in words:
            if re.search("^y", w):
                nhists += 1
                mo = SUBT.search(w)
                if mo:
                    self.subtitles.append(mo.group('subtitle'))
                else:
                    self.subtitles.append('')
###        if re.search("^n", words[1]) and re.search("^x", words[2]) and re.search("^y", words[3]) and re.search("^n", words[4]):
#        if DEBUG: print "Section Header: 1D histo", nhists, self.subtitles
        return nhists

    def Read1DHist(self, iline):
        """
        Read 1D histogram section
        """
        nhist = self.GetNhist(self.lines[iline]) # number of histograms to read in the current section
#        if DEBUG: print 'nhist: ', nhist
        isCharge = False
        if re.search("x-0.5", self.lines[iline].split()[1]):
            isCharge = True # the charge-mass-chart distribution, x-axis is defined by the 1st column only
        xarray = []
        xmax = None
        data = {}     # dictionary for all histograms in the current section
        errors = {}   # dictionary for all histograms in the current section

        for ihist in range(nhist):  # create the empty lists, so we could append later
            data[ihist] = []     
            errors[ihist] = []

        for line in self.lines[iline+1:]:
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            if isCharge:
                xarray.append(float(words[0])-0.5)
                xmax = float(words[0])+0.5
                data[0].append(float(words[1]))
                errors[0].append(float(words[2]))
            elif self.axis == 'reg':
                xarray.append(   float(words[0])-0.5)
                xmax =           float(words[0])+0.5
                data[0].append(  float(words[3])    )
                errors[0].append(float(words[4])    )
            else:
                xarray.append(float(words[0]))
                xmax =        float(words[1])
                for ihist in range(nhist):
                    data[ihist].append(  float(words[(ihist+1)*2  ]))
                    errors[ihist].append(float(words[(ihist+1)*2+1]))

        nbins = len(xarray)
        xarray.append(xmax)

        for ihist in range(nhist):
            if self.subtitles[ihist]: subtitle = ' - ' + self.subtitles[ihist]
            else: subtitle = ''
            self.FixTitles()
            h = TH1F("h%d" % self.ihist, "%s%s;%s;%s" % (self.title, subtitle, self.xtitle, self.ytitle), nbins, array('f', xarray))
            h.SetBit(TH1F.kIsAverage)
            self.ihist += 1
            for i in range(nbins):
                val = data[ihist][i]
                err = errors[ihist][i] * val
                h.SetBinContent(i+1, val)
                h.SetBinError(i+1, err)
        
            self.histos.Add(h)
        del self.subtitles[:]

    def Read1DGraphErrors(self, iline):
        """
        Read 1D graph section
        """
        ngraphs = self.GetNhist(self.lines[iline]) # graph and hist format is the same
        xarray = []
        data = {}
        errors = {}

        for igraph in range(ngraphs):
            data[igraph] = []
            errors[igraph] = []

        for line in self.lines[iline+1:]:
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            xarray.append(float(words[0]))
            for igraph in range(ngraphs):
                data[igraph].append(  float(words[(igraph+1)*2-1  ]))
                errors[igraph].append(float(words[(igraph+1)*2    ]))

        npoints = len(xarray)

        for igraph in range(ngraphs):
            if self.subtitles[igraph]: subtitle = ' - ' + self.subtitles[igraph]
            else: subtitle = ''
            self.FixTitles()
            g = TGraphErrors(npoints)
            g.SetNameTitle("g%d" % self.ihist, "%s%s;%s;%s" % (self.title, subtitle, self.xtitle, self.ytitle))
            self.ihist += 1
            for i in range(npoints):
                x = xarray[i]
                y = data[igraph][i]
                ey = errors[igraph][i]
                g.SetPoint(i, x, y)
                g.SetPointError(i, 0, ey*y)
            
            self.histos.Add(g)
        del self.subtitles[:]


    def FixTitles(self):
        """
        Makes some ROOT fixes

        """
        self.ytitle = self.ytitle.replace("cm^2", "cm^{2}")
        self.ytitle = self.ytitle.replace("cm^3", "cm^{3}")
        self.title = self.title.replace("cm^2", "cm^{2}")
        self.title = self.title.replace("cm^3", "cm^{3}")

    def Read2DHist(self, iline):
        """
        Read 2D histogram section
        """
        line = self.lines[iline].replace(" =", "=") # sometimes Angel writes 'y=' and sometimes 'y ='
        words = line.split()
        if len(words) != 15:
            print words
            print len(words)
            print "Read2DHist: format error"
            exit(1)
#        print words

        dy = float(words[6])
        ymin = float(words[2])
        ymax = float(words[4])
        if ymin<ymax:
            ymin,ymax = ymin-dy/2.0,ymax+dy/2.0
        else:
            ymin,ymax = ymax-dy/2.0, ymin+dy/2.0
        ny = int((ymax-ymin)/dy)
        if DEBUG: print "y:", dy, ymin, ymax, ny

        dx = float(words[13])
        xmin = float(words[9])
        xmax = float(words[11])
        if xmin<xmax:
            xmin,xmax = xmin-dx/2.0,xmax+dx/2.0
        else:
            xmin,xmax = xmax-dx/2.0, xmin+dx/2.0
        nx = int((xmax-xmin)/dx)

        data = []
        for line in self.lines[iline+1:]:
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
#            if DEBUG: print "words: ", words
            for w in words:
                if w == 'z:':
#                    if DEBUG: print "this is a color palette -> exit"
                    return # this was a color palette
                data.append(float(w))
#        if DEBUG: print data
       
        # self.ihist+1 - start from ONE as in Angel - easy to compare
        h = TH2F("h%d" % (self.ihist+1), "%s - %s;%s;%s;%s" % (self.title, self.subtitles[self.ihist], self.xtitle, self.ytitle, self.ztitle), nx, xmin, xmax, ny, ymin, ymax)
        self.ihist += 1

        for y in range(ny-1, -1, -1):
            for x in range(nx):
                d = data[x+(ny-1-y)*nx]
                h.SetBinContent(x+1, y+1, d)
        self.histos.Add(h)

    def isSameXaxis(self):
        """
        Return True if all the histograms in self.histos have the same x-axis
        """
        nhist = self.histos.GetEntries()
        nbins0 = self.histos[0].GetNbinsX()
        for i in range(1,nhist):
            h = self.histos[i]
            if nbins0 != self.histos[i].GetNbinsX():
                print "not the same bin number", i
                return false
            for bin in range(nbins0):
                if self.histos[0].GetBinLowEdge(i+1) != self.histos[i].GetBinLowEdge(i+1):
                    print "Low edge differ for bin %d of histo %d" % (bin, i)
                    return False
        return True

    def getXarray(self, h):
        """
        Return the tuple with x-low-edges of TH1 'h'
        """
        nbins = h.GetNbinsX()
        xarray = []
        for i in range(nbins+1):
            xarray.append(float(h.GetBinLowEdge(i+1)))

        return xarray
    
    def Make2Dfrom1D(self):
        """
        Makes a 2D histogram from a set of 1D !!! works only with 1 set of particles requested !!!
        """
        # check if all histograms have the same x-range:
        if not self.isSameXaxis():
            print "ERROR in Make2Dfrom1D: x-axes are different"
            sys.exit(1)

        # guess which dict_edges_array correspond to 1D histos
        nbins0 = self.histos[0].GetNbinsX()
        second_dimention = None
        second_dimention_nbins = None
        for key in self.dict_edges_array:
            nbins = len(self.dict_edges_array[key])-1
            if nbins==1: continue # we do not care
            if nbins0 != nbins:
                second_dimention = key
                second_dimention_nbins = nbins
        
        if second_dimention:
            if DEBUG: print "the second dimention is", second_dimention, second_dimention_nbins
        else:
            if DEBUG: print "Second dimention was not found based on the number of bins -> bin edges comparing needed"
            sys.exit(3)

#        h2 = TH2F("hall%s" % second_dimention, "", nbins0, 0, 1, 20, 0, 1)
        
#        if DEBUG: print array('f', self.getXarray(self.histos[0]))
        second_dimention_xarray = []
        for w in self.dict_edges_array[second_dimention]: second_dimention_xarray.append(float(w))
#        for w in self.dict_edges_array[second_dimention]: if DEBUG: print float(w)
#        array('f', second_dimention_xarray)

        h2 = TH2F("hall%s" % second_dimention, "%s;%s;%s;%s" % (self.histos[0].GetYaxis().GetTitle(), self.histos[0].GetXaxis().GetTitle(), "Time [nsec]", self.histos[0].GetYaxis().GetTitle()),
                  nbins0, array('f', self.getXarray(self.histos[0])),
                  second_dimention_nbins, array('f', second_dimention_xarray))

        nhist = self.histos.GetEntries() # number of 1D histograms
        for biny in range(nhist):
            h1 = self.histos[biny]
            for binx in range(nbins0):
                h2.SetBinContent(binx+1, biny+1, h1.GetBinContent(binx+1))
                h2.SetBinError(binx+1, biny+1, h1.GetBinError(binx+1))
            

        self.histos.Add(h2)

        

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
    print fname_in, "->" ,fname_out

    angel =  Angel(fname_in, fname_out)
    
    return angel.return_value

if __name__ == "__main__":
    sys.exit(main())
