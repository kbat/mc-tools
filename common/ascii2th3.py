#! /usr/bin/env python
#
# ASCII to TH3F converter

import sys,time,os,re
from ROOT import ROOT, TH3F, TH1F, TFile
from array import array

def str2float(s):
    """
    convert array of strings into array of floats
    """
    f = []
    for i in s:
        f.append(float(i))
    print "array: ", f
    return f
        

def main():
    """
    xmin xmax ymin ymax zmin zmax val rel_err
    """
    
    f = open(sys.argv[1])
    x = []
    y = []
    z = []
    val = {} # dictionary of bin indices
    relerr = {} # dictionary of bin indices
    nline = 0 # line number
    i = 0 # bin x
    j = 0 # bin y
    k = 0 # bin z
    for line in f.readlines():
#        print nline, "\t", line.strip()
        if re.search("^#", line): continue # skip comments
        w = line.split()

        if nline == 0:
            x.append(w[0])
            y.append(w[2])
            z.append(w[4])

            x.append(w[1])
            y.append(w[3])
            z.append(w[5])
        else:
            if (w[0] != x[i]) and (w[1] != x[i+1]):
                i = i+1
                x.append(w[1])
#            print "check y: ", w[2], y[j]
            if (w[2] != y[j]) and (w[3] != y[j+1]):
                j = j+1
                y.append(w[3])
            if (w[4] != z[k]) and (w[5] != z[k+1]):
                k = k+1
                z.append(w[5])

#        print i, j, k

        val[(i,j,k)] = w[6]
        relerr[(i,j,k)] = w[7]

        nline = nline+1

    f.close()
    print "x: ", x
    print "y: ", y
    print "z: ", z
#    print val
#    print relerr

    # arrays of float
    vx = str2float(x)
    vy = str2float(y)
    vz = str2float(z)
    # number of bins
    nx = len(x)-1
    ny = len(y)-1
    nz = len(z)-1

    h = TH3F("h", "title;x;y", nx, array('f', vx), ny, array('f', vy), nz, array('f', vz))
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if (i,j,k) in val:
                    h.SetBinContent(i+1, j+1, k+1, float(val[(i,j,k)]))
                    h.SetBinError(i+1, j+1, k+1, float(relerr[(i,j,k)])*float(val[(i,j,k)]))
#                    h.SetBinError(i+1, j+1, k+1, float(relerr[(i,j,k)]))
    h.Print()

    out = TFile("out.root", "recreate")
    h.Write()
    out.Close()
        


if __name__ == "__main__":
    sys.exit(main())
