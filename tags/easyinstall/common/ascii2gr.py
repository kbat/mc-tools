#! /usr/bin/env python
#
# ASCII to TGraph  converter

import sys,time,os,re
from array import array
from string import join
import argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def GetAsymmGraphs(colx, exlow, exhigh, coly, eylow, eyhigh, fname, l1, l2, name):
    graphs = ROOT.TObjArray()
    GetAsymmGraph(colx, exlow, exhigh, coly, eylow, eyhigh, fname, l1, l2, name, graphs, 0)
    return graphs

def GetGraphs(colx, colex, coly, coley, fname, l1, l2, name, title, relerr):
    graphs = ROOT.TObjArray()
    GetGraph(colx, colex, coly, coley, fname, l1, l2, name, title, graphs, 0, relerr)
    return graphs

def GetAsymmGraph(colx, exlow, exhigh, coly, eylow, eyhigh, fname, l1, l2, name, graphs, name_index):
    """
    Read between lines l1 and l2
    """

    vx = []  # vector of x-values
    vexlow = [] # vector of x-errors
    vexhigh = [] # vector of x-errors
    vy = []  #
    veylow = [] #
    veyhigh = []
    npoints = 0
    title = ""
    xtitle = ""
    ytitle = ""

    if l1 == None: l1 = int(1) # we count lines from one
    if l2 == None:
        ftmp = open(fname)
        l2 = len(ftmp.readlines()) # set to the number of lines in the file
        ftmp.close()

    print "--->reading between lines", l1, l2

    f = open(fname)
    for nline, line in enumerate(f.readlines(), 1):
        if l1 and nline<l1: continue
        if l2 and nline>l2: break

        words = line.split()
#        print words, len(words)

        if len(words) == 0:
            if npoints == 0:
                continue # we have not read any points yet -> just continue
            else:
#            print "creating new graph object"
                break
        if words[0][0] == '#':
            continue
        if len(words) < 2:
            print "Skipping line ", line.strip()
            continue

        vx.append(float(words[colx-1]))
        vy.append(float(words[coly-1]))

        vexlow.append(float(words[exlow-1]))
        vexhigh.append(float(words[exhigh-1]))

        veylow.append(float(words[eylow-1]))
        veyhigh.append(float(words[eyhigh-1]))

        npoints = npoints+1

    f.close()

#    print "number of points: ", npoints

    if npoints>0:

        gr = ROOT.TGraphAsymmErrors(npoints)
    
        if  name_index==0:
            gr.SetName(name)
        else:
            gr.SetName("%s%d" % (name, name_index))

        name_index = name_index+1
        
        for i in range(npoints):
            gr.SetPoint(i, vx[i], vy[i])
            gr.SetPointError(i, vexlow[i], vexhigh[i], veylow[i], veyhigh[i])
                    
        graphs.Add(gr)

#    print "nlines:", nline, l2
    if nline<l2:
        GetAsymmGraph(colx, exlow, exhigh, coly, eylow, eyhigh, fname, nline+1, l2, name, graphs, name_index)


def GetGraph(colx, colex, coly, coley, fname, l1, l2, name, title, graphs, name_index=0, relerr=False):
    """
    Read between lines l1 and l2
    """

    vx = []  # vector of x-values
    vex = [] # vector of x-errors
    vy = []  #
    vey = [] #
    npoints = 0
    xtitle = ""
    ytitle = ""

    if l1 == None: l1 = int(1) # we count lines from one
    if l2 == None:
        ftmp = open(fname)
        l2 = len(ftmp.readlines()) # set to the number of lines in the file
        ftmp.close()

    print "--->reading between lines", l1, l2

    f = open(fname)
    for nline, line in enumerate(f.readlines(), 1):
        if l1 and nline<l1: continue
        if l2 and nline>l2: break

        words = line.split()
#        print words, len(words)

        if len(words) == 0:
            if npoints == 0:
                continue # we have not read any points yet -> just continue
            else:
#            print "creating new graph object"
                break

        if words[0][0] == '#':
            # set titles in the case of data files downloaded from nndc.bnl.gov/exfor
            if words[0] == '#name:':
                title = join(words[1:])
            elif words[0] == '#X.axis:':
                xtitle = join(words[1:])
            elif words[0] == '#Y.axis:':
                ytitle = join(words[1:])
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

