#! /usr/bin/python
# Generates the MCNP vol cards
# https://github.com/kbat/mc-tools

import sys, textwrap, argparse

def main():
    """
    Generates the volume cards for MCNP input
    """

    parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-n', dest='N', type=int, help='Total number of cells in geometry', required=True)
    parser.add_argument('-vol', dest='vol', type=str, help='Dictionary of volumes. Format: "cell1 vol1 cell2 vol2". Example: "985 2.43687E+5 12 1.235"', required=True)

    args = parser.parse_args()

    a = args.vol.split()
    vols = dict(zip(map(int, a[0::2]), map(float, a[1::2])))

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

    s += " 1 %dr" % (args.N-c-3)

    print textwrap.fill(s, width=80, subsequent_indent=" "*7)

if __name__ == "__main__":
    sys.exit(main())
