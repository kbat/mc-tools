#! /usr/bin/env python
#
# ASCII to TH1F converter

import sys,time,os,re
from ROOT import ROOT, TH1F, TFile
from array import array

def GetHistogram(colxmin, colxmax, coly, coley, opt, fname):
    f = open(fname)
    vx = []  # upper border of the energy bin
    vy = []  # flux
    vey = [] # relative error
    line_number = 0
    x, dx, y, ey = 0, 0, 0, 0

    for line in f.readlines():
        words = line.split()
#        print words;
        if len(words) == 0:
            break
        if words[0][0] == '#':
            continue

        if line_number == 0:
            x = float(words[colxmin])
            vx.append(x)
            if opt=='center': 
                line_number = line_number + 1
                continue
        x = float(words[colxmax])
        vx.append(x)
        y  = float(words[coly])
        ey = float(words[coley])
        vy.append(y)
        vey.append(y*ey)

        line_number = line_number+1

    f.close()

    print vx
    print vy

    nbins = len(vy)
    h = TH1F("h%d" % (coly), "", nbins, array('f', vx))
    for i in range(nbins):
        if opt == 'width':
            dx = vx[i+1]-vx[i]
        else:
            dx = 1.0
        h.SetBinContent(i+1, vy[i]/dx)
        h.SetBinError(i+1,  vey[i]/dx)

    return h

def main():
    """
    Converts ASCII table to TH1
    Usage: ascii2th1 coly opt fname
           coly - number of column with data
                  relative data errors are assumed to be in coly+1
                  xbins are assumed to be in the columns 0 and 1
           opt - set it to 'width' if you need to divide y by the bin width
                otherwise use 'no'
                 if opt == 'center' then instead of lower/upper bin boundary only bin center is given (=>skip the 1st record and do things wrong... -> check required).
           Lines starting with '#' are ignored.

           EXAMPLE: assume you have a file with the following structure:
                     x1   x2    y1 ey1
                     x2   x3    y2 ey2
                     x3   x4    y3 ey3
                    so, in order to convert it in ROOT you write: ascii2th1 2 width file.txt
    """
    if len(sys.argv) == 1:
        print main.__doc__
        sys.exit(1)

    colxmin = 0
    coly = int(sys.argv[1])
    coley = coly+1
    opt = sys.argv[2]
    if opt not in ('no', 'width', 'center'):
        print "opt must be either 'no' or 'width'"
        sys.exit(1)

    if opt=='center':
        colxmax = colxmin
    else:
        colxmax = colxmin+1

    fname_in = sys.argv[3]
    fname_out = fname_in.replace(".dat", ".root")
    if fname_in == fname_out: fname_out = fname_in + ".root"
    print fname_in, '=>',fname_out

    fout = TFile(fname_out, "RECREATE")
    GetHistogram(colxmin, colxmax, coly, coley, opt, fname_in).Write()
    fout.Close()
    


if __name__ == "__main__":
    sys.exit(main())
