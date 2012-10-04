#! /usr/bin/python -W all
#
# $URL$
# $Id$
#

import sys, re, string
from array import array

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
    type = None     # tally type: 0=nondetector, 1=point detector; 2=ring; 3=FIP; 4=FIR; 5=FIC
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
        types = ['nondetector', 'point detector', 'ring', 'FIP', 'FIR', 'FIC']
        print "tally #%d:\t%s" % (self.number, self.title)
        if option == 'title': return
#        self.Check()
        print "\tparticles:", self.particle
        print "\ttype: %s (%s)" % (self.type, types[self.type])

        if self.d == 1:                                   # page 262
            print '\tthis is a cell or surface tally unless there is CF or SF card'
        elif self.d == 2:
            print '\tthis is a detector tally (unless thre is an ND card on the F5 tally)'

        print "\taxes:"
        for b in self.axes.keys():
            self.axes[b].Print()


    def getName(self):
        """
        Return the name of the tally
        """
        return "f%s" % self.number
    

class Axis:
    """Axis of a tally"""
    def __init__(self, name, number):
        """Axis Constructor"""
        self.name = name
        self.number = int(number) # number of cell or surfae bins
        self.arraycsn = [] # array of cell or surface numbers
        print "Axis %s added" % self.name

    def Print(self):
        """Axis printer"""
        print "\t Axis %s" % self.name


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