#    print "number of points: ", npoints

    if npoints>0:

        if not colex and not coley: gr = ROOT.TGraph(npoints)
        else:                       gr = ROOT.TGraphErrors(npoints)
        if len(xtitle) or len(ytitle):
#            gr.SetTitle("%s;%s;%s;" % (title, xtitle, ytitle))
            gr.SetTitle(title)
            gr.GetXaxis().SetTitle(xtitle)
            gr.GetYaxis().SetTitle(ytitle)
        elif ";" in title:
            gr.SetTitle(title)
#            gr.GetXaxis().SetTitle(xtitle)
#            gr.GetYaxis().SetTitle(ytitle) 
#            title,xtitle,ytitle = title.split(";")
#            gr.SetTitle(title)
        else:
            gr.SetTitle(title)

    
        if  name_index==0:
            gr.SetName(name)
        else:
            gr.SetName("%s%d" % (name, name_index))

        name_index = name_index+1
        
        for i in range(npoints):
            gr.SetPoint(i, vx[i], vy[i])
            if colex or coley: 
                if relerr:
                    gr.SetPointError(i, vex[i]*vx[i], vey[i]*vy[i])
                else:
                    gr.SetPointError(i, vex[i], vey[i])
                    
        graphs.Add(gr)

#    print "nlines:", nline, l2
    if nline<l2:
#        print "again"
        GetGraph(colx, colex, coly, coley, fname, nline+1, l2, name, graphs, name_index)

def main():
    """
    Converts ASCII file to TGraph or TGraphErrors
    Lines starting with '#' are ignored.

    It is assumed that different graphs are separated by an empty line. In this case a sequental prefix is appended to the graph's names.
    """
    
    parser = argparse.ArgumentParser(description=main.__doc__, epilog='Homepage: http://code.google.com/p/mc-tools')
    parser.add_argument('-x',  dest='colx',  type=int, help='x-column number (columns start from ONE)', required=True)
    parser.add_argument('-ex', dest='colex', type=int, help='ex-column number')
    parser.add_argument('-y',  dest='coly',  type=int, help='y-column number', required=True)
    parser.add_argument('-ey', dest='coley', type=int, help='ey-column number')
    parser.add_argument('inname', type=str, help='input file')
    parser.add_argument('-start', type=int, help='line to start', default=1)
    parser.add_argument('-end',   type=int, help='line to end, >=1, read until the end of file, if skipped')
    parser.add_argument('-o', dest='outname', type=str, help='output file name')
    parser.add_argument('-update', action="store_true", default=False, help='if set, the file will be updated, otherwise - recreated')
    parser.add_argument('-relerr', action="store_true", default=False, help='if set, the errors are assumed to be relative')
    parser.add_argument('-name', type=str, help='Graph name', default='gr')
    parser.add_argument('-title', type=str, help='Graph title', default='')

    parser.add_argument('-exlow', dest='exlow', type=int, help='low abs error on X in the case of TGraphAsymmErrors')
    parser.add_argument('-exhigh', dest='exhigh', type=int, help='high abs error on X in the case of TGraphAsymmErrors')
    parser.add_argument('-eylow', dest='eylow', type=int, help='low abs error on Y in the case of TGraphAsymmErrors')
    parser.add_argument('-eyhigh', dest='eyhigh', type=int, help='high abs error on Y in the case of TGraphAsymmErrors')

    print parser.parse_args()

    results = parser.parse_args()

    fname_in = results.inname
    if results.outname:
        fname_out = results.outname
    else:
        fname_out = fname_in.replace(".dat", ".root")
    
    if fname_in == fname_out: fname_out = fname_in + ".root"
    print fname_in, '=>',fname_out

    if results.update:
        fout_option = 'update'
    else:
        fout_option = 'recreate'

    fout = ROOT.TFile(fname_out, fout_option)
    if results.eylow is None:
        GetGraphs(results.colx, results.colex, results.coly, results.coley, fname_in, results.start, results.end, results.name, results.title, results.relerr).Write()
    else:
        GetAsymmGraphs(results.colx, results.exlow, results.exhigh,
                       results.coly, results.eylow, results.eyhigh,
                       fname_in, results.start, results.end, results.grname).Write()
    fout.ls()
    fout.Close()
    


if __name__ == "__main__":
    sys.exit(main())
