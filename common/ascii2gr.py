#! /usr/bin/env python
#
# ASCII to TH1F converter

import sys,time,os,re
from ROOT import ROOT, TGraph, TGraphErrors, TFile
from array import array

def GetGraph(colx, colex, coly, coley, fname):
    f = open(fname)
    vx = []  # vector of x-values
    vex = [] # vector of x-errors
    vy = []  #
    vey = [] #
    npoints = 0

    for line in f.readlines():
        words = line.split()
        print words;
        if len(words) < 2:
            print "Skipping line ", line.strip()
            continue
        if words[0][0] == '#':
            continue

        vx.append(float(words[colx-1]))
        vy.append(float(words[coly-1]))

        if colex: vex.append(float(words[colex-1]))
        else: vex.append(0)
        if coley: vey.append(float(words[coley-1]))
        else: vey.append(0)

        npoints = npoints+1

    f.close()

    print npoints

    print colex, coley

    if colex == 0 and coley == 0:
        gr = TGraph(npoints)
    else:
        gr = TGraphErrors(npoints)

    gr.SetName('gr')

    for i in range(npoints):
        gr.SetPoint(i, vx[i], vy[i])
        if colex or coley: gr.SetPointError(i, vex[i], vey[i])

    return gr

def main():
    """
    Converts ASCII table to TGraph or TGraphErrors
    Usage: ascii2gr colx colex coly coley fname
           colx, coly - column numbers with x and y values
           colex, coley - column numbers with x and y errors
           if colex or coley is 0 then these values are not read
           Lines starting with '#' are ignored.

           EXAMPLE: assume you have a file with the following structure:
                     x1   y1  ey1
                     x2   y2  ey2
                     x3   y3  ey3
                    so, in order to convert it in ROOT you write: ascii2th1 1 0 2 3 file.txt
    """
    if len(sys.argv) == 1:
        print main.__doc__
        sys.exit(1)

    colx  = int(sys.argv[1])
    colex = int(sys.argv[2])
    coly  = int(sys.argv[3])
    coley = int(sys.argv[4])

    fname_in = sys.argv[5]
    fname_out = fname_in.replace(".dat", ".root")
    if fname_in == fname_out: fname_out = fname_in + ".root"
    print fname_in, '=>',fname_out

    fout = TFile(fname_out, "RECREATE")
    GetGraph(colx, colex, coly, coley, fname_in).Write()
    fout.Close()
    


if __name__ == "__main__":
    sys.exit(main())
