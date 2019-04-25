#! /usr/bin/env python
#
# ASCII to TH1F converter

from __future__ import print_function
import sys,time,os,re
from array import array
import ROOT, argparse

ROOT.PyConfig.IgnoreCommandLineOptions = True

def GetHistogram(colxmin, colxmax, coly, coley, opt, hname, htitle, fname):
#    print(colxmin, colxmax, coly, coley, opt, fname)
    print(opt)
    f = open(fname)
    vx = []  # upper border of the energy bin
    vy = []  # flux
    vey = [] # error
    line_number = 0
    x, dx, y, ey = 0, 0, 0, 0
    xmin = [] # array of xmin - used with 'mcnp' option

    for iline,line in enumerate(f.readlines()):
        words = line.split()
#        print(words);
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
        if 'relerr' in opt:
            vey.append(ey*y)
        else:
            vey.append(ey)

        line_number = line_number+1

    f.close()

#    print("vx", vx)
#    print("vy", vy)
#    print("ey", vey)

    nbins = len(vy)
    h = ROOT.TH1F(hname, htitle, nbins, array('f', vx))
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
    supported_options = ['no', 'width', 'center', 'mcnp', 'abserr']

    parser = argparse.ArgumentParser(description=main.__doc__, epilog='epilog')
    parser.add_argument('-xmin',  dest='colxmin',  type=int, help='xmin column', required=True)
    parser.add_argument('-xmax',  dest='colxmax',  type=int, help='xmax column', required=True)
    parser.add_argument('-ex',  dest='colex',  type=int, help='x-err column', required=True)
    parser.add_argument('-y',  dest='coly',  type=int, help='y column', required=True)
    parser.add_argument('-ey',  dest='coley',  type=int, help='y-err column', required=True)
    parser.add_argument('-hname',  dest='hname',  type=str, help='histogram name', required=False, default='h')
    parser.add_argument('-htitle',  dest='htitle',  type=str, help='histogram title', required=False, default="")
    parser.add_argument('option', type=str, help='option', choices=supported_options) #, metavar='(e-the|e-phi)')
    parser.add_argument('inname', type=str, help='input file')
    results = parser.parse_args()

    if len(sys.argv) == 1:
        print(main.__doc__)
        sys.exit(1)


    fname_in = results.inname
    fname_out = fname_in.replace(".dat", ".root")
    if fname_in == fname_out: fname_out = fname_in + ".root"
    print(fname_in, '=>',fname_out)

    fout = ROOT.TFile(fname_out, "recreate")
    GetHistogram(results.colxmin, results.colxmax, results.coly, results.coley, results.option, results.hname, results.htitle, fname_in).Write()
    fout.Close()
    


if __name__ == "__main__":
    sys.exit(main())
