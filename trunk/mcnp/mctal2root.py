#! /usr/bin/python -W all

import sys, re, string
from array import array
from ROOT import ROOT, TFile, TH1F, TObjArray, THnSparseF

class Tally:
    number = None
    title = None
    particle = None
    type = None     # tally type: 0=nondetector, 1=point detector; 2=ring; 3=FIP; 4=FIR; 5=FIC
    cells = None
    f  = None       # number of cell, surface or detector bins
    d  = None       # number of total / direct or flagged bins
# u is the number of user bins, including the total bin if there is one.
#   If there is a total bin, then 'ut' is used.
#   If there is cumulative binning, then 'uc' is used
# The same rules apply for the s, m, c, e, and t - lines
    u  = None
    s  = None       # segment or radiography s-axis bin
    m  = None       # multiplier bin
    c  = None       # cosine or radiography t-axis bin
    e  = None       # energy bin
    t  = None       # time bin

    boundaries = {}
    boundaries['f'] = []
    boundaries['d'] = []
    boundaries['u'] = []
    boundaries['s'] = []
    boundaries['m'] = []
    boundaries['c'] = []
    boundaries['e'] = []
    boundaries['t'] = []

    data = []
    errors = [] # errors are relative

    tfc_n   = None  # number of sets of tally fluctuation data
    tfc_jtf = []    # list of 8 numbers, the bin indexes of tally fluctuation chart bin
    tfc_data = []   # list of 4 numbers for each set of tally fluctuation chart data: nps, tally, error, figure of merit

    
    def __init__(self, number):
        self.number = number
        for b in self.boundaries: del self.boundaries[b][:]
        del self.data[:]
        del self.errors[:]

    def Print(self, option=''):
        print "tally #%d:\t%s" % (self.number, self.title)
        print "nbins", self.getNbins(), len(self.data)
        if option == 'title': return
#        self.Check()
        print "\tparticles:", self.particle
        print "\ttype:", self.type
        print "\tcells:", self.cells
        print "\tdimensions:", self.f, self.d, self.u, self.s, self.m, self.c, self.e, self.t
        print "\tnumber of dimensions:", self.getNdimensions()

        if self.d == 1:                                   # page 262
            print '\tthis is a cell or surface tally unless there is CF or SF card'
        elif self.d == 2:
            print '\tthis is a detector tally (unless thre is an ND card on the F5 tally)'

        for b in self.boundaries:
            if self.boundaries[b]:
                if len(self.boundaries[b])<10:
                    print "\tbins", b, ":", self.boundaries[b]
                else:
                    print "\tbins", b, ":", self.boundaries[b][0], '...', self.boundaries[b][-1]
        
#        print "\tData:", self.data
#        print "\tRelative Errors:", self.errors

