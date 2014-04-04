#! /usr/bin/python -W all
# $Id$
# $URL$

import sys, math, struct
from ssw import fortranRead

def sr2deg(val):
    """Converts steradians to degrees"""
    return math.acos(max([1.0-val/math.pi/2.0, -1.0])) * 180.0/math.pi;


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
        self.ebxlow = 0    # min energy
        self.ebxhgh = 0.0  # max energy
        self.nebxbn = 0    # number of energy intervals
        self.debxbn = 0.0  # energy bin width
        # angular binning
        self.abxlow = 0
        self.abxhgh = 0
        self.nabxbn = 0
        self.dabxbn = 0.0
        
        self.igmusx = 0   # number of low energy neutron groups
        self.engmax = []  # low-energy upper boundaries
        self.gbstor = []  # errors
        self.gdstor = []  # array with flux (Part/GeV/cmq/pr)

        self.epgmax = []  # high-energy upper boundaries
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

    def getALowEdge(self):
        """Return solid angle lower edges vector"""
        vec = []
        val = 0
        for ia in range(self.nabxbn+1):
            if abs(self.itusbx)<=1: # linear in angle
                val = self.abxlow + ia*self.dabxbn
                vec.append(val)
            else: # logarithmic in angle
                if ia==0: # first bin
                    vec.append(0.0) # see note 2 for USRBDX on page 237
                    val = self.abxlow
                    vec.append(val)
                else:
                    if ia!=self.nabxbn:
                        val = self.abxlow*pow(self.dabxbn, ia)
                        vec.append(val)
        return vec

    def getData(self, ie, ia, unit, lowneut=False):
        """
        Return a list of 
        data (above low energy neutrons) in energy bin ie and angular bin ia
        unit == sr:  [Part/sr/GeV/cmq/pr]
        unit == deg: [Part/deg/GeV/cmq/pr]
        and its relative error
        if lowneut = False then return high energy data (default)
        if lowneut = True then return low energy neutron data
        """

        if lowneut:
            y = ie + ia*self.igmusx 
            val = self.gdstor[y]  # !!! FIX THIS !!!
            err = self.gbstor[y]
#            print "ie,ia,y, val,err", ie, ia, y, val, err
            val /= self.engmax[y-1]-self.engmax[y]
        else:
            y = ie + ia*self.nebxbn 
            val = self.gdstor[y]
            err = self.gbstor[y]

        if unit == 'sr':
            return val,err
        elif unit == 'deg':
            vec = self.getALowEdge()
            return val * (vec[ia+1]-vec[ia]) / (sr2deg(vec[ia+1])-sr2deg(vec[ia])), err
        else: raise IOError("unit %s is not supported" % unit)



    def Print(self):
        def PrintV(val, sameline):
            """Prints value"""
            print "%e" % val,
            if not sameline: print "\n\t",
        
        def PrintVE(val, err, sameline):
            """Prints value and error"""
            print "%e +/- %g %%\t" % (val, err),
            if not sameline: print "\n\t",

        print "\nDetector n: %d (%d) %s" % (self.nx, self.nx, self.titusx)
        print "\t(Area: %g cmq," % self.ausbdx
        print "\t distr. scored: %d," % self.idusbx
        print "\t from reg. %d to %d," % (self.nr1usx, self.nr2usx)

        if self.isOneWay(): print "\t one way scoring,"
        else: print "\t this is a two ways estimator"
        
        if self.isFluence(): print "\t fluence scoring scoring)"
        else: print "\t current scoring)"
        
        print ""
        
        print "\tTot. resp. (Part/cmq/pr) %e +/- %e %%" % (self.totresp, 100*self.totresperr)
        print "\t( -->      (Part/pr)     %e +/- %e %% )"  % (self.totresp*self.ausbdx, 100*self.totresperr)

        print ""

        print "\t**** Different. Fluxes as a function of energy ****",
        print "\t****      (integrated over solid angle)        ****"
        print "\t Energy boundaries (GeV):\n"
        print "\t",
        for i in range(self.nebxbn):
            PrintV(self.epgmax[i], (i+1) % 5)
        print "\n\tLowest boundary (GeV):", self.epgmax[self.nebxbn] # if does not work, see UsxSuw::GetLowsetBoundary

        print "\n\tFlux (Part/GeV/cmq/pr):"
        print "\t",
        for i in range(self.nebxbn):
            PrintVE(self.flux[i], 100.0*self.fluxerr[i], (i+1)%2)

        if self.llnusx:
            print "\t Energy boundaries (GeV):\n"
            print "\t",
            for i in range(self.igmusx): PrintV(self.engmax[i], (i+1) % 5)
            print "\n\tLowest boundary (GeV):", self.engmax[i]
            print self.igmusx
