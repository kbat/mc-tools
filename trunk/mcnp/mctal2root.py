#! /usr/bin/python -W all
#
# $URL$
# $Id$
#

import sys, re, string
from array import array
from mctal import Header, Tally, Axis, MCTAL
from mcnp import GetParticleNames
from ROOT import ROOT, TH3F, TH1F, TFile


def main():
    """
    readmctal - an example how to read the mctal file
    Usage: readmctal mctal
    ... many features are not yet supported!

    Homepage: http://code.google.com/p/mc-tools
    """

#    good_tallies = [4] # list of 'good' tally types
    fname_in = sys.argv[1]


    mctal = MCTAL(fname_in)
    mctal.good_tallies = [2, 4]
    mctal.verbose = False
    tallies = mctal.Read()
    print "total number of good tallies:", len(tallies)

    tallies = [ mctal.GetTally(12) ]
    
    for t in tallies:
        for a in ['f', 'd', 'u', 's', 'm', 'c', 'e', 't']:   print a, t.axes[a].arraycsn
        
        nbins = len(t.axes['e'].arraycsn)
        bins = [0] + t.axes['e'].arraycsn
        print bins, len(bins)

        h55001a = TH1F("f%dh55001a" % t.number, "", nbins, array('f', bins))
        h55001b = TH1F("f%dh55001b" % t.number, "", nbins, array('f', bins))
        h55006a = TH1F("f%dh55006a" % t.number, "", nbins, array('f', bins))
        h55006b = TH1F("f%dh55006b" % t.number, "", nbins, array('f', bins))
        
#        print t.data
        print len(t.data)

        gbin = 0
        for f in range(2):
            for s in range(2):
                for e in range(nbins):
                    if s == 0:
                        if f==0:
                            h55001a.SetBinContent(e+1, t.data[gbin])
                            h55001a.SetBinError(e+1, t.errors[gbin]*t.data[gbin])
                        elif f==1:
                            h55006a.SetBinContent(e+1, t.data[gbin])
                            h55006a.SetBinError(e+1, t.errors[gbin]*t.data[gbin])
                    elif s == 1:
                        if f==0:
                            h55001b.SetBinContent(e+1, t.data[gbin])
                            h55001b.SetBinError(e+1, t.errors[gbin]*t.data[gbin])
                        elif f==1:
                            h55006b.SetBinContent(e+1, t.data[gbin])
                            h55006b.SetBinError(e+1, t.errors[gbin]*t.data[gbin])
                    gbin = gbin+1
                gbin = gbin+1 # total


            # h55001b.SetBinContent(i+1, t.data[gbin])
            # h55001b.SetBinError(i+1, t.errors[gbin]*t.data[gbin])
            # gbin = gbin+1
            # h55006a.SetBinContent(i+1, t.data[gbin])
            # h55006a.SetBinError(i+1, t.errors[gbin]*t.data[gbin])
            # gbin = gbin+1
            # h55006b.SetBinContent(i+1, t.data[gbin])
            # h55006b.SetBinError(i+1, t.errors[gbin]*t.data[gbin])
            # gbin = gbin+1
        print gbin

        fout = TFile("out.root", "recreate")
        h55001a.Write()
        h55001b.Write()
        h55006a.Write()
        h55006b.Write()
        fout.Close()

    return 0

    # code below works for mesh tally only
    t = None
    for tt in tallies:
        if tt.number == 4:
            t = tt

#    t.axes['f'].Print()
    # xyz? xzy- yxz- yzx- zxy? zyx-
    # yxz?
    # 3 loops XYZ -> yzx? zyx?
    # 3 loops ZYX -> yxz? xyz?  back: t.data[len(t.data)-ii-1]: 

            xbins = map(float, t.axes['f'].getBins('i'))
            ybins = map(float, t.axes['f'].getBins('j'))
            zbins = map(float, t.axes['f'].getBins('k'))

            h = TH3F("h", "", len(xbins)-1, array('f', xbins),
                     len(ybins)-1, array('f', ybins),
                     len(zbins)-1, array('f', zbins))
            if (len(xbins)-1) * (len(ybins)-1) * (len(zbins)-1) != len(t.data):
                print "data array length is not equal to ni*nj*nk"

            ii = 0
            for i in range(h.GetNbinsX()):
                for j in range(h.GetNbinsY()):
                    for k in range(h.GetNbinsZ()):
                        h.SetBinContent(i+1, j+1, k+1, t.data[ii])
                        h.SetBinError(i+1, j+1, k+1, t.data[ii]*t.errors[ii])
                        ii = ii + 1

            h.SaveAs("a.root")
    
    return 0



if __name__ == '__main__':
    sys.exit(main())
