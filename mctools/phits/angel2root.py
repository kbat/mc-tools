#!/usr/bin/env python3
#
#  A script to convert ANGEL (PHITS) output into the ROOT format
#  Author: Konstantin Batkov
#  Contact: batkov@gmail.com
#  https://github.com/kbat/mc-tools
#
#  Usage: angel2root.py file.dat
#

import sys, re, argparse, os
from array import array
from mctools.phits.phits import TallyOutputParser
import ROOT
# The line below is needed to prevent command-line arguments from
# stolen by PyROOT and handed to TApplication
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TH1F, TH2F, TFile, TObjArray, TGraphErrors

"""
def isData(line):
    words = line.strip()
#    print(words)
    for w in words:
        try:
            float(w)
        except ValueError:
            return False
    return True
"""

#        SUBT = re.compile('prot*')
SUBT = re.compile(r"""
\(
(?P<subtitle>.*)\s*?
\)
""", re.VERBOSE)

#: a regular expression which describes the page-separating line.
pageSepRE = re.compile(r"^[\s#]newpage:$")

#: a regular expression to search for continuation lines of "reg = "
regMeshRE = re.compile(r"^ *([,0-9{}<\(\)\[\]\-\+]|all|u *=).*")

#: a regular expression to separate the values in multiplier subsection
#  ex.1      mat                   mset1
#            all ( 1.79077E-13 2002 1 -4 )
#         => ['( 1.79077E-13 2002 1 -4 )']
#  ex.2      mat         mset1           mset2           mset3
#            all ( 1.0000 -250 ) ( 1.0000 -200 ) ( 1.0000 -201 )
#         => ['( 1.0000 -250 )','( 1.0000 -200 )','( 1.0000 -201 )]
mulDataRE = re.compile(r"(\(.*?\))+") # match non-greedily

DEBUG = 0 # accept integral value. (> 1 to print the data)

