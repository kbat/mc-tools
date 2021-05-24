#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import sys, argparse
from os import path
from mctools.mcnp.mctal import MCTAL
import numpy as np
sys.path.insert(1, '@python2dir@')

def getEdges(axis, n):
        if len(axis):
                return ("{:13.5e} {:13.5e}".format(axis[n-1],axis[n]))
        else:
                return ("{:13.5e} {:13.5e}".format(0.0, 0.0)) # artificial values if axis not divided


def main():
        """
        MCTAL to TXT converter.
        Converts \033[1mmctal\033[0m files produced by MCNP(X) into a text file.
        """
        parser = argparse.ArgumentParser(description=main.__doc__,
                                         epilog="Homepage: https://github.com/kbat/mc-tools")
        parser.add_argument('mctal', type=str, help='mctal file name')
        parser.add_argument('txt', type=str, nargs='?', help='output txt file name', default="")
        parser.add_argument('-bins', '--print-bins', action='store_true', default=False, dest='bins', help='print bin numbers')
        parser.add_argument('-edges', '--print-edges', action='store_true', default=False, dest='edges', help='print bin edges')
        parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

        arguments = parser.parse_args()

        if not (arguments.bins ^ arguments.edges):
                parser.error("Either -bins or -edges must be specified")

        if not path.isfile(arguments.mctal):
                print(f"mctal2txt: File {arguments.mctal} does not exist.", file=sys.stderr)
                return 1

        m = MCTAL(arguments.mctal,arguments.verbose)

        T = m.Read()

        if m.thereAreNaNs:
                print(" \033[1;30mOne or more tallies contain NaN values. Conversion will succeed anyway.\033[0m", file=sys.stderr)

        if arguments.txt == "":
                txtFileName = "%s%s" % (arguments.mctal,".txt")
        else:
                txtFileName = arguments.txt

        txtFile = open(txtFileName, "w")

        if arguments.verbose:
                print("\n\033[1;34m[Converting...]\033[0m")

        if arguments.bins:
                print("#   f     d     u     s     m     c     e     t     i     j     k           value   rel.error", file=txtFile)
        elif arguments.edges:
                print("# {:>11s} ".format("fmin") + (23*"{:>13s} ").
                      format("fmax","dmin","dmax","umin","umax","smin","smax","mmin","mmax","cmin","cmax","emin","emax","tmin","tmax","imin","imax","jmin","jmax","kmin","kmax","value","rel.error"),
                      file=txtFile)

        for tally in T:
                tallyLetter = "f"
                if tally.radiograph:
                        tallyLetter = tally.getDetectorType(True) # Here the argument set to True enables the short version of the tally type
                if tally.mesh:
                        tallyLetter = tally.getDetectorType(True)

                # name and tally comment:
                print(f"# {tallyLetter}{tally.tallyNumber} {' '.join(tally.tallyComment.tolist()).strip()}", file=txtFile)

                nCells  = tally.getNbins("f",False)
                fAxis   = tally.getAxis("f")
                nCora   = tally.getNbins("i",False) # Is set to 1 even when mesh tallies are not present
                iAxis   = tally.getAxis("i")
                nCorb   = tally.getNbins("j",False) # Is set to 1 even when mesh tallies are not present
                jAxis   = tally.getAxis("j")
                nCorc   = tally.getNbins("k",False) # Is set to 1 even when mesh tallies are not present
                kAxis   = tally.getAxis("k")
                nDir    = tally.getNbins("d",False)
                dAxis   = tally.getAxis("d")
                usrAxis = tally.getAxis("u")
                nUsr    = tally.getNbins("u",False)
                segAxis = tally.getAxis("s")
                nSeg    = tally.getNbins("s",False)
                nMul    = tally.getNbins("m",False)
                mAxis   = tally.getAxis("m")
                cosAxis = tally.getAxis("c")
                nCos    = tally.getNbins("c",False)
                ergAxis = tally.getAxis("e")
                nErg    = tally.getNbins("e",False)
                timAxis = tally.getAxis("t")
                nTim    = tally.getNbins("t",False)

                for f in range(nCells):
                        for d in range(nDir):
                                for u in range(nUsr):
                                        for s in range(nSeg):
                                                for m in range(nMul):
                                                        for c in range(nCos):
                                                                for e in range(nErg):
                                                                        for t in range(nTim):
                                                                                for k in range(nCorc):
                                                                                        for j in range(nCorb):
                                                                                                for i in range(nCora):
                                                                                                        val = tally.getValue(f,d,u,s,m,c,e,t,i,j,k,0)
                                                                                                        err = tally.getValue(f,d,u,s,m,c,e,t,i,j,k,1)
                                                                                                        if arguments.bins:
                                                                                                                print((11*"{:5d} "+2*"{:13.5e} ").format(f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1,val,err),
                                                                                                                      file=txtFile)
                                                                                                        elif arguments.edges:
                                                                                                                print((11*"{} "+2*"{:13.5e} ").
                                                                                                                      format(getEdges(fAxis,f+1),getEdges(dAxis,d+1),
                                                                                                                             getEdges(usrAxis,u+1),getEdges(segAxis,s+1),getEdges(mAxis,m+1),
                                                                                                                             getEdges(cosAxis,c+1),getEdges(ergAxis,e+1),getEdges(timAxis,t+1),
                                                                                                                             getEdges(iAxis,i+1),getEdges(jAxis,j+1),getEdges(kAxis,k+1),
                                                                                                                             val,err),
                                                                                                                      file=txtFile)

                if arguments.verbose:
                        print(f" \033[33mTally {tally.tallyNumber:5d} saved\033[0m")

        print(f"\n\033[1;34mASCII file saved to:\033[1;32m {txtFileName}\033[0m\n")
        txtFile.close()


if __name__ == "__main__":
        sys.exit(main())