#        print 2*(1+len(self.boundaries['e'])) * (1+len(self.boundaries['t'])), len(self.data)

    def getNbinsAxis(self, axis, remove_zeros=True):
        n = 0
        n = len(self.boundaries[axis]) # this takes into account NT (total bin) by removing it - in any case we can get it by TH1::Integral()
        # if   axis == 't': n = self.t[1]
        # elif axis == 'e': n = self.e[1]
        # elif axis == 'c': n = self.c[1]
        # elif axis == 'm': n = self.m[1]
        # elif axis == 's': n = self.s[1]
        # elif axis == 'u': n = self.u[1]
        # elif axis == 'd': n = self.d[1]
        # elif axis == 'f': n = self.f[1]
        # else:
        #     print "Error - no such axis in getNbins", axis
        #     sys.exit(1)

        # this is needed for Histogram():
        if remove_zeros and n == 0:
            n = 1
        return n


    def getNbins(self):
        # Why don't just return len(self.data) ? - because it only works for 1D histos
        nbins = 1 #2  # !!! why 2? written on page 263, but still not clear Guess: value+error pairs?!!!
        for b in self.boundaries:
            l = len(self.boundaries[b])
            if l != 0: 
                nbins = nbins * (l+1)
        return nbins

    def getNdimensions(self):
        """
        Return number of non-empty dimensions of the tally (histogram)
        """
        return len(self.GetStrippedBoundaries())

    def GetStrippedBoundaries(self):
        """
        Return boundaries without entries which have 0 or 1 bins
        """
        return dict( (b, v) for b,v in self.boundaries.iteritems() if len(v)>0 )

    def GetGlobalBinNumber(self, f, d, u, s, m, c, e, t):
        """
        Return global bin number to get value from self.data and self.error
        !!! not yet checked for all dimensions !!!
        checked for: t, et, ut
        """
        bt = len(self.boundaries['t'])+1
        be = len(self.boundaries['e'])+1
        bc = len(self.boundaries['c'])+1
        bm = len(self.boundaries['m'])+1
        bs = len(self.boundaries['s'])+1
        bu = len(self.boundaries['u'])+1
        bd = len(self.boundaries['d'])+1
        bf = len(self.boundaries['f'])+1

        gb  = t
        gb += e*bt
        gb += c*bt*be
        gb += m*bt*be*bc
        gb += s*bt*be*bc*bm
        gb += u*bt*be*bc*bm*bs
        gb += d*bt*be*bc*bm*bs*bu
        gb += f*bt*be*bc*bm*bs*bu*bd

        return gb

    def Check(self):
        """
        Perform a simple check of the tally
        """
        if len(self.tfc_jtf) != 8:
            print 'length of tfc_jtf array is not 8 but', len(self.tfc_jtf)
            sys.exit(1)

        if len(self.tfc_data) != 4:
            print 'length of tfc_data array is not 4 but', len(self.tfc_data)
            sys.exit(1)

        if self.number % 10 != 4:            return 0   # everything below is for tally #4 only:

        if self.e:
            length = len(self.boundaries['e'])
            if self.e-1 != length:
                print "number of enerby bins is wrong: et=%d, len(energy_bins)=%d" % (self.e, length)
                sys.exit(1)

            length = len(self.data)
            if self.e != length:
                print "number of data bins is wrong: et=%d, len(data)=%d" % (self.e, length)
                sys.exit(1)

            length = len(self.errors)
            if self.e != length:
                print "number of error bins is wrong: et=%d, len(errors)=%d" % (self.e, length)
                sys.exit(1)

    def Histogram(self):
        """
        Histograms the current tally
        """
        print "->Histogram"
        stripped_boundaries = self.GetStrippedBoundaries()
#        print self.e[1]
#        print "nbins: ", self.getNbins(), len(self.data)

        bins = []
        for i in stripped_boundaries.keys():
            bins.append(self.getNbinsAxis(i))
        # bins.append(self.f[1])
        # bins.append(self.d[1])
        # bins.append(self.u[1])
        # bins.append(self.s[1])
        # bins.append(self.m[1])
        # bins.append(self.c[1])
        # bins.append(self.e[1])
        # bins.append(self.t[1])
        print "bins: ", bins
# both 3 lines below give the same result:
#        while 0 in bins:  bins.remove(0)
#        bins = [x for x in bins if x]
        bins = filter(lambda item: item>1, bins)

        dim = len(bins)

        """ test """
        print "test"
        print "before: ", self.boundaries
        stripped_boundaries = self.GetStrippedBoundaries()
        print "after: ", stripped_boundaries
        print len(stripped_boundaries)

        print "dim,bins: ", dim,bins
        print "boundaries: ", stripped_boundaries
        hs = THnSparseF("f%d" % self.number, "", dim, array('i', bins));
        hs.Print()
        print hs.GetNdimensions()
        # set bin edges:
        for i,b in enumerate(stripped_boundaries):
            print "here: ", self.getNbinsAxis(b), stripped_boundaries[b]
            edges = [0.0] + stripped_boundaries[b]
            print "setting bin edges for ", i,b,edges
            hs.SetBinEdges(i, array('d', edges)) # !!! max edge is just +1 to the previous edge
            hs.GetAxis(i).SetTitle("%s" % b)
            print stripped_boundaries[b]


#        print "hs bins: ", hs.GetNbins()
#        for bin in range(self.getNbins()):
#            print bin, self.data[bin]
#            hs.SetBinContent(bin+1, 1.0) #self.data[bin])
        print self.data
        print "length: ", len(self.data)

        coords = []
        print "here"
#        print self.boundaries
#        print stripped_boundaries.keys(), bins

        print self.boundaries['t'], self.t

        gbin = 0
        for f in range(self.getNbinsAxis("f")):
            for d in range(self.getNbinsAxis("d")):
                for u in range(self.getNbinsAxis("u")):
                    for s in range(self.getNbinsAxis("s")):
                        for m in range(self.getNbinsAxis("m")):
                            for c in range(self.getNbinsAxis("c")):
                                for e in range(self.getNbinsAxis("e")):
                                    for t in range(self.getNbinsAxis("t")):