def is_float(s):
    """
    Return True if s is float. Otherwise return False
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def splitHline(inLine):
    """split an "h:" line into words w/ "(...)" taking into account
    """
    line = inLine.strip() # remove leading/trailing whitespaces
    if DEBUG: print("splitHline: stripped line = '{}'".format(line),len(line))
    staPos = [0] # start position of a word (the first should be 0)
    endPos = []
    inWord  = True  # True if in a word
    inParen = False # True if between '(' and ')'
    for idx in range(1,len(line)):
        if line[idx] == '(': inParen = True
        elif line[idx] == ')': inParen = False
        elif line[idx] == ' ' and line[idx-1] != ' ' and not inParen:
            endPos.append(idx)
        elif line[idx] != ' ' and line[idx-1] == ' ' and not inParen:
            staPos.append(idx)
    endPos.append(len(line))
    if DEBUG > 1:
        print("splitHline: staPos: ", staPos,len(staPos))
        print("splitHline: endPos: ", endPos,len(endPos))
    words = []
    for idx in range(len(staPos)):
        words.append(line[staPos[idx]:endPos[idx]])
    if DEBUG > 1: print("splitHline: words = :", words)
    return words


class Angel:
    fname = None
    title  = None
    subtitles = []
    xtitle = None
    ytitle = None
    ztitle = None
    mesh = None
    axis = [] # there might be several axes -> list
    reg = []
    output = None
    output_title = None # commented part of output line - for z-title
    unit = None
    unit_title = None # commented part of the unit line - for z-title
    file = None # file name as defined in the PHITS tally
    part = [] # list of particles
    lines = []
    return_value = 0
    numPlotPages = 0 # number of plot pages <- later deduced from len(pageLST)

# this group of variables is used to convert a set of 1D histograms to 2D (if necessary):
    dict_nbins = {} # dictionary of number of bins - to guess if 2D histo is needed
    last_nbins_read = None # last name of binning read (ne, nt, na, ...)
    dict_edges_array = {} # dictionary of arrays with bin edges

    ihist = 0 # histogram number - must start from ZERO
    def __init__(self, fname_in, fname_out, **kwargs):
#        global DEBUG
        #: a python list which contains the numbers of lines which separate
        #: pages
        pageSepLineLST = []
        #: a list of tuples; each tuple contains the contents of a page.
        pageLST = []
        #: the number of ``newpage:``.
        numNewpages = 0

        self.fname = fname_in
        file = open(self.fname)
        self.lines = tuple(file.readlines())
        file.close()

        # create the output anyway; remove if nothing to save
        fout = TFile(fname_out, "recreate")
        self.histos = TObjArray() # the owner is the output file
        self.avBitSet = kwargs["avBitSet"]
        self.sangel = False # existence of additional angel instruction w/ "sangel = "

        ipage = -1

        ##################################################
        # scan whole the file and count the "^[\s#]newpage:$",
        ##################################################
        for idx,line in enumerate(self.lines):
            modLine = line.rstrip() # strip spaces/newlines at the right
            if pageSepRE.search(modLine):
                numNewpages += 1
                pageSepLineLST.append(idx)
        if DEBUG: print("pageSepLineLST: ", pageSepLineLST)

        ##################################################
        # Separate each page into a tuple and
        # store them into a list named 'pageLST'
        ##################################################
        #   the 1st page
        pageLST.append( tuple( self.lines[:pageSepLineLST[0]] ) )
        #   intermediate
        for pageIdx in range(1,numNewpages):
            pageLST.append(
                self.lines[ pageSepLineLST[pageIdx-1]+1 :
                            pageSepLineLST[pageIdx] ] )
        #   the last page
        pageLST.append( tuple( self.lines[pageSepLineLST[-1]+1:] ) )

        #   the number of plot pages
        self.numPlotPages = len(pageLST) - 1 # one header page
        if DEBUG: print("numPlotPages: ", self.numPlotPages)

        ##################################################
        # scan the first page and extract header information
        ##################################################
        if DEBUG > 1:
            # print each tuple element
            print("Header Page as a tuple of strings: \n", pageLST[0])
            print("Strings(stripped):")
            for elNo in range(len(pageLST[0])):
                print("\t",elNo,pageLST[0][elNo].strip())
        if DEBUG: print("========== Start processing the header page ==========")
        iline = 0
        while iline < len(pageLST[0]):
            line = pageLST[0][iline].strip()
            # print("{}: line = \'{}\'".format(iline,line))
            if re.search("title = ", line):
                words = line.split()
                self.title = ' '.join(words[2:])
                if DEBUG: print("title: ", self.title)
                iline += 1
            elif re.search("mesh = ", line):
                words = line.split()
                self.mesh = words[2]
                if DEBUG: print("mesh: ", self.mesh)
                if self.mesh == "reg" or self.mesh == "tet":
                    # process line(s) for region/tetra mesh
                    # The next line should be "reg = ".
                    # Extract the string between '=' and '#'.
                    regStr = re.split(r"[=#]", pageLST[0][iline+1].strip())[1]
                    if DEBUG: print("regStr(1st): ", regStr)
                    # The region line(s) may continue...
                    iline += 2 # start from the next of "reg = "
                    while True:
                        if regMeshRE.match(pageLST[0][iline]):
                            regStr += pageLST[0][iline].strip()
                            iline += 1
                            if DEBUG: print("\tiline => ",iline)
                        else:
                            break
                    if DEBUG: print("regStr(fin): ", regStr)
                else: iline += 1
            elif re.search("axis = ", line):
                for a in line.split()[2:]:
                    if a == '#': break
                    self.axis.append(a)
                if DEBUG: print("axis: ", self.axis)
                iline += 1
            elif re.search("^n[eartxyzl] = ", line.strip()): # !!! make sence if we specify number of bins but not the bin width
                words = line.split()
                self.dict_nbins[words[0]] = int(words[2])
                self.last_nbins_read = words[0]
                if DEBUG: print("dict_nbins:", self.dict_nbins)
                iline += 1
            elif re.search("#    data = ", line):
                self.dict_edges_array[self.last_nbins_read] = self.GetBinEdges(iline)
                iline += 1
            elif re.search("part = ", line):
                words = line.split()
                # The "part = " line immediately below the "multiplier = all"
                # solely belongs and applys to the multiplier subsection.
                self.part = words[2:]
                if DEBUG: print("particles:", self.part)
                iline += 1
            elif re.search("output = ", line):
                words = line.split()
                self.output = words[2]
                self.output_title = ' '.join(words[4:])
                if self.unit_title != None: self.ztitle = self.output_title + " " + self.unit_title
                iline += 1
            elif re.search("unit = ", line):
                words = line.split()
                self.unit = words[2]
                self.unit_title = ' '.join(words[6:])
                if self.output_title != None: self.ztitle = self.output_title + " " + self.unit_title
                iline += 1
            elif re.search("file = ", line):
                words = line.split()
                self.file, ext = os.path.splitext(words[2])
                iline += 1
            elif re.search("multiplier = ", line):
                self.mult_part = pageLST[0][iline+1].strip().split()[2]
                self.mult_emax = pageLST[0][iline+3].strip().split()[2]
                self.mult_mat  = pageLST[0][iline+4].strip().split()[1:]
                self.mult_mul = mulDataRE.findall(pageLST[0][iline+5].strip()) # non-greedy
                if DEBUG:
                    print("self.mult_part: ", self.mult_part)
                    print("self.mult_emax: ", self.mult_emax)
                    print("self.mult_mat : ", self.mult_mat)
                    print("self.mult_mul:  ", self.mult_mul)
                iline += 5
            elif re.search("sangel =", line):
                self.sangel = True
                if DEBUG: print("sangel = True: '{}'".format(pageLST[0][iline].strip()))
                iline += 1
            else:
                iline += 1 # just advance one line
        if DEBUG: print("========== Finish processing the header page ==========")

        ##################################################
        # scan the remaining data pages one by one
        # book and fill histograms
        ##################################################
        for npage in range(1, len(pageLST)):
            if DEBUG: print("========== Page {} ==========".format(npage))
            # first scan: extract header info in advance to the data extraction
            if DEBUG: print("---------- 1st scan ----------")
            hLST = [] # list of 'H-tuples', (Line#OfH,"typeOfH"). ("typeOfH" is redundant)
            for iline, line in enumerate(pageLST[npage]):
                line.strip()
                if re.search("^x:", line):
                    words = line.split()
                    self.xtitle = ' '.join(words[1:])
                    if DEBUG: print("xtitle:", self.xtitle)
                    continue
                elif re.search("^y:", line):
                    words = line.split()
                    self.ytitle = ' '.join(words[1:])
                    if DEBUG: print("ytitle:", self.ytitle)
                    continue
                elif re.search("^z:", line):
                    if not re.search("xorg", line):
                        print(line)
                        print("new graph - not yet implemented")
                    continue
                elif re.search("'no. =", line): # subtitles of 2D histogram
                    self.subtitles.append(' '.join(line[line.find(',')+1:].split()).replace("\'", '').strip())
                    if DEBUG: print("subtitle:", self.subtitles)
                elif re.search("^h", line):
                    if DEBUG: print("h-line found: '{}'".format(line))
                    hLST.append( (iline,line.split()[0]) ) # H-tuple
            if DEBUG: print("hLST: ", hLST)

            # second scan: extract data.
            #              scan only within the current page, pass the corresponding
            #              global line number for data decoding
            if DEBUG: print("---------- 2nd scan ----------")
            for iline, line in enumerate(pageLST[npage]):
                # skip to the last histogram in this page
                if self.sangel and iline < hLST[-1][0]: continue
                line.strip()
                #: 'global' line number (not in the current page).
                #: The counting of local line number (iline) start just after
                #: the location of "^[\s#]newpage:$" and therefore '+1'
                igline = iline + pageSepLineLST[npage-1] + 1
                if re.search("^h", line):
                    if re.search("^h: [nx]", line): # !!! We are looking for 'h: n' instead of 'h' due to rz-plots.
                        if DEBUG: print("one dimentional graph section")
                        self.Read1DHist(igline, npage)
                        continue
                    elif re.search("h:              x", line):
                        if DEBUG: print("calling Read1DGraphErrors()")
                        self.Read1DGraphErrors(igline, npage)
                        continue
                    elif re.search("h:   x      n     n", line) and \
                    re.search("#    num    tetra   volume",
                              pageLST[npage][iline+1].strip()): # tetra mesh
                        if DEBUG: print("calling Read1DGraphErrors() for tetra mesh")
                        self.Read1DGraphErrors(igline, npage, tet=True)
                        continue
                    elif re.search("^h([2d]|c2?):", line):
                        if DEBUG:
                            if re.search("^h2", line): print("h2: two dimentional contour plot section")
                            if re.search("^hd", line): print("hd: two dimentional cluster plot section")
                            if re.search("^hc", line): print("hc: two dimentional colour cluster plot section")
                        self.Read2DHist(igline)
                        break # no need to scan further, only to find color palette etc.
                    elif 'reg' in self.axis: # line starts with 'h' and axis is 'reg' => 1D histo in region mesh. For instance, this is whe case with [t-deposit] tally and mesh = reg.
                        if DEBUG: print("calling Read1DHist() (region mesh)")
                        self.Read1DHist(igline, npage)
                        continue

#        print(self.dict_edges_array)
        if self.is1D():
            if DEBUG: print("1D")
        else:
            if DEBUG: print("2D")
#            self.Make2Dfrom1D()


        if DEBUG: print("self.histos.GetEntries(): ", self.histos.GetEntries())
        if self.histos.GetEntries():
            self.histos.Write()
            fout.Close()
            self.return_value = 0
        else:
            print("Have not found any histograms/graphs in this file")
            self.return_value = 1
            fout.Close()
            os.remove(fname_out) # Nothing to write, remove the output file

    def is1D(self):
        """
        Trying to guess if we have many 1D histograms which actually form a 2D one.
        """
        nn1 = 0 # number of cases when number of bins is not 1
        for key in self.dict_nbins:
            if int(self.dict_nbins[key])>1: nn1 += 1
        if DEBUG: print("nn1:", nn1)

        if nn1 <= 1:
            return True
        else:
            return False

    # def GetBinEdgesOrig(self, iline):
    #     print("iline:", iline)
    #     edges = []
    #     for line in self.lines[iline+1:]:
    #         print("line: ", line)
    #         if line[0] == '#':
    #             words =  line[1:].split()
    #             print(words)
    #             for w in words:
    #                 edges.append(w)
    #         else: break
    #     if len(edges)-1 != self.dict_nbins[self.last_nbins_read]:
    #         print("ERROR in GetBinEdges: wrong edge or bin number:", len(edges)-1, self.dict_nbins[self.last_nbins_read])
    #         sys.exit(1)
    #    # print('edges:', edges)
    #     return tuple(edges)


    def GetBinEdges(self, iline):
        edges = []
        for line in self.lines[iline+1:]:
            words =  line.split()
            if line[0] == '#': # if the distribution type is 1 or 2 then '#' is used
                if DEBUG > 1: print(words[1:])
                for w in words[1:]:
                    edges.append(w)
            elif is_float(words[0]):
                for w in words: # if the distribution type is 3 then there is no "#"
                    edges.append(w)
            else: break
        if len(edges)-1 != self.dict_nbins[self.last_nbins_read]:
            print("ERROR in GetBinEdges: wrong edge or bin number:", len(edges)-1, self.dict_nbins[self.last_nbins_read])
            sys.exit(1)
       # print('edges:', edges)
        return tuple(edges)

    def GetNhist(self, line):
        """
        Analyzes the section header and return the number of histograms in the section data
        (but not in the entire file!)
        """
# Let's remove all spaces between ')'. For some reason line.replace('\s*)', ')') does not work
# so we do it in this weird way:
        if DEBUG: print("GetNhist(): line = \'{}\'".format(line))
        line1 = None
        while line1 != line:
            line1 = line
            line = line.replace(' )', ')')

        words = splitHline(line)
        if DEBUG:
            print("GetNhist(): line = \'{}\'".format(line))
            if DEBUG > 1: print("GetNhist(): words = ", words)
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
        if DEBUG: print("Section Header: 1D histo", nhists, self.subtitles)
        return nhists

    def Read1DHist(self, iline, pageNum):
        """
        Read 1D histogram section
        """
        nhist = self.GetNhist(self.lines[iline]) # number of histograms to read in the current section
        if DEBUG: print('nhist: ', nhist)
        isCharge = False
        if re.search("x-0.5", self.lines[iline].split()[1]):
            isCharge = True # the charge-mass-chart distribution, x-axis is defined by the 1st column only
            if DEBUG: print("isCharge = True")
        xarray = []
        xmax = None
        data = {}     # dictionary for all histograms in the current section
        errors = {}   # dictionary for all histograms in the current section
        bin_labels = [] # relevant for self.axis == 'reg' only

        for ihist in range(nhist):  # create the empty lists, so we could append later
            data[ihist] = []
            errors[ihist] = []

        for line in self.lines[iline+1:]:
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            if DEBUG > 1: print("Read1DHist(): words = ",words)
            if isCharge:
                if DEBUG: print("Read1DHist(): isCharge")
                xarray.append(float(words[0])-0.5)
                xmax = float(words[0])+0.5
                data[0].append(float(words[1]))
                errors[0].append(float(words[2]))
            elif 'reg' in self.axis:
                if DEBUG: print("Read1DHist(): reg")
                xarray.append(   float(words[0])-0.5)
                xmax =           float(words[0])+0.5
                bin_labels.append(words[1]) # region number
                for ihist in range(nhist):
                    data[ihist].append(  float(words[(ihist+1)*2+1])    )
                    errors[ihist].append(float(words[(ihist+1)*2+2])    )
            else:
                if DEBUG > 1: print("Read1DHist(): else")
                xarray.append(float(words[0]))
                xmax =        float(words[1])
                for ihist in range(nhist):
                    data[ihist].append(  float(words[(ihist+1)*2  ]))
                    errors[ihist].append(float(words[(ihist+1)*2+1]))

        nbins = len(xarray)
        xarray.append(xmax)

        if DEBUG:
            print("Read1DHist(): len(xarray) = ", len(xarray))
            print("Read1DHist(): nhist = ", nhist)
            print("Read1DHist(): len(data) = ", len(data))
            print("Read1DHist(): len(errors) = ", len(errors))
            for idx in range(nhist):
                print("Read1DHist(): len(data[{}]) = {}".format(idx, len(data[idx])))
                print("Read1DHist(): len(errors[{}]) = {}".format(idx, len(errors[idx])))
            print("Read1DHist(): self.numPlotPages = ", self.numPlotPages)
            if DEBUG > 1:
                print("Read1DHist(): xarray= ", xarray)
                for idx in range(nhist):
                    print("Read1DHist(): data[{}]= {}".format(idx, data[idx]))
                    print("Read1DHist(): errors[{}] = {}".format(idx, errors[idx]))

        for ihist in range(nhist):
            if self.subtitles[ihist]: subtitle = ' - ' + self.subtitles[ihist+1]
            else: subtitle = ''
            if DEBUG: print("Read1DHist(): subtitle = '{}'".format(subtitle))
            self.FixTitles()
            # self.ihist+1 - start from ONE as in Angel - easy to compare
            if self.numPlotPages == 1:
                if nhist == 1:
                    hname = "%s" % (self.file)
                else:
                    hname = "%s_%s" % (self.file, self.subtitles[ihist+1])
            else:
                if nhist == 1:
                    hname = "%s_%d" % (self.file, pageNum)
                else:
                    hname = "%s_%d_%s" % (self.file, pageNum, self.subtitles[ihist+1])
            if DEBUG: print("Read1DHist(): hname = '{}'".format(hname))
            h = TH1F(hname, "%s%s;%s;%s" % (self.title, subtitle, self.xtitle, self.ytitle), nbins, array('f', xarray))
            if self.avBitSet:
                h.SetBit(TH1F.kIsAverage)
            self.ihist += 1
            for i in range(nbins):
                val = data[ihist][i]
                err = errors[ihist][i] * val
                h.SetBinContent(i+1, val)
                h.SetBinError(i+1, err)

            if 'reg' in self.axis:
                for i in range(nbins):
                    h.GetXaxis().SetBinLabel(i+1, bin_labels[i])
                h.GetXaxis().SetTitle("Region number")

            self.histos.Add(h)
        del self.subtitles[:]

    def Read1DGraphErrors(self, iline, pageNum, tet=False):
        """
        Read 1D graph section
        """
        ngraphs = self.GetNhist(self.lines[iline]) # graph and hist format is the same
        if DEBUG: print("ngraphs: ", ngraphs)
        xarray = []
        data = {}
        errors = {}
        tetShift = 2 if tet else 0 # column shift for tetra mesh

        for igraph in range(ngraphs):
            data[igraph] = []
            errors[igraph] = []

        for line in self.lines[iline+1:]:
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            if DEBUG > 2: print("Read1DGraphErrors(): words = ",words)
            xarray.append(float(words[0]))
            for igraph in range(ngraphs):
                data[igraph].append(  float(words[(igraph+1)*2-1+tetShift]))
                errors[igraph].append(float(words[(igraph+1)*2  +tetShift]))

        npoints = len(xarray)

        if DEBUG:
            print("Read1DGraphErrors(): len(xarray) = ", len(xarray))
            print("Read1DGraphErrors(): ngraphs = ", ngraphs)
            print("Read1DGraphErrors(): len(data) = ", len(data))
            print("Read1DGraphErrors(): len(errors) = ", len(errors))
            for idx in range(ngraphs):
                print("Read1DGraphErrors(): len(data[{}]) = {}".format(idx, len(data[idx])))
                print("Read1DGraphErrors(): len(errors[{}]) = {}".format(idx, len(errors[idx])))
            print("Read1DGraphErrors(): self.numPlotPages = ", self.numPlotPages)
            if DEBUG > 1:
                print("Read1DGraphErrors(): xarray = ", xarray)
                for idx in range(ngraphs):
                    print("Read1DGraphErrors(): data[{}]= {}".format(idx, data[idx]))
                    print("Read1DGraphErrors(): errors[{}] = {}".format(idx, errors[idx]))

        for igraph in range(ngraphs):
            if self.subtitles[igraph]: subtitle = ' - ' + self.subtitles[igraph+1]
            else: subtitle = ''
            if DEBUG: print("Read1DGraphErrors(): subtitle = '{}'".format(subtitle))
            self.FixTitles()
            g = TGraphErrors(npoints)
            ### Releasing the ownership
            ROOT.SetOwnership(g, False) # old style.
            # cppyy-based newer PyROOT.
            # g.SetOwnership(False)
            # -> AttributeError: 'TGraphErrors' object has no attribute 'SetOwnership'
            # self.ihist+1 - start from ONE as in Angel - easy to compare
            if self.numPlotPages == 1:
                if ngraphs == 1:
                    gname = self.file
                else:
                    gname = "%s_%s" % (self.file, self.subtitles[igraph+1])
            else:
                if ngraphs == 1:
                    gname = "%s_%d" % (self.file, pageNum)
                else:
                    gname = "%s_%d_%s" % (self.file, pageNum, self.subtitles[igraph+1])
            if DEBUG: print("Read1DGraphErrors(): gname = ", gname)
            g.SetNameTitle(gname, "%s%s;%s;%s" % (self.title, subtitle, self.xtitle, self.ytitle))
            self.ihist += 1
            if DEBUG: print("Read1DGraphErrors(): name = '{}', title = '{}{};{};{}'".format(
                gname, self.title, subtitle, self.xtitle, self.ytitle))
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

        if DEBUG: print("Read2DHist(): invoked with iline = ", iline)
        line = self.lines[iline].replace(" =", "=") # sometimes Angel writes 'y=' and sometimes 'y ='
        words = line.split()
        if DEBUG: print("Read2DHist(): words = ", words)
        if len(words) != 15:
            print(words)
            print(len(words))
            sys.exit("Read2DHist: format error")
#        print(words)

        dy = float(words[6])
        ymin = float(words[2])
        ymax = float(words[4])
        if dy>0:
            if ymin<ymax:
                ymin,ymax = ymin-dy/2.0,ymax+dy/2.0
            else:
                ymin,ymax = ymax-dy/2.0, ymin+dy/2.0
        elif dy<0:
            if ymin<ymax:
                sys.exit("Fix me: ymin<ymax when dy<0")
#                ymin,ymax = ymin-dy/2.0,ymax+dy/2.0
            else:
                ymin,ymax = ymax+dy/2.0, ymin-dy/2.0
        ny = abs(int(round((ymax-ymin)/dy)))
        if DEBUG: print("Read2DHsit(): y: (ymin,ymax,dy,ny) = ({},{},{},{})".format(ymin,ymax,dy,ny))

        dx = float(words[13])
        xmin = float(words[9])
        xmax = float(words[11])
        if xmin<xmax:
            xmin,xmax = xmin-dx/2.0,xmax+dx/2.0
        else:
            xmin,xmax = xmax-dx/2.0, xmin+dx/2.0
        nx = int(round((xmax-xmin)/dx))
        if DEBUG: print("Read2DHist(): x: (xmin,xmax,dx,nx) = ({},{},{},{})".format(xmin,xmax,dx,nx))

        data = []
        for line in self.lines[iline+1:]:
            line = line.strip()
            if DEBUG > 1: print("Read2DHist(): line = '{}'".format(line))
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            if DEBUG > 1: print("Read2DHist(): words = ", words)
            for w in words:
                if w == 'z:':
                    if DEBUG: print("Read2DHist(): this is a color palette -> exit")
                    return # this was a color palette
                data.append(float(w))
        if DEBUG > 1: print("Read2DHist(): data = ", data)

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
                print("not the same bin number", i)
                return false
            for bin in range(nbins0):
                if self.histos[0].GetBinLowEdge(i+1) != self.histos[i].GetBinLowEdge(i+1):
                    print("Low edge differ for bin %d of histo %d" % (bin, i))
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
            print("ERROR in Make2Dfrom1D: x-axes are different")
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
            if DEBUG: print("the second dimention is", second_dimention, second_dimention_nbins)
        else:
            if DEBUG: print("Second dimention was not found based on the number of bins -> bin edges comparing needed")
            sys.exit(3)

#        h2 = TH2F("hall%s" % second_dimention, "", nbins0, 0, 1, 20, 0, 1)

#        if DEBUG: print(array('f', self.getXarray(self.histos[0])))
        second_dimention_xarray = []
        for w in self.dict_edges_array[second_dimention]: second_dimention_xarray.append(float(w))
#        for w in self.dict_edges_array[second_dimention]: if DEBUG: print(float(w))
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
    parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: https://github.com/kbat/mc-tools")

    parser.add_argument("-a", "--average", action="store_true",
                        help="set the TH1.kIsAverage bit for averaging")
    parser.add_argument("infilename", action="store", nargs=1, type=str,
                        help="input ANGEL filename")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="verbose output (not yet implemented)")
    args = parser.parse_args()

    fname_in = args.infilename[0]
    fname_out = re.sub(r"\....$", ".root", fname_in)
    if fname_in == fname_out:
        fname_out = fname_in + ".root"
    print(fname_in, "->" ,fname_out)

    angel =  Angel(fname_in, fname_out,avBitSet=args.average)

    return angel.return_value

if __name__ == "__main__":
    sys.exit(main())
