#! /usr/bin/python -W all

import sys, re, string
from array import array
from ROOT import ROOT, TFile, TH1F, TObjArray

class Tally:
    number = None
    title = None
    particle = None
    cells = None
    f  = None       # number of cell, surface or detector bins
    d  = None       # total / direct or flagged bin
    u  = None       # user bin
    s  = None       # segment or radiography s-axis bin
    m  = None       # multiplier bin
    c  = None       # cosine or radiography t-axis bin
    e  = None       # energy bin
    t  = None       # time bin

    energy_bins = [] # et-1 size array

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
        del self.energy_bins[:]
        for b in self.boundaries: del self.boundaries[b][:]
        del self.data[:]
        del self.errors[:]

    def Print(self, option=''):
        print "tally #%d:\t%s" % (self.number, self.title)
        print "nbins", self.getNbins(), len(self.data)
        if option == 'title': return
        self.Check()
        print "\tparticles:", self.particle
        print "\tcells:", self.cells
        print "\tdimentions:", self.f, self.d, self.u, self.s, self.m, self.c, self.e, self.t
        if self.e:
            print "\tenergy bins:", self.energy_bins[0], '...', self.energy_bins[-1]
        for b in self.boundaries:
            if self.boundaries[b]:
                print "\tbins", b, ":", self.boundaries[b][0], '...', self.boundaries[b][-1]

#        print 2*(1+len(self.boundaries['e'])) * (1+len(self.boundaries['t'])), len(self.data)

    def getNbins(self):
        nbins = 2  # !!! why 2? written on page 263, but still not clear !!!
        for b in self.boundaries:
            l = len(self.boundaries[b])
            if l != 0: 
                nbins = nbins * (l+1)
        return nbins

    def Check(self):
        if len(self.tfc_jtf) != 8:
            print 'length of tfc_jtf array is not 8 but', len(self.tfc_jtf)
            sys.exit(1)

        if len(self.tfc_data) != 4:
            print 'length of tfc_data array is not 4 but', len(self.tfc_data)
            sys.exit(1)

        if self.number % 10 != 4:            return 0   # everything below is for tally #4 only:

        if self.e:
            length = len(self.energy_bins)
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
#        print self.energy_bins
#        for i in range(len(self.energy_bins)):
#            if i>0:
#                if self.energy_bins[i] < self.energy_bins[i-1]:
#                    print i
        title = ""
        if self.title: title = self.title
        if self.number % 10 == 4:
            h = TH1F("f%d" % self.number, title, self.e-2, array('f', self.energy_bins))
            for i in range(self.e-1): # et-1 => skip the last bin with total over all energy value (see p. 139 - E Tally Energy)
                val = self.data[i]
                dx = h.GetBinLowEdge(i+1)-h.GetBinLowEdge(i) 
                val = val/dx # divide by the bin width
                h.SetBinContent(i, val)
                h.SetBinError(i, val*self.errors[i])
        elif self.number % 10 == 5:
            h = TH1F("f%d" % self.number, title, self.e, array('f', [0] + self.energy_bins))
            for i in range(self.e):
                val = self.data[i] # !!! not normalized by the bin width !!! 
                h.SetBinContent(i+1, val)
                h.SetBinError(i+1, val*self.errors[i])
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
    
    kod = None
    ver = None
    probid_date = None
    probid_time = None
    probid = []
    knod = None
    nps = None
    rnr = None
    problem_title = None # problem identification line
    ntal = None # total number of tallies
    ntals = [] # array of tally numbers
    tally = None # current tally

    is_vals = False # True in the data/errors section

    histos = TObjArray()

    for line in file_in.readlines():
        if kod is None:
            kod, ver, probid_date, probid_time, knod, nps, rnr = line.split()
            probid.append(probid_date)
            probid.append(probid_time)
            print kod, ver, probid, knod, nps, rnr

            continue
        else:
            if problem_title is None:
                problem_title = line.strip()
                print problem_title
                continue

        words = line.split()

        if not ntal and words[0] == 'ntal':
            ntal = words[1]
            continue

        if ntal and not tally and words[0] != 'tally':
            for w in words:
                ntals.append(int(w))
            print ntal, 'tallies:', ntals

        if words[0] == 'tally':
            if tally: 
                tally.Print('title')
                if tally.number % 10 == 4 or tally.number == 5 or tally.number == 15:
                    histos.Add(tally.Histogram())
                elif tally.number == 125:
                    tally.Print()
#                    histos.Add(tally.Histogram())
                del tally
            tally = Tally(int(words[1]))
            tally.particle = words[2:]
            if tally.number not in ntals:
                print 'tally %d is not in ntals' % tally.number
                print ntals
                return 1
            continue

        if not tally: continue

        if tally.f and tally.d is None and line[0] == ' ':
            tally.cells = words

        if tally.f is None and words[0] not in ['1', 'f']:
            tally.title = line.strip()


        if tally.t and is_vals == False and len(tally.data) == 0 and line[0] == ' ':
            for w in words:
                tally.boundaries['t'].append(float(w))

        if tally.e and tally.t is None and line[0] == ' ':
            for w in words:
                tally.energy_bins.append(float(w))
                tally.boundaries['e'].append(float(w))

        if   words[0] == 'f':  tally.f  = int(words[1])
        elif words[0] == 'd':  tally.d  = int(words[1])
        elif words[0] == 'u' or words[0] == 'ut':  tally.u  = int(words[1])
        elif words[0] == 's':  tally.s  = int(words[1])
        elif words[0] == 'm':  tally.m  = int(words[1])
        elif words[0] == 'c':  tally.c  = int(words[1])
        elif words[0] == 'et' or words[0] == 'e': tally.e = int(words[1])
        elif words[0] == 't' or words[0] == 'tt':  tally.t  = int(words[1])
        elif words[0] == 'tfc':
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

    #tally.Print()

    histos.Print()

    file_in.close()

    fout = TFile(fname_out, 'recreate')
    histos.Write()
    fout.Close()


if __name__ == '__main__':
    sys.exit(main())
