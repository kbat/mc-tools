#! /usr/bin/env python
#
# ASCII to TH1F converter

import sys,time,os,re
from ROOT import ROOT, TH1F, TFile
from array import array

def GetHistogram(colxmin, colxmax, coly, coley, opt, fname):
#    print colxmin, colxmax, coly, coley, opt, fname
    print opt
    f = open(fname)
    vx = []  # upper border of the energy bin
    vy = []  # flux
    vey = [] # error
    line_number = 0
    x, dx, y, ey = 0, 0, 0, 0
    xmin = [] # array of xmin - used with 'mcnp' option

    for iline,line in enumerate(f.readlines()):
        words = line.split()
#        print words;
        if len(words) == 0:
            break
        if words[0][0] == '#':
            continue

        if line_number == 0:
            if 'mcnp' not in opt:
                x = float(words[colxmin])
                vx.append(x)
            if 'center' in opt: 
                line_number = line_number + 1
                continue
            elif 'mcnp' in opt:
                vx.append(0.0)
        x = float(words[colxmax])
        vx.append(x)
        y  = float(words[coly])
        ey = float(words[coley])
        vy.append(y)
        if 'abserr' in opt:
            vey.append(ey)
        else:
            vey.append(y*ey)

        line_number = line_number+1

    f.close()

#    print "vx", vx
#    print "vy", vy
#    print "ey", vey

    nbins = len(vy)
    h = TH1F("h%d" % (coly), "", nbins, array('f', vx))
    for i in range(nbins):
        if 'width' in opt:
            dx = vx[i+1]-vx[i]
        else:
            dx = 1.0
        h.SetBinContent(i+1, vy[i]/dx)
        h.SetBinError(i+1,  vey[i]/dx)

    return h

def main():
    """
    Converts ASCII table to TH1
    Usage: ascii2th1 colxmin coly opt fname
           coly - number of column with data
                  relative data errors are assumed to be in coly+1
                  xbins are assumed to be in the columns 0 and 1
           opt - comma separated list of options. set it to 'width' if you need to divide y by the bin width
                otherwise use 'no'
                 if opt == 'center' then instead of lower/upper bin boundary only bin center is given (=>skip the 1st record and do things wrong... -> check required).
           Lines starting with '#' are ignored.

           EXAMPLE: assume you have a file with the following structure:
                     x1   x2    y1 ey1
                     x2   x3    y2 ey2
                     x3   x4    y3 ey3
                    so, in order to convert it in ROOT you write: ascii2th1 0 2 width file.txt
    """
    if len(sys.argv) == 1:
        print main.__doc__
        sys.exit(1)

    colxmin = int(sys.argv[1])
    coly = int(sys.argv[2])
    coley = coly+1
    opts = sys.argv[3].split(',')
    supported_options = ['no', 'width', 'center', 'mcnp', 'abserr']
    for opt in opts:
        if opt not in (supported_options):
            print "opt", opt, "is not supported."
            print "Option must take one of these values:", supported_options
            sys.exit(1)

    if 'center' in opts or 'mcnp' in opts:
        colxmax = colxmin
        print "here"
    else:
        colxmax = colxmin+1

    fname_in = sys.argv[4]
    fname_out = fname_in.replace(".dat", ".root")
    if fname_in == fname_out: fname_out = fname_in + ".root"
    print fname_in, '=>',fname_out

    fout = TFile(fname_out, "RECREATE")
    GetHistogram(colxmin, colxmax, coly, coley, opts, fname_in).Write()
    fout.Close()
    


if __name__ == "__main__":
    sys.exit(main())
