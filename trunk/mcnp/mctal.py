#! /usr/bin/python -W all
#
# $URL$
# $Id$
#
# Page numbers refer to MCNPX 2.7.0 manual

import sys, re, string
from array import array
from mcnp import GetParticleNames

class Header:
    """mctal header container"""
    def __init__(self):
        """Header initialisation"""
        self.kod = 0            # name of the code, MCNPX
        self.ver = 0            # code version
        self.probid = []        # date and time when the problem was run
        self.knod = 0           # the dump number
        self.nps = 0            # number of histories that were run
        self.rnr = 0            # number of pseudorandom numbers that were used
        self.title = None       # problem identification line
        self.ntal = 0           # number of tallies
        self.ntals = []         # array of tally numbers
        self.npert = 0          # number of perturbations

    def Print(self):
        """Prints the class members"""
        print ("code:\t\t%s" % self.kod)
        print ("version:\t%s" % self.ver)
        print ("date and time:\t%s" % self.probid)
        print ("dump number:\t%s" % self.knod)
        print ("number of histories:\t%s" % self.nps)
        print ("number of pseudorandom numbers used:\t%s" % self.rnr)
        print ("title: %s" % self.title)

        if self.ntal>1: print self.ntal, 'tallies:', self.ntals
        else: print self.ntal, 'tally:', self.ntals

        if self.npert != 0: print("number of perturbations: %s" % self.npert)

class Tally:
    number = None
    title = ""
    particle = None
    type = None     # tally type: 0=nondetector, 1=point detector; 2=ring; 3=pinhole radiograph; 4=transmitted image radiograph (rectangular grid); 5=transmitted image radiograph (cylindrical grid) - see page 320 of MCNPX 2.7.0 Manual
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
    binlabels = []

    axes = {}

    data = []
    errors = [] # errors are relative

    tfc_n   = None  # number of sets of tally fluctuation data
    tfc_jtf = []    # list of 8 numbers, the bin indexes of tally fluctuation chart bin
    tfc_data = []   # list of 4 numbers for each set of tally fluctuation chart data: nps, tally, error, figure of merit
    
    def __init__(self, number):
        self.axes['f'] = None
        self.axes['d'] = None
        self.axes['u'] = None
        self.axes['s'] = None
        self.axes['m'] = None
        self.axes['c'] = None
        self.axes['e'] = None
        self.axes['t'] = None

        self.number = number
        del self.data[:]
        del self.errors[:]

    def Print(self, option=''):
        """Tally printer"""
        print "\nprinting tally:"
        types = ['nondetector', 'point detector', 'ring', 'FIP', 'FIR', 'FIC']
        print "tally #%d:\t%s" % (self.number, self.title)
        if option == 'title': return
#        self.Check()
        print "\tparticles:", GetParticleNames(self.particle)
        print "\ttype: %s (%s)" % (self.type, types[self.type])

        if self.d == 1:
            print '\tthis is a cell or surface tally unless there is CF or SF card'
        elif self.d == 2:
            print '\tthis is a detector tally (unless thre is an ND card on the F5 tally)'

        print "\taxes:"
        for b in self.axes.keys():
            self.axes[b].Print()

        print "\tdata:"
        print self.data
        print "\terrors:"
        print self.errors


    def getName(self):
        """
        Return the name of the tally
        """
        return "f%s" % self.number
    

class Axis:
    """Axis of a tally"""
    def __init__(self, name, numbers):
        """Axis Constructor"""
        self.name = name
        self.numbers = numbers # we keep all array numbers, but not the first one only (in the case of mesh tally there are > than 1 number)
        self.number = int(self.numbers[0]) # see page 320
        self.arraycsn = [] # array of cell or surface numbers (written for non-detector tallies only)
        
        # ni, nj and nk make sense for mesh tallies only (see e.g. tally 4 in figs/cold-neutron-map/2/case001/small-stat/mctal)
        # these are number of bins in i,j,k directions
        self.ni = None
        self.nj = None
        self.nk = None
        if len(self.numbers)>1:
            self.ni, self.nj, self.nk = self.numbers[2:]


        print "Axis %s added" % self.name


    def Print(self):
        """Axis printer"""
        print "\t Axis %s" % self.name
        if len(self.numbers)>1:
            print "\t\tni,nj,nk: ", self.ni, self.nj, self.nk
            
        print "\t\tcsn %s" % self.arraycsn


class MCTAL:
    """mctal container"""
    good_tallies = [5] # list of 'good' tally types

    def __init__(self, fname):
        """Constructor"""
        self.fname = fname # mctal file name
        self.tallies = []  # list of tallies


    def read(self):
        """method to parse the mctal file"""
        verbose = True          # verbosity switch
        probid_date = None       # date from probid
        probid_time = None       # time from probid
        tally = None             # current tally
        is_vals = False          # True in the data/errors section
        is_bin_labels = False    # True in the line after the "^tally" line
        
        h = Header()

        # to be continued - see readmctal.py