#                                        gbin = self.GetGlobalBinNumber(f,d,u,s,m,c,e,t)
#                                        print "gbin ", gbin
                                        val = self.data[gbin]
                                        err = self.errors[gbin]
                                        for thekey in stripped_boundaries.keys():
                                            if   thekey == 't': coords.append(t+1) # t+1 - checked
                                            elif thekey == 'e': coords.append(e+1)
                                            elif thekey == 'c': coords.append(c+1)
                                            elif thekey == 'm': coords.append(m+1)
                                            elif thekey == 's': coords.append(s+1)
                                            elif thekey == 'u': coords.append(u+1)
                                            elif thekey == 'd': coords.append(d+1)
                                            elif thekey == 'f': coords.append(f+1)
                                        print coords, gbin, val,err
                                        hs.SetBinContent(array('i', coords), val)
                                        hs.SetBinError(array('i', coords), err*val)
                                        del coords[:]
                                        gbin += 1

        return hs

#        hs.SetBinEdges(1, array('d', [0.0] + self.boundaries['e'] + [3000.0])) # !!! max energy set to 3000
#        # !!! first bin set to -0.1 since t-bins start from 0
#        hs.SetBinEdges(2, array('d', [-0.1] + self.boundaries['t'] + [sys.float_info.max])) # !!! max time set to MAX_FLOAT
#        print hs.GetAxis(2).GetNbins(), hs.GetAxis(2).GetBinLowEdge(1)




    def Histogram1D(self):
# old version - 1D histogram only
# f5 tallies work only with energy binnings !!!
#        print self.energy_bins
#        for i in range(len(self.energy_bins)):
#            if i>0:
#                if self.energy_bins[i] < self.energy_bins[i-1]:
#                    print i
        print "ndim:",self.getNdimensions()
        title = "" # ";energy [MeV]"
        if self.title: title = self.title + title
        if self.number % 10 == 4:
            nbins = self.getNbins()
#            print nbins, self.e[1]
            h = TH1F("f%d" % self.number, title, nbins-2, array('f', self.boundaries['e']))
            for i in range(nbins-1): # et-1 => skip the last bin with total over all energy value (see p. 139 - E Tally Energy)
                val = self.data[i]
                dx = h.GetBinLowEdge(i+1)-h.GetBinLowEdge(i) 
                val = val/dx # divide by the bin width
                h.SetBinContent(i, val)
                h.SetBinError(i, val*self.errors[i])
        elif self.number % 10 == 5:
            h = TH1F("f%d" % self.number, title, self.e[1], array('f', [0] + self.boundaries['e']))
            for i in range(self.e[1]):
                val = self.data[i] # !!! not normalized by the bin width !!! 
                h.SetBinContent(i+1, val)
                h.SetBinError(i+1, val*self.errors[i])
        elif self.number % 10 == 6: # energy deposit
            print "histogramming"
            nbins = len(self.data)
            print "nbins: ", nbins
            if self.getNbins()-1 == len(self.boundaries['f']): # region binning only
                
#                h = TH1F("f%d" % self.number, title, nbins, array('f', self.boundaries['f']+ [self.boundaries['f'][len(self.boundaries['f'])-1]+1]))
                h = TH1F("f%d" % self.number, title + ";Cell", nbins, 0, nbins)
                print h.GetNbinsX()
                for i in range(nbins):
                    print i+1, h.GetBinCenter(i+1)
                    val = self.data[i] # !!! not normalized by the bin width !!! 
                    h.SetBinContent(i+1, val)
                    h.SetBinError(i+1, val*self.errors[i])
                    h.GetXaxis().SetBinLabel(i+1, "%d" % self.boundaries['f'][i])
            else:
                print "Error from Histogram: this binning not yet supported"
                exit(1)
        return h

