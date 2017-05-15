#! /usr/bin/python3 -W all
from __future__ import print_function
import sys, argparse, re
from os import path

def read(opt,dtl,start,end):
    """ Read the optics file """

    pmqBase = dtl + "PMQ"

    f = open(opt)
    val = 0.0
    iPMQ = int(1)
    found = False
    for l in f:
        if re.search(start,l):
            found = True
        if found:
            val = float(l.split()[4])*100.0
            var = "%s%dLength" % (pmqBase, iPMQ)
            print("Control.addVariable(\"%s\",%g);" % (var,val))
            # read the next line with GapLength
            l = f.readline()
            val = float(l.split()[4])*100.0
            var = "%s%dGapLength" % (pmqBase, iPMQ)
            print("Control.addVariable(\"%s\",%g);" % (var,val))

        if found:
            iPMQ += 1

        if found and re.search(end,l):
            stop = True
            break
            
    f.close()


    
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

    read(args.opt, args.dtl, args.start, args.end)

if __name__ == "__main__":
    sys.exit(main())

