#! /usr/bin/python3 -W all
from __future__ import print_function
import sys, argparse, re
from os import path

def main():
    """ Convert optics file into CombLayer variables """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('opt', type=str, help='optics file name')
    parser.add_argument('-dtl', type=str, help='DTL name (e.g. LinacDTL1)', required=True)
    parser.add_argument('-start', type=str, help='first record (e.g. quad1213)', required=True)
    parser.add_argument('-end', type=str, help='last record (e.g. D204)')

    args = parser.parse_args()

    if not path.isfile(args.opt):
        print("optics2var: Can't open %s" % args.opt, file=sys.stderr)
        return 1

    pmqBase = args.dtl + "PMQ"

    f = open(args.opt)
    val = 0.0
    iPMQ = int(1)
    found = False
    for l in f:
        if re.search(args.start,l):
            found = True
        if found:
            val = float(l.split()[4])*100.0
            var = "Control.addVariable(\"%s%dLength\",%g);" % (pmqBase, iPMQ, val)
            print(var)
            # read the next line with GapLength
            l = f.readline()
            val = float(l.split()[4])*100.0
            var = "Control.addVariable(\"%s%dGapLength\"%g);" % (pmqBase,iPMQ,val)
            print(var)

        if found:
            iPMQ += 1

        if found and re.search(args.end,l):
            stop = True
            break
            
    f.close()

if __name__ == "__main__":
    sys.exit(main())

