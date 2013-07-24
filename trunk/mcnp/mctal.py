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
        print ("\033[1m[HEADER]\033[0m")
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


    tfc_n   = None  # number of sets of tally fluctuation data
    
    def __init__(self, number):
        self.axes = {}
        self.axes['f'] = None
        self.axes['d'] = None
        self.axes['u'] = None
        self.axes['s'] = None
        self.axes['m'] = None
        self.axes['c'] = None
        self.axes['e'] = None
        self.axes['t'] = None

        self.number = number
        self.data = []
        self.errors = [] # errors are relative
        self.tfc_jtf = []    # list of 8 numbers, the bin indexes of tally fluctuation chart bin
        self.tfc_data = []   # list of 4 numbers for each set of tally fluctuation chart data: nps, tally, error, figure of merit

    def Print(self, option=[]):
        """Tally printer.
           Options: title, 
        """
        print "\n\033[1mprinting tally:\033[0m"
        types = ['nondetector', 'point detector', 'ring', 'FIP', 'FIR', 'FIC']
        print "tally #%d:\t%s" % (self.number, self.title)
#        if 'title' in option: return
#        self.Check()
        if self.particle>0:
            print "\tparticles:", GetParticleNames(self.particle)
        print "\ttype: %s (%s)" % (self.type, types[self.type])

        if self.d == 1:
            print '\tthis is a cell or surface tally unless there is CF or SF card'
        elif self.d == 2:
            print '\tthis is a detector tally (unless thre is an ND card on the F5 tally)'

        if 'axes' in option:
            print "\taxes:"
            for b in self.axes.keys():
                self.axes[b].Print()

        if 'data' in option:
            print "\tdata:"
            print self.data
            print len(self.data)
            print "\terrors:"
            print self.errors
            print len(self.errors)


    def getName(self):
        """
        Return the name of the tally
        """
        return "f%s" % self.number
    

class Axis:
    """Axis of a tally"""
    binlabels = []
    boundaries = []
#    numbers = []

    def __init__(self, name, numbers):
        """Axis Constructor"""
        self.name = name
        self.numbers = numbers # we keep all array numbers, but not the first one only (in the case of mesh tally there are > than 1 number)
        if isinstance(numbers, int):
            self.number = int(self.numbers)
        else:       
            self.number = int(self.numbers[0]) # see page 320
       # print name, numbers, self.number
        self.arraycsn = [] # array of cell or surface numbers (written for non-detector tallies only)
        
        # ni, nj and nk make sense for mesh tallies only (see e.g. tally 4 in figs/cold-neutron-map/2/case001/small-stat/mctal)
        # these are number of bins in i,j,k directions
        self.ni = None
        self.nj = None
        self.nk = None
        if not isinstance(self.numbers, int) and len(self.numbers)>2: # if it's an array (as in case of mesh tally)
            self.ni, self.nj, self.nk = self.numbers[2:]


#        print "Axis %s added" % self.name


    def Print(self):
        """Axis printer"""
        print "\t Axis %s" % self.name, self.numbers
        if not isinstance(self.numbers, int):
            print "\t\tni,nj,nk: ", self.ni, self.nj, self.nk
            
        print "\t\tcell/surface: %s" % self.arraycsn
        print "Number of bins:", len(self.arraycsn)

    def getBins(self, i):
        """Return array of bins in the directon of 'i' (can be i, j, or k)
Meaningful only for non-detector tallies  if len(self.numbers)>1"""
        if len(self.arraycsn) == 0 or len(self.numbers)<=1:
            print "Axis::getBins has no sense in this context"
            return []
        start, end = 0, 0
        if i=='i':
            start = 0
            end = self.ni+1
        elif i=='j':
            start = self.ni+1
            end = start+self.nj+1
        elif i=='k':
            start = self.ni+1 + self.nj+1
            end = start + self.nk+1

        return self.arraycsn[start:end]


