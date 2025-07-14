#!/usr/bin/env python

import sys, re
import argparse
from mctools.fluka import line

import numpy as np
from typing import Tuple, List
#from contextlib import redirect_stdout

def split_mesh(
    lower_left: Tuple[float, float, float],
    upper_right: Tuple[float, float, float],
    bins: Tuple[int, int, int],
    num_submeshes: int
) -> List[dict]:
    """
    Splits a 3D Cartesian mesh into submeshes along the axis with the most bins.

    Args:
        lower_left: (x0, y0, z0) lower-left corner of the full mesh.
        upper_right: (x1, y1, z1) upper-right corner of the full mesh.
        bins: (nx, ny, nz) number of bins along x, y, z axes.
        num_submeshes: number of submeshes to create along the axis with max bins.

    Returns:
        A list of dictionaries, each with:
            - 'lower_left': (x0, y0, z0)
            - 'upper_right': (x1, y1, z1)
            - 'bins': (nx, ny, nz)
    """

    lower_left = np.array(lower_left, dtype=float)
    upper_right = np.array(upper_right, dtype=float)
    bins = np.array(bins, dtype=int)

    axis = np.argmax(bins)
    total_bins = bins[axis]

    if total_bins < num_submeshes:
        raise ValueError("Number of submeshes exceeds number of bins on the splitting axis.")

    # Compute bin width and mesh width along the split axis
    bin_width = (upper_right[axis] - lower_left[axis]) / total_bins

    submeshes = []

    for i in range(num_submeshes):
        sub_lower = lower_left.copy()
        sub_upper = upper_right.copy()
        sub_bins = bins.copy()

        # Compute bin indices and physical coordinates for the submesh
        start_bin = i * total_bins // num_submeshes
        end_bin = (i + 1) * total_bins // num_submeshes
        sub_bins[axis] = end_bin - start_bin

        sub_lower[axis] = lower_left[axis] + start_bin * bin_width
        sub_upper[axis] = lower_left[axis] + end_bin * bin_width

        submeshes.append({
            'lower_left': tuple(sub_lower),
            'upper_right': tuple(sub_upper),
            'bins': tuple(sub_bins)
        })

    return submeshes


def main():
    """
    A script to speedup FLUKA geometry check with its GEOEND card.

    Split the geometry check mesh defined in the GEOEND card between several input files to run in parallel.
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('inp', type=str, help='FLUKA input file with geometry check mesh defined')
    parser.add_argument('-j', type=int, help='number of input files to generate', required=True)

    args = parser.parse_args()

    first = True

    forig = open(args.inp)

    for l in forig.readlines():
        l = l.strip()
        if re.search(f"\AGEOEND", l):
            if first:
                l = l.strip().removesuffix("DEBUG")
                card, xmax, ymax, zmax, xmin, ymin, zmin = l.split()
                print(card, xmax, ymax, zmax, xmin, ymin, zmin)
                first = False
            else:
                l = l.strip().removesuffix("&")
                card, nx, ny, nz = l.split()
                print(card, nx, ny, nz)

 #   assert max(float(nx), float(ny), float(nz)) > args.j, "Max number of bins is below number of input files required"

    # corners
    lower_left = (xmin, ymin, zmin)
    upper_right = (xmax, ymax, zmax)
    bins = tuple(map(float, (nx, ny, nz)))

    result = split_mesh(lower_left, upper_right, bins, args.j)

    prefix = args.inp.removesuffix(".inp")
    print(f"{prefix=}")

    for idx, sub in enumerate(result):
        # print(f"Submesh {idx + 1}:")
        # print(f"  Lower-left:  {sub['lower_left']}")
        # print(f"  Upper-right: {sub['upper_right']}")
        # print(f"  Bins:        {sub['bins']}")

#        xmin, ymin, zmin = sub['lower_left']

        inp = f"{prefix}{idx+1}.inp"
        print(inp)
        first = True
        with open(inp, "w") as f:
            forig.seek(0)
            for l in forig.readlines():
                if not re.search(f"\AGEOEND", l):
                    print(l.strip(), file=f)
                else:
                    if first:
                        line("GEOEND", *sub['upper_right'], *sub['lower_left'], "DEBUG", f)
                        first = False
                    else:
                        line("GEOEND", *sub['bins'], "", "", "", "&", f)

    forig.close()

if __name__ == "__main__":
    sys.exit(main())
