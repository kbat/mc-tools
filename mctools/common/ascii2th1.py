#! /usr/bin/python
#
# ASCII to TH1F converter

from __future__ import print_function
import sys,time,os,re
from array import array
import ROOT, argparse
import pandas as pd

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

def mcnp(fin, fout, hname, htitle, x,y):
    df = pd.read_csv(fin, header=None, sep=' ', names=["x", "y"]) # data frame
##    df.info()
    nrow,ncol = df.shape
    nbins = nrow-1 # number of bins in the histogram

#    print(df['x'][1])

    vx = []
    for i in range(nrow):
        x = df['x'][i]
        vx.append(x)

    h = ROOT.TH1F(hname, htitle, nbins, array('f', vx))

    for i in range(nbins):
        h.SetBinContent(i+1, df['y'][i])

    h.Print('a')

    return h


def main():
    """
    Converts ASCII table to TH1.
    Column numbering starts from ONE.
    """
    supported_options = ['root', 'mcnp', 'center']

    parser = argparse.ArgumentParser(description=main.__doc__, epilog='epilog')
    parser.add_argument('-xmin',  dest='colxmin',  type=int, help='xmin column', required=True)
    parser.add_argument('-xmax',  dest='colxmax',  type=int, help='xmax column', default=-1)
    parser.add_argument('-ex',  dest='colex',  type=int, help='x-err column', default=-1)
    parser.add_argument('-y',  dest='coly',  type=int, help='y column', required=True)
    parser.add_argument('-ey',  dest='coley',  type=int, help='y-err column', default=-1)
    parser.add_argument('-hname',  dest='hname',  type=str, help='histogram name', required=False, default='h')
    parser.add_argument('-htitle',  dest='htitle',  type=str, help='histogram title', required=False, default="")
    parser.add_argument('option', type=str, help='option', choices=supported_options)
    parser.add_argument('inname', type=str, help='input file')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        print(main.__doc__)
        sys.exit(1)


    fname_in = args.inname
    fname_out = fname_in.replace(".dat", ".root")
    if fname_in == fname_out: fname_out = fname_in + ".root"
    print(fname_in, '=>',fname_out)

    fout = ROOT.TFile(fname_out, "recreate")
    if args.option == "mcnp":
        h = mcnp(fname_in, fname_out, args.hname, args.htitle, args.colxmin, args.coly)
        h.Write()
    else:
        GetHistogram(args.colxmin, args.colxmax, args.coly, args.coley, args.option, args.hname, args.htitle, fname_in).Write()

    fout.Close()



if __name__ == "__main__":
    sys.exit(main())
