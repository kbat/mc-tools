#! /usr/bin/pyton -W all

#import pandas as pd
import re,sys
import ROOT

class Table:
    def __init__(self, N):
        self.n = N
        self.title = "table %d" % self.n
        self.head = "" # names of columns
        self.buf = [] # buffer for data

    def checkBuffer(self):
        """ Perform basic checks of buf """
        nx = len(self.buf[0])
        for i,b in enumerate(self.buf):
            if nx != len(self.buf[i]):
                print>>sys.stderr, "Table %d: Wrong number of columns:" % (self.n), self.buf[i]
                sys.exit(1)

    def setXYtitle(self, h):
        """ Set x-title based of head """
        head = re.sub(" Y", "H", self.head)
        head = re.sub(" H", "H", head)
        head = head.split()
        for i,label in enumerate(head[1:],1):
            print i, label
            h.GetXaxis().SetBinLabel(i, label)

        if re.search("HALFLIFE,S", h.GetXaxis().GetBinLabel(1)): # HALFLIFE -> T_{1/2}
            h.GetXaxis().SetBinLabel(1, "T_{1/2} [sec]")

        h.GetYaxis().SetTitle(head[0].title())
        
                
    def getHist(self):
        """ Return TH2D """
        if self.n >= 7:
            return 0
        self.checkBuffer()
        ny = len(self.buf)
        nx = len(self.buf[0])-1
        h = ROOT.TH2D("table%d" % self.n, self.title, nx, 0, nx, ny, 0, ny)
        self.setXYtitle(h)
        for iy,b in enumerate(self.buf):
            data = map(float, b[1:])
            h.GetYaxis().SetBinLabel(iy+1, b[0])
            for ix,d in enumerate(data):
                h.SetBinContent(ix+1, iy+1, data[ix])
        return h

    def Print(self):
        print "Table %d: %s" % (self.n, self.title)
#        print "buffer:"
#        print self.buf

class AllTabs:
    def __init__(self, fname):
#        s = "H   1     STABLE   1.778E-0004 2.382E-0004 3.194E-0004 3.194E-0004"
#        s = "Ar 44   7.1220E+02 0.000E+0000 2.017E-0022 2.549E-0022 7.668E-0024"
#        m = re.sub("(?<=H)   ", "", s)
#        m = re.sub("(?<=[a-z,A-Z])   ", "", s)
#        m = re.sub("(?<=[a-z,A-Z]) {1,3}", "", s)
#        print m
        
        # s = "A<66               6.127E-0004 8.373E-0004 1.174E-0003 1.174E-0003"
        # s = "65<A<173            0.000E+0000 0.000E+0000 0.000E+0000 0.000E+0000"            
        # s = re.sub("(?<=<[0-9,A,<].) ", " a", s)
        # print s
        # return

        
        f = open(fname)
        it = 0
        self.tables = []
        t = 0 # current table
        for i,line in enumerate(f.readlines()):
#            line = line.rstrip()
            
            if re.search("Input Deck for CINDER'90", line): continue
            if re.search("\A\+", line): continue

            if t and t.head != "": # skip continuation of headers if the header is already set
                if re.search("UP", line): continue
                if re.search("DOWN", line): continue
                if re.search("NUCLIDE", line): continue
            
            if re.search(" TABLE ", line):
                tn = int(line.split()[-1]) # table number
                if t != 0:
                    self.tables.append(t)
                t = Table(tn)
                it = i # save the line number where the current table starts
            if i == it+2:
                title = line.strip()
                t.title = title
            elif i == it+6:
                t.head = line.strip()
                t.buf = [] #t.head + "\n"
            elif i>it+6:
                line = re.sub("STABLE", "-1", line)
                line = re.sub("(?<=[a-z,A-Z]) {1,3}", "", line) # remove space b/w isotope name and Z
                line = re.sub("TOTAL", "TOTAL -2", line)
                if re.search("<", line): continue # tmp do not support groups of nuclides in the end of a table
                t.buf.append(line.split())

        f.close()
