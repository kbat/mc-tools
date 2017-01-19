#! /usr/bin/python
# Generates the MCNP vol cards
# https://github.com/kbat/mc-tools

import sys, textwrap, argparse

def main():
# total number of cells:
    N = 3019

    vols = {}
    vols[985] = 2.43687E+5
    vols[1780] = 7.27140E+04
    vols[1776] = 3.69161E+05
    vols[6] = 1.96631E+04
    vols[8] = 1.97065E+04
    vols[10] = 1.95215E+04
    vols[12] = 1.64029E+04
    vols[14] = 1.64034E+04
    vols[16] = 1.65427E+04
    vols[476] = 4.36069E+01
    vols[512] = 3.72525E+04
    vols[513] = 3.74750E+04
    #print vols


    s = "vol"
    c0 = 0 # number of previous cell in the 'vols' dict
    dist = 0 # distance from the current cell to the previous one in the 'vols' dict
    for i,c in enumerate(sorted(vols.iterkeys())):
        v = vols[c]
        dist=c-c0
    
        #    print "%d:" % i, c,v, dist
    
        if dist==1:
            s += " %g " % v
        if dist==2:
            s += " 1 %g " % (v)
        elif dist>2:
            s += " 1 %dr %g " % (dist-2, v)
        c0 = c

    s += " 1 %dr" % (N-c-3)

    print textwrap.fill(s, width=80, subsequent_indent=" "*7)

if __name__ == "__main__":
    sys.exit(main())
