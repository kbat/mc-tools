#! /usr/bin/python -W all

import sys, argparse
import numpy as np
from os import path
sys.path.append("/usr/local/flair")
sys.path.append("/usr/local/flair/lib")
import Data, fortran, struct
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def getType(n):
    """ Decrypt what(1) of usrbdx """
    for i1 in (-2,-1,1,2):
        for i2 in (0,1):
            for i3 in (0,1):
                if (i1+10*i2+100*i3 == n):
                    return (i1,i2,i3) # i3 is irrelevant - use bin.fluence instead
    print >> sys.stderr, "usrbdx2root: what(1) == %d undefined" % n
    sys.exit(1)

def isLogE(x):
    if x in (-2,-1):
        return True
    return False

def isLogA(x):
    if x in (-2,2):
        return True
    return False

def getAxesTitle(det,x):
    ztitle = "1/cm^{2}/GeV/sr"
    if int(det.dist) in (208,211): # differential energy fluence/current
        ztitle = "GeV/cm^{2}/GeV/sr"   # FLUKA manual page 247
    return {
        -2 : ";log10(Energy/GeV);log10(#Omega/rad);" + ztitle,
        -1 : ";log10(Energy/GeV);#Omega [rad];" + ztitle,
         1 : ";Energy [GeV];#Omega [rad];" + ztitle,
         2 : ";Energy [GeV];log10(#Omega/rad);" + ztitle,
        }[x]

def getLogBins(nbins, low, high):
    """ Return array of bins with log10 equal widths """

    x = float(low)
    dx = pow(high/low, 1.0/nbins);
    
    return np.array([x*pow(dx,i) for i in range(nbins+1)], dtype=float)

def getLinBins(nbins, low, high):
    """ Return array of bins with linearly equal widths """
    x = float(low)
    dx = float(high-low)/nbins

    return np.array([x+i*dx for i in range(nbins+1)], dtype=float)

def getEbins(det, i):
    """ Return lin or log energy bins depending on the value of i """

    if isLogE(i):
        return getLogBins(det.ne, det.elow, det.ehigh)
    else:
        return getLinBins(det.ne, det.elow, det.ehigh)

def getAbins(det, i):
    """ Return lin or log angular bins depending on the value of i """

    if isLogA(i):
        return getLogBins(det.na, det.alow, det.ahigh)
    else:
        return getLinBins(det.na, det.alow, det.ahigh)

def hist(det):
    """ Create histogram for the given detector """

    w1 = getType(det.type) # decrypted what(1)
    title = det.name + getAxesTitle(det,w1[0])
    return ROOT.TH2F(det.name, title, det.ne, getEbins(det, w1[0]), det.na, getAbins(det, w1[0]))


class Usrtrack(Data.Usrxxx):
    """ Reads the ustsuw binary output
        (USRTRACK / USRCOLL estimators)
    """
    def readHeader(self, filename):
        """ Reads the file header info 
            Based on Data.Usrbdx
        """
        f = Data.Usrxxx.readHeader(self, filename)
        self.sayHeader()
        
        for i in range(1000):
            data = fortran.read(f)
            if data is None: break
            size = len(data)
            print "size: ", size

            if size == 14 and data[:10] == "STATISTICS":
                self.statpos = f.tell()
                for det in self.detector:
                    data = Data.unpackArray(fortran.read(f))
                    det.total = data[0]
                    det.totalerror = data[1]
                    for j in range(6):
                        fortran.skip(f)
                break

            if size != 50: raise IOError("Invalid USRTRACK/USRCOLL file")

            header = struct.unpack("=i10siiififfif", data)

            det = Data.Detector()
            det.nb = header[0]
            det.name = header[1].strip() # titutc - track/coll name
            det.type = header[2] # itustc - type of binning: 1 - linear energy etc
            det.dist = header[3] # idustc = distribution to be scored
            det.reg  = header[4] # nrustc = region
            det.volume = header[5] # vusrtc = volume (cm**3) of the detector
            det.lowneu = header[6] # llnutc = low energy neutron flag
            det.elow = header[7] # etclow = minimum energy [GeV]
            det.ehigh = header[8] # etchgh = maximum energy [GeV]
            det.ne = header[9] # netcbn = number of energy intervals
            det.de = header[10] # detcbn = energy bin width

            self.detector.append(det)

            if det.lowneu:
                data = fortran.read(f)
                det.ngroup =  struct.unpack("=i",data[:4])[0]
                det.egroup = struct.unpack("=%df"%(det.ngroup+1), data[4:])
            else:
		det.ngroup = 0
		det.egroup = []

            self.printHeader(det)
	    size  = (det.ngroup+det.ne) * 4
	    if size != fortran.skip(f):
		raise IOError("Invalid USRBDX file")
        f.close()

    def printHeader(self, det):
        """ Prints the header """
        print "Detector:", det.name
        print " binning type: ", det.type
        print " distribution to be scored:", det.dist
        print " region:", det.reg
        print " volume:", det.volume
        print " low energy neutrons:", det.lowneu
        print " %g < E < %g GeV / %d bins; bin width: %g" % (det.elow, det.ehigh, det.ne, det.de)
        
            
                

def main():
    """ Converts ustsuw output into a ROOT TH1F histogram """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('usrtrack', type=str, help='ustsuw binary output')
    parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')
    
    args = parser.parse_args()

    if not path.isfile(args.usrtrack):
        print >> sys.stderr, "ustsuw2root: File %s does not exist." % args.usrtrack
        return 1

    if args.root == "":
        rootFileName = "%s%s" % (args.usrtrack,".root")
    else:
        rootFileName = args.root
    
    b = Usrtrack()
    b.readHeader(args.usrtrack)

    ND = len(b.detector)
    
    if args.verbose:
        b.sayHeader()
        print "\n%d tallies found:" % ND
        for i in range(ND):
            b.say(i)
            print ""

    fout = ROOT.TFile(rootFileName, "recreate")
    for i in range(ND):
        val = Data.unpackArray(b.readData(i))
        err = Data.unpackArray(b.readStat(i))
        det = b.detector[i]

        h = hist(det)
        
        for i in range(det.ne):
            for j in range(det.na):
                    gbin = i + j * det.ne
                    h.SetBinContent(i+1, j+1, val[gbin])
                    h.SetBinError(i+1, j+1, err[gbin]*val[gbin])
        h.SetEntries(b.weight)
        h.Write()

    fout.Close()

if __name__=="__main__":
    sys.exit(main())
