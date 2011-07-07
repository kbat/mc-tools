#! /usr/bin/env python
#
# ASCII to TH1F converter

import sys,time,os,re
from ROOT import ROOT, TGraph, TGraphErrors, TFile
from array import array
import argparse

def GetGraph(colx, colex, coly, coley, fname, l1, l2, name):
    """
    Read between lines l1 and l2
    """

    f = open(fname)
    vx = []  # vector of x-values
    vex = [] # vector of x-errors
    vy = []  #
    vey = [] #
    npoints = 0

    for nline, line in enumerate(f.readlines(), 1):
        if l1 and nline<l1: continue
        if l2 and nline>l2: break

        words = line.split()
#        print words;
        if words[0][0] == '#':
            continue
        if len(words) < 2:
            print "Skipping line ", line.strip()
            continue

        vx.append(float(words[colx-1]))
        vy.append(float(words[coly-1]))

        if colex: vex.append(float(words[colex-1]))
        else: vex.append(0)
        if coley: vey.append(float(words[coley-1]))
        else: vey.append(0)

        npoints = npoints+1

    f.close()

    print "number of points: ", npoints

    print colex, coley

    if not colex and not coley:
        gr = TGraph(npoints)
    else:
        gr = TGraphErrors(npoints)

    gr.SetName(name)

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
    
    parser = argparse.ArgumentParser(description=main.__doc__, epilog='epilog')
    parser.add_argument('-x',  dest='colx',  type=int, help='x-column number', required=True)
    parser.add_argument('-ex', dest='colex', type=int, help='ex-column number')
    parser.add_argument('-y',  dest='coly',  type=int, help='y-column number', required=True)
    parser.add_argument('-ey', dest='coley', type=int, help='ey-column number')
    parser.add_argument('inname', type=str, help='input file')
    parser.add_argument('-start', type=int, help='line to start, >=1')
    parser.add_argument('-end',   type=int, help='line to end, >=1')
    parser.add_argument('-o', dest='outname', type=str, help='output file name')
    parser.add_argument('-recreate', action="store_true", default=False)
    parser.add_argument('-name', type=str, help='Graph\'s name', default='gr')

    print parser.parse_args()

    results = parser.parse_args()

    fname_in = results.inname
    if results.outname:
        fname_out = results.outname
    else:
        fname_out = fname_in.replace(".dat", ".root")
    
    if fname_in == fname_out: fname_out = fname_in + ".root"
    print fname_in, '=>',fname_out

    if results.recreate:
        fout_option = 'recreate'
    else:
        fout_option = 'update'

    fout = TFile(fname_out, fout_option)
    GetGraph(results.colx, results.colex, results.coly, results.coley, fname_in, results.start, results.end, results.name).Write()
    fout.Close()
    


if __name__ == "__main__":
    sys.exit(main())
