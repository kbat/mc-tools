#! /usr/bin/python -W all
# $Id$
# $URL$

import sys, math, struct
from ssw import fortranRead


class USXSUW:
    def __init__(self, fname):
        self.fname = fname
        print self.fname

        self.title  = ""
        self.time   = ""
        self.wctot  = None
        self.nctot  = 0
        self.mctot  = 0
        self.mbatch = 0

        self.file = open(self.fname, "rb")
        data = fortranRead(self.file)
        if data is None: raise IOError("Invalid USXSUW file")

        self.title, self.time, self.wctot, self.nctot, self.mctot, self.mbatch = struct.unpack("=80s32s1f3i", data)


    def reset(self):
# values we read for each record
        self.nx     = 0    # record number
        self.titusx = ""
        self.itusbx = 0    # type of the binning
        self.idusbx = 0    # distribution to be scored
        self.nr1usx = 0    # first region
        self.nr2usx = 0    # second region
        self.ausbdx = 0.0  # area
        self.lwusbx = None # one or two directions
        self.lfusbx = None # current or fluence
        self.llnusx = None # low energy neutrons
        # energy binning
        self.ebxlow = 0
        self.ebxhgh = 0.0
        self.nebxbn = 0
        self.debxbn = 0.0
        # angular binning
        self.abxlow = 0
        self.abxhgh = 0
        self.nabxbn = 0
        self.dabxbn = 0.0
        
        self.igmusx = 0   # number of low energy neutron groups
        self.engmax = []  # array of upper energy bin boudaries
        self.gdstor = []  # array with flux (Part/GeV/cmq/pr)

    def checkStatFlag(self, data):
        """Checks whether data == 'STATISTICS'"""
        s = 'STATISTICS'
        l = len(data)
        if l == 14:
            val = struct.unpack("=10s4s", data)
            if val[0] == s: return True
        else: return False

    def read(self):
        self.reset()
        record = 0
        while True:
            data = fortranRead(self.file)
            if self.checkStatFlag(data): break

            self.nx, self.titusx, self.itusbx, self.idusbx, self.nr1usx, self.nr2usx, self.ausbdx, self.lwusbx, self.lfusbx, self.llnusx, self.ebxlow, self.ebxhgh, self.nebxbn, self.debxbn, self.abxlow, self.abxhgh, self.nabxbn, self.dabxbn  = struct.unpack("=1i10s4i1f3i2f1i1f2f1i1f", data)
        # in FORTRAN a bool is written as an integer, so we cast types here:
            self.lwusbx, self.lfusbx, self.llnusx = map(bool, (self.lwusbx, self.lfusbx, self.llnusx))

            if (self.llnusx): # if low energy neutrons
                data = fortranRead(self.file)
                l = (len(data)-4)/4
                tmp = struct.unpack("=i%df" % l, data)
                self.igmusx = tmp[0] # number of groups
                self.engmax = tmp[1:]
            else:
                self.igmusx = 0

            data = fortranRead(self.file)
            self.gdstor = struct.unpack("=%df" % self.getNbinsTotal(), data)
            record += 1
        print record, "records found"

        print ""
        self.file.close()


    def Print(self):
        print self.title
        print self.time
        print self.wctot, self.nctot, self.mctot, self.mbatch
        print self.nx, self.titusx, self.itusbx, self.idusbx, self.nr1usx, self.nr2usx, self.ausbdx, self.lwusbx, self.lfusbx, self.llnusx
        print "energy binning: ", self.ebxlow, self.ebxhgh, self.nebxbn, self.debxbn
        print "angular binning: ", self.abxlow, self.abxhgh, self.nabxbn, self.dabxbn
        print "number of low energy neutron groups: ", self.igmusx#, self.engmax
        

    def getNbinsTotal(self):
        return (self.nebxbn + self.igmusx) * self.nabxbn
