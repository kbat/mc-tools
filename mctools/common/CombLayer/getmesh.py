#!/usr/bin/env python3

import sys
from argparse import ArgumentTypeError, ArgumentParser, RawTextHelpFormatter

def positive_float(x):
    try:
        x = float(x)
    except ValueError:
        raise ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x <= 0.0:
        raise ArgumentTypeError("%r not in range (0.0, inf)" % (x))
    return x

def check(name, n, nmin, nmax, width):
    """ Check if n > 0 """
    if width > nmax-nmin:
        raise ArgumentTypeError("{name} bin width is too large: {width} > {max}-{min}".
                                format(name=name, width=width, min=nmin, max=nmax))
    if n<=0.0:
        raise ArgumentTypeError("n{name}={n} <= 0: {name}min={min} {name}max={max} d{name}={width}".
                                format(n=n, name=name, min=nmin, max=nmax, width=width))


def main():
    """
    Print mesh definition in the CombLayer format
    Vec3D(xmin,ymin,zmin) Vec3D(xmax,ymax,zmax) nx ny dz
    """

    axes = ('x', 'y', 'z')

    parser = ArgumentParser(description=main.__doc__,
                            formatter_class=RawTextHelpFormatter,
                            epilog="Homepage: https://github.com/kbat/mc-tools")
    for a in axes:
        parser.add_argument("%smin"%a, type=float, help="%smin"%a)
    for a in axes:
        parser.add_argument("%smax"%a, type=float, help="%smax"%a)
    for a in axes:
        parser.add_argument("d%s"%a, type=positive_float, help="%s bin width"%a)

    args = parser.parse_args()

    nx = round((args.xmax - args.xmin) / args.dx)
    ny = round((args.ymax - args.ymin) / args.dy)
    nz = round((args.zmax - args.zmin) / args.dz)

    check("x", nx, args.xmin, args.xmax, args.dx)
    check("y", ny, args.ymin, args.ymax, args.dy)
    check("z", nz, args.zmin, args.zmax, args.dz)

    print("Vec3D({},{},{}) Vec3D({},{},{}) {} {} {}".format(
        args.xmin, args.ymin, args.zmin, args.xmax, args.ymax, args.zmax,
        nx, ny, nz))


if __name__ == "__main__":
    sys.exit(main())
