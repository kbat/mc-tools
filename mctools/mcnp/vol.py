#!/usr/bin/env python3
# Generate volume cards for MCNP input
# https://github.com/kbat/mc-tools

import sys, textwrap, argparse

def main():
    """Generate volume cards for MCNP input

    The same script can be used for other similar cards, i.e. inp, pd, dxc...
    Typical use: python $MCTOOLS/mctools/mcnp/vol.py -card dxc -ntotal 100 -values "25 1 26 1 30 1" -default 0
    """

    parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-ntotal', dest='N', type=int, help='Total number of cells/surfaces in geometry (depending on the card type)', required=True)
    parser.add_argument('-values', dest='values', type=str, help='Dictionary of values. Format: "cell1 value1 cell2 value2". Example: "985 2.43687E+5 12 1.235"', required=True)
    parser.add_argument('-default', dest='default', type=str, help="Default value for non-specified cells. Either a float value or 'j' can be entered", default="1.0")
    parser.add_argument('-card', dest='card', type=str, help='Card name', default="vol")

    args = parser.parse_args()

    a = args.values.split()
    if len(a) % 2:
        print("Error: length of values must be even", a)
        sys.exit(1)

    values = dict(list(zip(list(map(int, a[0::2])), list(map(float, a[1::2])))))
    cells = sorted(values.keys())

    cell_max = cells[-1] # max cell/surface number from the values array
    if args.N < cell_max:
        print(f"Error: values contain cell/surface number larger than ntotal: {cell_max} > {args.N}")
        sys.exit(2)

    if cells[0] <= 0:
        print(f"Error: first cell must be >= 1: {cells[0]}")
        sys.exit(3)

    s = args.card
    c0 = 0 # number of previous cell in the 'values' dict
    dist = 0 # distance from the current cell to the previous one in the 'values' dict
    for i,cell in enumerate(cells):
        v = values[cell]
        dist=cell-c0

        if dist==1:
            s += " %g" % v
        elif dist==2:
            s += " %s %g" % (args.default, v)
        elif dist>2:
            if args.default=='j':
                s += " %dj %g" % (dist-1, v)
            else:
                s += " %s %dr %g" % (args.default, dist-2, v)

        c0 = cell

    nleft = args.N-cell_max # number of cells left
    if nleft==1:
        s+= " %s" % (args.default)
    elif nleft>1:
        if args.default=='j':
            s += " %dj" % (nleft)
        else:
            s += " %s %dr" % (args.default, nleft-1)

    print(textwrap.fill(s, width=80, subsequent_indent=" "*7))

if __name__ == "__main__":
    sys.exit(main())
