#! /usr/bin/env python -W all
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
    print("array: ", f)
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

    title, xtitle, ytitle, ztitle = "title", "x-title", "y-title", "z-title"

    # first make a list of all coordinates:
    for i, line in enumerate(f.readlines()):
        if re.search("^#", line):
            if i==0: title = line[1:].strip()
            elif i==1: xtitle = line[1:].strip()
            elif i==2: ytitle = line[1:].strip()
            elif i==3: ztitle = line[1:].strip()
            continue # skip comments
        w = line.split()

        if nline == 0:
            x.append(w[0])
            y.append(w[2])
            z.append(w[4])

            x.append(w[1])
            y.append(w[3])
            z.append(w[5])
        else: # now we do not care about being uniqe - fix it later
            x.append(w[1])
            y.append(w[3])
            z.append(w[5])

        nline = nline+1

    vx = sorted(str2float(list(set(x))))
#    vx =  [ x*-1 for x in vx[::-1]] + vx[1:]
#    print("\n!!! vx: added reversed values - used only for polar plots !!!\n")
    vy = sorted(str2float(list(set(y))))
    vz = sorted(str2float(list(set(z))))
#    vz =  [-600] + [ z*-1 for z in vz[::-1]] + vz[1:] + [600] # !!! add reversed values - used only for polar plots !!!
#    print("\n!!! vz: added reversed values - used only for polar plots !!!\n")

#        print(i, j, k)
#        val[(i,j,k)] = w[6]
#        relerr[(i,j,k)] = w[7]

    print("x: ", vx)
    print("y: ", vy)
    print("z: ", vz)

    nx = len(vx)-1
    ny = len(vy)-1
    nz = len(vz)-1
    
    print(nx, ny, nz)

    h = TH3F("neutron", "%s;%s;%s;%s" % (title, xtitle, ytitle, ztitle), nx, array('f', vx), ny, array('f', vy), nz, array('f', vz))


    f.seek(0)
    x0, y0, z0 = 0, 0, 0
    bin0 = 0
    for line in f.readlines():
        if re.search("^#", line): continue # skip comments
        w = line.split()
        
        x0 = (float(w[0]) + float(w[1]))/2.0
        y0 = (float(w[2]) + float(w[3]))/2.0
        z0 = (float(w[4]) + float(w[5]))/2.0

        bin0 = h.FindBin(x0, y0, z0)
        h.SetBinContent(bin0, float(w[6]))
        h.SetBinError(bin0, float(w[6])*float(w[7]))

    f.close()

#     # arrays of float
#     vx = str2float(x)
#     vy = str2float(y)
#     vz = str2float(z)
#     # number of bins

#     for i in range(nx):
#         for j in range(ny):
#             for k in range(nz):
#                 if (i,j,k) in val:
#                     h.SetBinContent(i+1, j+1, k+1, float(val[(i,j,k)]))
#                     h.SetBinError(i+1, j+1, k+1, float(relerr[(i,j,k)])*float(val[(i,j,k)]))
# #                    h.SetBinError(i+1, j+1, k+1, float(relerr[(i,j,k)]))
#     h.Print()

    out = TFile("out.root", "recreate")
    h.Write()
    out.Close()
        


if __name__ == "__main__":
    sys.exit(main())
