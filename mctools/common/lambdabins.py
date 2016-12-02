#! /usr/bin/python

import sys, argparse
from string import strip
from mctools import L2E, E2L
import textwrap

def LambdaBins(nbins, lmin, lmax, edgesE):
    """
    Return array of energy boundaries in order to make equal binning in wavelength.
    If edgesE array is not empty, overwrites some of the bin edges.
    """
    l = [] # lambda bins
    e = [] # energy bins
    dl = (lmax-lmin)/nbins  # lambda bin width
    
    for i in range(nbins+1): l.append(lmin+i*dl)

    for i in range(nbins+1):
        e.append(L2E(l[nbins-i]))

    # insert edges:
    for i in range(nbins+1):
        for edge in edgesE:
            if i==0 and e[i]>edge:
                e[i] = edge
            elif i==nbins and e[i]<edge:
                e[i] = edge
            elif e[i]<edge and e[i+1]>edge:
                e[i] = edge
        
    return e

def main():
    """
    Print array of energy boundaries in order to make equal binning in wavelength
    """

    parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: https://github.com/kbat/mc-tools/mc-tools", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('nbins', type=int, help='Number of lambda bins')
    parser.add_argument('lmin', type=float, help='lambda min')
    parser.add_argument('lmax', type=float, help='lambda max')
    parser.add_argument('-w', type=int, dest='width', help='Maximal column width (put 0 for inf value)', required=False, default=0)
    parser.add_argument('-edgesE', type=str, dest='edgesE', help='Comma-separated list of energies [MeV] to be explicitly at the edges', required=False, default="")

    args = parser.parse_args()

    if args.edgesE:
        edgesE = map(float, map(strip, args.edgesE.split(',')))
    else:
        edgesE = []

    if args.width:
        print textwrap.fill(" ".join(map(str, LambdaBins(args.nbins, args.lmin, args.lmax, edgesE))), width=80, subsequent_indent=" "*7)
    else:
        print " ".join(map(str, LambdaBins(args.nbins, args.lmin, args.lmax, edgesE)))

if __name__=="__main__":
    sys.exit(main())