def main():
    """
    mctal2root - MCTAL to ROOT converter
    Usage: mctal2root mctal [output.root]
    many features are not yet supported!
    """

    fname_in = sys.argv[1]
    fname_out = re.sub("\....$", ".root", fname_in)
    if fname_in == fname_out:
        fname_out = fname_in + ".root"
    print fname_out

    file_in = open(fname_in)
    
    kod = None               # name of the code, MCNPX
    ver = None               # code version
    probid = []              # date and time when the problem was run
    probid_date = None       # date from probid
    probid_time = None       # time from probid
    knod = None              # the dump number
    nps = None               # number of histories that were run
    rnr = None               # number of pseudorandom numbers that were used
    problem_title = None     # problem identification line
    ntal = None              # total number of tallies
    ntals = []               # array of tally numbers
    tally = None             # current tally

    is_vals = False          # True in the data/errors section

    histos = TObjArray()     # array of histograms

    for line in file_in.readlines():
        if kod is None:
            kod, ver, probid_date, probid_time, knod, nps, rnr = line.split()
            probid.append(probid_date)
            probid.append(probid_time)
#            print kod, ver, probid, knod, nps, rnr
            continue
        else:
            if problem_title is None and line[0] == " ":
                problem_title = line.strip()
                print problem_title
                continue

        words = line.split()

        if not ntal and words[0] == 'ntal':
            ntal = int(words[1])
            continue

        if ntal and not tally and words[0] != 'tally':
            for w in words:
                ntals.append(int(w))
            if ntal>1: print ntal, 'tallies:', ntals
            else: print ntal, 'tally:', ntals

        if words[0] == 'tally':
            if tally: 
                tally.Print()
#                histos.Add(tally.Histogram())
                if tally.number % 10 == 4 or tally.number == 5 or tally.number == 6 or tally.number == 15:
                    histos.Add(tally.Histogram())
#                elif tally.number == 125:
#                    tally.Print()
#                    histos.Add(tally.Histogram())
                del tally
            tally = Tally(int(words[1]))
            tally.particle = int(words[2])
            tally.type = int(words[3])
            if tally.number not in ntals:
                print 'tally %d is not in ntals' % tally.number
                print ntals
                return 1
            continue

        if not tally: continue

        if tally.f and tally.d is None and line[0] == ' ':
            tally.cells = words
            for w in words:
                tally.boundaries['f'].append(float(w))

        if tally.f is None and words[0] not in ['1', 'f']:
            tally.title = line.strip()
            print "tally.title:", tally.title
            

        if tally.t and is_vals == False and len(tally.data) == 0 and line[0] == ' ':
            for w in words:
                tally.boundaries['t'].append(float(w))

        if tally.e and tally.t is None and line[0] == ' ':
#            if len(tally.boundaries['e']) == 0: tally.boundaries['e'].append(0.0)
            for w in words: tally.boundaries['e'].append(float(w))

        if tally.u and tally.s is None and line[0] == ' ':
#            if len(tally.boundaries['u']) == 0: tally.boundaries['u'].append(0.0)
            for w in words: tally.boundaries['u'].append(float(w))

        if   not tally.f and re.search('^f', line[0]):        tally.f = words[0], int(words[1])
        elif not tally.d and re.search('^d', line[0]):        tally.d = words[0], int(words[1])
        elif not tally.u and re.search ("u[tc]?", line[0:1]): tally.u = words[0], int(words[1])
        elif not tally.s and re.search('^s[tc]?', line[0:1]): tally.s = words[0], int(words[1])
        elif not tally.m and re.search('^m[tc]?', line[0:1]): tally.m = words[0], int(words[1])
        elif not tally.c and re.search('^c[tc]?', line[0:1]): tally.c = words[0], int(words[1])
        elif not tally.e and re.search("^e[y]?",  line[0:1]): tally.e = words[0], int(words[1])
        elif not tally.t and re.search("^t[tc]?", line[0:1]): tally.t = words[0], int(words[1])
        elif line[0:2] == 'tfc':
            tally.tfc_n = words[1]
            tally.tfc_jtf = words[2:]

        if tally.tfc_n and line[0] == ' ':
            tally.tfc_data = words

        if words[0] == 'vals':
            is_vals = True
            continue

        if is_vals:
            if line[0] == ' ':
                for iw, w in enumerate(words):
                    if not iw % 2: tally.data.append(float(w))
                    else: tally.errors.append(float(w))
            else:
                is_vals = False

    tally.Print()
    histos.Add(tally.Histogram())

    histos.Print()

    file_in.close()

    fout = TFile(fname_out, 'recreate')
    histos.Write()
    fout.Close()


if __name__ == '__main__':
    sys.exit(main())