class MCTAL:
    """mctal container"""
    good_tallies = [1, 2, 5, 4] # list of 'good' tally types (only implemented types are listed here, but a user can narrow this list even more)
    verbose = True          # verbosity switch

    def __init__(self, fname):
        """Constructor"""
        self.fname = fname # mctal file name
        self.tallies = []  # list of tallies


    def GetTally(self, n):
        """Return tally number 'n'"""
        for t in self.tallies:
            if t.number==n:
                return t
        print "Can't find tally number %d" % n
        return 0


    def Read(self):
        """method to parse the mctal file"""
        probid_date = None       # date from probid
        probid_time = None       # time from probid
        tally = None             # current tally
        is_vals = False          # True in the data/errors section
        is_bin_labels = False    # True in the line after the "^tally" line
        
        h = Header()

        is_list_of_particles = False # True if the line with the list of particles follows the ^tally line           

        file_in = open(self.fname)
    

        for line in file_in.readlines():
            if h.kod == 0:
                h.kod, h.ver, probid_date, probid_time, h.knod, h.nps, h.rnr = line.split()                                                                   
                h.probid.append(probid_date)
                h.probid.append(probid_time)
                continue
            else:
                if h.title is None and line[0] == " ":
                    h.title = line.strip()
                    continue

            words = line.split()
            if not h.ntal and words[0] == 'ntal':
                h.ntal = int(words[1])
                if len(words) == 4 and words[2] == 'npert':
                    h.npert = int(words[3])
                continue

            if h.ntal and not tally and words[0] != 'tally': # list of tally numbers follows
                for w in words:  h.ntals.append(int(w))
                if self.verbose: h.Print()

            if words[0] == 'tally':
                if self.verbose: print("")
                if tally:                                                  
                    if tally.number and tally.number % 10 in self.good_tallies:
                        self.tallies.append(tally)
                    del tally

                tally = Tally(number=int(words[1]))
                tally.particle = int(words[2])
                if tally.particle < 0: # then tally.particle is number of particle types and the next line lists them                                         
                    is_list_of_particles = True
                tally.type = int(words[3])                                                                                                                    
                if self.verbose:
                    print "\033[1mtally number %d particle %d of type %d\033[0m" % (tally.number, tally.particle, tally.type)
                    if tally.number not in h.ntals:
                        print 'tally %d is not in ntals' % tally.number
                        print 'ntals:', h.ntals
                        return 1

    #            is_bin_labels = True

                continue                                                                        

            if is_list_of_particles:
                tally.particle = map(int, words)
                is_list_of_particles = False
                if self.verbose: print "list of particles: ", GetParticleNames(tally.particle)
                continue
            
            if not tally: continue

            if tally.axes['f'] and tally.axes['d'] is None and line[0] == ' ': # reading under the f-tally (non-detector only)
                for w in words:
                    tally.axes['f'].arraycsn.append(str(w))
                continue

    #        if tally.axes['f'] is None and words[0] not in ['1', 'f']:                                                                                       
    #            tally.title = line.strip()                                                                                                                   
    #            print "tally.title:", tally.title                                                                                                            
    #            return 0                                                                                                                                     
                                                                                                                                                              
            if tally.axes['t'] and is_vals == False and len(tally.data) == 0 and line[0] == ' ':
                for w in words: tally.axes['t'].arraycsn.append(float(w))
                continue

            if tally.axes['e'] and tally.axes['t'] is None and line[0] == ' ':
                for w in words: tally.axes['e'].arraycsn.append(float(w))
                continue

            if tally.axes['u'] and tally.axes['s'] is None and line[0] == ' ':
                for w in words: tally.axes['u'].arraycsn.append(float(w))
                continue

            if   not tally.axes['f'] and re.search('^f', line[0]):
                tally.axes['f'] = Axis(words[0], map(int, words[1:]))
                continue
            elif not tally.axes['d'] and re.search('^d', line[0]):
                tally.axes['d'] = Axis(words[0], map(int, words[1:]))
                continue
            elif not tally.axes['u'] and re.search ("u[tc]?", line[0:1]):
                tally.axes['u'] = Axis(words[0], map(int, words[1:]))
                continue
            elif not tally.axes['s'] and re.search('^s[tc]?', line[0:1]):
                tally.axes['s'] = Axis(words[0], map(int, words[1:]))
#                print "here"
#                tally.axes['s'].Print()
                continue
            elif not tally.axes['m'] and re.search('^m[tc]?', line[0:1]):
                tally.axes['m'] = Axis(words[0], map(int, words[1:]))
                continue
            elif not tally.axes['c'] and re.search('^c[tc]?', line[0:1]): 
                tally.axes['c'] = Axis(words[0], map(int, words[1:]))                         
                continue
            elif not tally.axes['e'] and re.search("^e[tc]?",  line[0:1]):
                tally.axes['e'] = Axis(words[0], map(int, words[1:]))                        
                continue
            elif not tally.axes['t'] and re.search("^t[tc]?", line[0:1]):
                tally.axes['t'] = Axis(words[0], map(int, words[1:]))
                continue
            # elif line[0:2] == 'tfc':
            #     tally.tfc_n = words[1]
            #     tally.tfc_jtf = words[2:]
            #     continue

            if tally.tfc_n and line[0] == ' ':                                      
                tally.tfc_data.append(map(float, words))
                continue

            if words[0] == 'vals':
                is_vals = True
                continue

            if is_vals:
                if line[0] == ' ':
                    for iw, w in enumerate(words):
                        if not iw % 2:
                            tally.data.append(float(w))
                        else:
                            tally.errors.append(float(w))
                else:
                    is_vals = False # at this point we should be at the 'tfc' line
                    if line[0:3] == 'tfc':
                        tally.tfc_n = words[1]
                        tally.tfc_jtf = words[2:]
                    else:
                        print "mctal.py: something goes wrong after the 'values' - we assumed it's the 'tfc' record"
                    continue


        if tally:  # save the latest tally
            if tally.number and tally.number % 10 in self.good_tallies:
                self.tallies.append(tally)
            del tally
                    
        file_in.close()

        return self.tallies
