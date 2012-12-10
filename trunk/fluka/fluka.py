#! /usr/bin/python -W all
# $Id$
# $URL$

import sys, math, struct
from ssw import fortranRead

class USRBDXCARD:
    """USXSUW record - corresponds to one USRBDX card"""
    def __init__(self):
        self.reset()

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
        self.gbstor = []  # ???
        self.gdstor = []  # array with flux (Part/GeV/cmq/pr)

        self.epgmax = []

        self.flux   = []  # why different from gdstor???
        self.fluxerr= []  # 
        self.cumulflux = [] # cumulative flux
        self.cumulfluxerr = [] # cumulative flux

        self.totresp = 0  # total responce
        self.totresperr = 0  # total responce error

    def isOneWay(self):
        return not self.lwusbx

    def isFluence(self):
        return self.lfusbx

    def getNbinsTotal(self):
        return (self.nebxbn + self.igmusx) * self.nabxbn

    def getNEbinsTotal(self):
        return self.nebxbn + self.igmusx

    def Print(self):
        print "\nDetector n: %d (%d) %s" % (self.nx, self.nx, self.titusx)
        print "\t(Area: %g cmq," % self.ausbdx
        print "\t distr. scored: %d," % self.idusbx
        print "\t from reg. %d to %d," % (self.nr1usx, self.nr2usx)

        if self.isOneWay(): print "\t one way scoring,"
        else: print "\t this is a two ways estimator"
        
        if self.isFluence(): print "\t fluence scoring scoring)"
        else: print "\t current scoring)"
        
        print ""
        
        print "\tTot. resp. (Part/cmq/pr) %g +/- %g %%" % (self.totresp, 100*self.totresperr)
        print "\t( -->      (Part/pr)     %g +/- %g %% )"  % (self.totresp*self.ausbdx, 100*self.totresperr)

        print ""

        print "\t**** Different. Fluxes as a function of energy ****"
        print "\t****      (integrated over solid angle)        ****"
        print "\t Energy boundaries (GeV):"
        print "\t"
        print self.nebxbn, len(self.epgmax)
#        for i in range(self.nebxbn):
#            print self.epgmax[i]

        print self.itusbx, self.idusbx, self.nr1usx, self.nr2usx, self.ausbdx, self.lwusbx, self.lfusbx, self.llnusx
        print "energy binning: ", self.ebxlow, self.ebxhgh, self.nebxbn, self.debxbn
        print "angular binning: ", self.abxlow, self.abxhgh, self.nabxbn, self.dabxbn
        print "number of low energy neutron groups: ", self.igmusx#, self.engmax

        print "total responce: %g +- %g" % (self.totresp, self.totresperr)



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

        self.ubsarray = []   # array ob USRBDXCARD objects
        self.nrecords = 0    # number of USRBDX cards

        self.file = open(self.fname, "rb")
        data = fortranRead(self.file)
        if data is None: raise IOError("Invalid USXSUW file")

        self.title, self.time, self.wctot, self.nctot, self.mctot, self.mbatch = struct.unpack("=80s32s1f3i", data)

    def reset(self):
        """Reset method"""
        

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
            ubs = USRBDXCARD()
            data = fortranRead(self.file)
            if self.checkStatFlag(data): break

            ubs.nx, ubs.titusx, ubs.itusbx, ubs.idusbx, ubs.nr1usx, ubs.nr2usx, ubs.ausbdx, ubs.lwusbx, ubs.lfusbx, ubs.llnusx, ubs.ebxlow, ubs.ebxhgh, ubs.nebxbn, ubs.debxbn, ubs.abxlow, ubs.abxhgh, ubs.nabxbn, ubs.dabxbn  = struct.unpack("=1i10s4i1f3i2f1i1f2f1i1f", data)
        # in FORTRAN a bool is written as an integer, so we cast types here:
            ubs.lwusbx, ubs.lfusbx, ubs.llnusx = map(bool, (ubs.lwusbx, ubs.lfusbx, ubs.llnusx))

            if (ubs.llnusx): # if low energy neutrons
                data = fortranRead(self.file)
                l = (len(data)-4)/4
                vtmp = struct.unpack("=i%df" % l, data)
                ubs.igmusx = vtmp[0] # number of groups
                ubs.engmax = vtmp[1:]
            else:
                ubs.igmusx = 0

            data = fortranRead(self.file)
            ubs.gdstor = struct.unpack("=%df" % ubs.getNbinsTotal(), data)
            record += 1
            ubs.Print()
            self.ubsarray.append(ubs)
        self.nrecords = record
        print self.nrecords, "USRBDX cards found"

        for record in range(self.nrecords):
            data = fortranRead(self.file)
            ubs = self.ubsarray[record]
            ubs.totresp, ubs.totresperr = struct.unpack("=2f", data)
#            print ubs.igmusx
            data = fortranRead(self.file)
#            print "here:", len(data)/4,  ubs.nebxbn+ubs.igmusx, ubs.getNbinsTotal()
            vtmp = struct.unpack("=2i2f%df" % ubs.getNEbinsTotal(), data)
            print "check:"
            if vtmp[0] != ubs.nebxbn: raise IOError("nebxbn record is wrong")
            if vtmp[1] != ubs.igmusx: raise IOError("igmusx record is wrong")
            print "emin, emax:", vtmp[2], vtmp[3] # !!! maybe not only these 2 records are written when more than 1 user interval ???
            self.epgmax = vtmp[4:]

            data = fortranRead(self.file)
            ubs.flux = struct.unpack("=%df" % ubs.getNEbinsTotal(), data)
#            print ubs.flux[1:10]
#            print ubs.gdstor[1:10]

            data = fortranRead(self.file)
            ubs.fluxerr = struct.unpack("=%df" % ubs.getNEbinsTotal(), data)

            data = fortranRead(self.file)
            ubs.cumulflux = struct.unpack("=%df" % ubs.getNEbinsTotal(), data)

            data = fortranRead(self.file)
            ubs.cumulfluxerr = struct.unpack("=%df" % ubs.getNEbinsTotal(), data)

            if ubs.nabxbn:
                data = fortranRead(self.file)
                ubs.gbstor = struct.unpack("=%df" % ubs.getNbinsTotal(), data)
                


        print ""
        #data = fortranRead(self.file)
        #print len(data)

        self.file.close()


    def Print(self):
        print self.title
        print self.time
        print self.wctot, self.nctot, self.mctot, self.mbatch
