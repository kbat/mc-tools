#!/usr/bin/env python3

import sys, argparse
from os import path
import numpy as np
from mctools import fluka
from mctools.fluka.flair import Data

def getEdges(xmin, xmax, nbins):
    """Return bin edges given the axis min, max and number of equidistant bins

    """

    dx = (xmax - xmin)/nbins
    x = np.arange(xmin, xmax, dx).tolist()
    x.append(xmax)
    return x

def main():
    """Convert usbsuw output into text.

       Format: min and max edges of the bin along each axis followed by the value and its relative error.
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('usbsuw', type=str, help='usbsuw binary output')
    parser.add_argument('out', type=str, nargs='?', help='output ASCII file name', default="")
    parser.add_argument('-f', action='store_true', default=False, dest='force', help='overwrite output file')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

    args = parser.parse_args()

    if not path.isfile(args.usbsuw):
        print("usbsuw2txt: File %s does not exist." % args.usbsuw, file=sys.stderr)
        return 1

    if args.out == "":
        outFileName = "%s%s" % (args.usbsuw,".txt")
    else:
        outFileName = args.out

    if not args.force and path.isfile(outFileName):
        print("usbsuw2txt: File %s already exists. Use '-f' to overwrite." % outFileName, file=sys.stderr)
        return 1

    b = Data.Usrbin()
    b.readHeader(args.usbsuw)

    ND = len(b.detector)

    if args.verbose:
        b.sayHeader()
        print("\n%d tallies found:" % ND)
        for i in range(ND):
            b.say(i)
            print("")

    with open(outFileName, "w") as fout:
        for i in range(ND):
            val = Data.unpackArray(b.readData(i))
            err = Data.unpackArray(b.readStat(i))
            det = b.detector[i]

            title = fluka.particle.get(det.score, "unknown")
            axes = ""
            if det.type % 10 in (0, 3, 4, 5, 6): # cartesian
                axes = "xmin xmax ymin ymax zmin zmax value relerr"
            elif det.type % 10 in (1, 7):
                axes = "rmin        rmax         phimin       phimax       zmin         zmax         value       relerr"

            x = getEdges(det.xlow, det.xhigh, det.nx)
            y = getEdges(det.ylow, det.yhigh, det.ny)
            z = getEdges(det.zlow, det.zhigh, det.nz)

            print(f"# {title}", file=fout)
            print(f"# {axes}",  file=fout)

            for i in range(det.nx):
                for j in range(det.ny):
                    for k in range(det.nz):
                        gbin = i + j * det.nx + k * det.nx * det.ny
                        print(f"{x[i]:>12.5e} {x[i+1]:>12.5e} {y[j]:>12.5e} {y[j+1]:>12.5e} {z[k]:>12.5e} {z[k+1]:>12.5e} {val[gbin]:>12.5e} {err[gbin]:>.4f}", file=fout)

if __name__=="__main__":
    sys.exit(main())
