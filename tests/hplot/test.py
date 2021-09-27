#!/usr/bin/env python3

from os import system
from sys import exit
import ROOT

nx, xmin, xmax = (4, -2, 2)
ny, ymin, ymax = (6, -3, 3)
nz, zmin, zmax = (8, -4, 4)

def check(i, j, k, val, hval, err, herr):
    nerrors = 0
    if val != hval:
        nerrors += 1
        print(i,j,k,"Value is wrong:", hval, val)
    if err != herr:
        nerrors += 1
        print(i,j,k,"Error is wrong", herr, err)
    return nerrors

def bins(nbins, x1, x2):
    width = (x2-x1)/nbins
    return [x1+width*(i-0.5) for i in range(1, nbins+1)]

def build(fname, hname):

    h = ROOT.TH3I(hname, ";x;y;z", nx, xmin, xmax, ny, ymin, ymax, nz, zmin, zmax)

    for i in range(1,nx+1):
        for j in range(1,ny+1):
            for k in range(1,nz+1):
                h.SetBinContent(i,j,k, k*100+j*10+i)
                h.SetBinError(i,j,k, k*50+j*5+i)

    h.SaveAs(fname)

def testXY(fname="test.root", hname="h3"):

    offset = bins(nz, zmin, zmax)
    for plane in ("xy", "yx"):
        print("Testing ", plane)
        for k,off in enumerate(offset,1):
            command = "hplot %s %s -plane %s -offset %g -o hplot.root" % (fname, hname, plane, off)
            system(command)

            f = ROOT.TFile("hplot.root")
            c1 = f.Get("hplot")
            h = c1.GetListOfPrimitives().At(0)

            nerrors = 0
            for i in range(1,nx+1):
                for j in range(1,ny+1):
                    val = k*100+j*10+i
                    err = k*50+j*5+i
                    if plane == "yx":
                        hval = h.GetBinContent(i,j)
                        herr = h.GetBinError(i,j)
                    else:
                        hval = h.GetBinContent(j,i)
                        herr = h.GetBinError(j,i)
                    check(i,j,k,val,hval,err,herr)
            f.Close()

    return nerrors

def testXZ(fname="test.root", hname="h3"):

    offset = bins(ny, ymin, ymax)
    for plane in ("xz", "zx"):
        print("Testing ", plane)
        for j,off in enumerate(offset,1):
            command = "hplot %s %s -plane %s -offset %g -o hplot.root" % (fname, hname, plane, off)
            system(command)

            f = ROOT.TFile("hplot.root")
            c1 = f.Get("hplot")
            h = c1.GetListOfPrimitives().At(0)

            nerrors = 0
            for i in range(1,nx+1):
                for k in range(1,nz+1):
                    val = k*100+j*10+i
                    err = k*50+j*5+i
                    if plane == "xz":
                        hval = h.GetBinContent(k,i)
                        herr = h.GetBinError(k,i)
                    else:
                        hval = h.GetBinContent(i,k)
                        herr = h.GetBinError(i,k)
                    check(i,j,k,val,hval,err,herr)
            f.Close()

    return nerrors

def testYZ(fname="test.root", hname="h3"):

    offset = bins(nx, xmin, xmax)
    for plane in ("yz", "zy"):
        print("Testing ", plane)
        for i,off in enumerate(offset,1):
            command = "hplot %s %s -plane %s -offset %g -o hplot.root" % (fname, hname, plane, off)
            system(command)

            f = ROOT.TFile("hplot.root")
            c1 = f.Get("hplot")
            h = c1.GetListOfPrimitives().At(0)

            nerrors = 0
            for j in range(1,ny+1):
                for k in range(1,nz+1):
                    val = k*100+j*10+i
                    err = k*50+j*5+i
                    if plane == "yz":
                        hval = h.GetBinContent(k,j)
                        herr = h.GetBinError(k,j)
                    else:
                        hval = h.GetBinContent(j,k)
                        herr = h.GetBinError(j,k)
                    check(i,j,k,val,hval,err,herr)
            f.Close()

    return nerrors


def main():
    build("test.root", "h3")
    nerrors = 0
    nerrors = testXY()
    nerrors += testXZ()
    nerrors += testYZ()


    if nerrors == 0:
        system("rm -f hplot.root test.root")
        print("OK")
    else:
        print(nerrors, " errors found")

    return nerrors

if __name__ == "__main__":
    exit(main())