#            print "here", len(self.gbstor), len(self.gdstor), self.nabxbn
            print "\n\tFlux (Part/GeV/cmq/pr): (!!! SOMETHING IS WRONG WITH VALUE NORMALISATION HERE (not divided by energy?), BUT ERRORS ARE OK !!!)\n\t",
            for ie in range(self.igmusx):
                for ia in range(self.nabxbn):
                    val = self.getData(ie+1, ia, 'deg', True)
                    PrintVE(val[0], 100*val[1], (ie+1)%2)
                

        print "\n\t**** Cumulative Fluxes as a function of energy ****",
        print "\t****      (integrated over solid angle)        ****"

        print "\n\t Energy boundaries (GeV):"
        print "\t",
        for i in range(self.nebxbn):
            PrintV(self.epgmax[i], (i+1) % 5)
        print "Lowest boundary (GeV):", self.epgmax[self.nebxbn] # if does not work, see

        print "\n\tCumul. Flux (Part/cmq/pr):\n\n\t",
        for i in range(self.nebxbn):
            PrintVE(self.cumulflux[i], 100.0*self.cumulfluxerr[i], (i+1)%2)

        if self.llnusx:
            print "\n\t Energy boundaries (GeV):\n"
            print "\t",
            for i in range(self.igmusx): PrintV(self.engmax[i], (i+1) % 5)
            print "\n\tLowest boundary (GeV):", self.engmax[i]

            print "\n\tCumul. Flux (Part/cmq/pr):here\n\t",

            for i in range(self.igmusx):
                PrintVE(self.cumulflux[i+self.nebxbn], 100*self.cumulfluxerr[i+self.nebxbn], (i+1)%2) # this is OK
        
        if self.nabxbn>1: # if more than one angle required
            print "\n\t**** Double diff. Fluxes as a function of energy ****"
            alowedges = self.getALowEdge()
            print "\tSolid angle minimum value (sr): ", alowedges[0]
            print "\tSolid angle upper boundaries (sr):\n\t",
            for i, val in enumerate(alowedges[1:], 1):
                PrintV(val, i%5)

            alowedgesdeg = map(sr2deg, alowedges)
            print "\n\tAngular minimum value (deg.): ", alowedgesdeg[0]
            print "\tAngular upper boundaries (deg.):\n\t",
            for i,val in enumerate(alowedgesdeg[1:], 1):
                PrintV(val, i%5)

        # high-energy part
            for ie in range(self.nebxbn):
                print "\n\tEnergy interval (GeV): %e %e" % (self.epgmax[ie], self.epgmax[ie+1])
                print "\tFlux (Part/sr/GeV/cmq/pr):\n\t",
                for ia in range(self.nabxbn):
                    val = self.getData(self.nebxbn-ie-1, ia, 'sr')
                    PrintVE(val[0], 100*val[1], (ia+1)%2)
                print "Flux (Part/deg/GeV/cmq/pr):\n\t",
                for ia in range(self.nabxbn):
                    val = self.getData(self.nebxbn-ie-1, ia, 'deg')
                    PrintVE(val[0], 100*val[1], (ia+1)%2)


        # low-energy part
#        for ie in range(self.nebxbn):
            


        # print self.itusbx, self.idusbx, self.nr1usx, self.nr2usx, self.ausbdx, self.lwusbx, self.lfusbx, self.llnusx
        # print "energy binning: ", self.ebxlow, self.ebxhgh, self.nebxbn, self.debxbn
        # print "angular binning: ", self.abxlow, self.abxhgh, self.nabxbn, self.dabxbn
        # print "number of low energy neutron groups: ", self.igmusx#, self.engmax

        # print "total responce: %e +- %g" % (self.totresp, self.totresperr)



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


    def Read(self):
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
            ubs.epgmax = vtmp[3:][:]

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
        for ubs in self.ubsarray:
            ubs.Print()
