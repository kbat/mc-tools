#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import sys, argparse
from os import path
from mctools.mcnp.mctal import MCTAL
import numpy as np
sys.path.insert(1, '@python2dir@')

def main():
        """
        MCTAL to TXT converter.
        Converts \033[1mmctal\033[0m files produced by MCNP(X) into a text file.
        """
        parser = argparse.ArgumentParser(description=main.__doc__,
                                         epilog="Homepage: https://github.com/kbat/mc-tools")
        parser.add_argument('mctal', type=str, help='mctal file name')
        parser.add_argument('txt', type=str, nargs='?', help='output txt file name', default="")
        parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

        arguments = parser.parse_args()

        if not path.isfile(arguments.mctal):
                print("mctal2txt: File %s does not exist." % arguments.mctal, file=sys.stderr)
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

        print("#   f     d     u     s     m     c     e     t     i     j     k           val     rel.error", file=txtFile)
        for tally in T:
                tallyLetter = "f"
                if tally.radiograph:
                        tallyLetter = tally.getDetectorType(True) # Here the argument set to True enables the short version of the tally type
                if tally.mesh:
                        tallyLetter = tally.getDetectorType(True)

                # name and tally comment:
                print("# %s%d" % (tallyLetter, tally.tallyNumber) + ' '.join(tally.tallyComment.tolist()).strip(), file=txtFile)

                nCells  = tally.getNbins("f",False)
                nCora   = tally.getNbins("i",False) # Is set to 1 even when mesh tallies are not present
                nCorb   = tally.getNbins("j",False) # Is set to 1 even when mesh tallies are not present
                nCorc   = tally.getNbins("k",False) # Is set to 1 even when mesh tallies are not present
                nDir    = tally.getNbins("d",False)
                usrAxis = tally.getAxis("u")
                nUsr    = tally.getNbins("u",False)
                segAxis = tally.getAxis("s")
                nSeg    = tally.getNbins("s",False)
                nMul    = tally.getNbins("m",False)
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
                                                                                                        print("%5d %5d %5d %5d %5d %5d %5d %5d %5d %5d %5d %13.5e %13.5e" % (f+1,d+1,u+1,s+1,m+1,c+1,e+1,t+1,i+1,j+1,k+1,val,err), file=txtFile)

                if arguments.verbose:
                        print(" \033[33mTally %5d saved\033[0m" % (tally.tallyNumber))

        print("\n\033[1;34mASCII file saved to:\033[1;32m %s\033[0m\n" % (txtFileName))
        txtFile.close()


if __name__ == "__main__":
        sys.exit(main())
