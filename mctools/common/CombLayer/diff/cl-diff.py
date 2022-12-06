#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import sys, argparse
import numpy as np
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """
    A tool to compare two CombLayer geometries
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('exe', type=str, nargs=2, help='Paths to two CombLayer executable to compare')
    parser.add_argument('opts', type=str, help='Options to build geometry')
    parser.add_argument("-vtkopts", type=str, dest='vtkopts', help='Options to generate VTK', default="-vtk -vtkType density -vtkMesh free ", required=False)
    parser.add_argument("-xrange", type=float, dest='xrange', nargs=2, help='x-axis range', default=None, required=True)
    parser.add_argument("-yrange", type=float, dest='yrange', nargs=2, help='y-axis range', default=None, required=True)
    parser.add_argument("-zrange", type=float, dest='zrange', nargs=2, help='z-axis range', default=None, required=True)
    parser.add_argument("-nz", type=int, help='nz', default=None, required=True)
    parser.add_argument("-nx", type=int, help='nx', default=None, required=True)
    parser.add_argument("-ny", type=int, help='ny', default=None, required=True)
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

    args = parser.parse_args()

    zstep = (args.zrange[1]-args.zrange[0])/args.nz

    zindex=0
    for z in np.arange(args.zrange[0], args.zrange[1], zstep):
        mesh = f"\'Vec3D({args.xrange[0]},{args.yrange[0]},{z})\' \'Vec3D({args.xrange[1]},{args.yrange[1]},{z+zstep})\' {args.nx} {args.ny} 1"
        exeindex = 0
        for exe in args.exe:
            vtk = f"exe{exeindex}_z{zindex}.vtk"
            cmd=f"{exe} {args.opts} {args.vtkopts} {mesh} {vtk} && vtk2root -type TH3F {vtk} && rm -f {vtk} && "
            print(cmd, end=" ")
            exeindex += 1
        root1 = f"exe0_z{zindex}.root"
        root2 = f"exe1_z{zindex}.root"
#        print(f"$MCTOOLS/mctools/common/CombLayer/diff/hist-diff.py {root1} h3 {root2} h3 > hist-diff{zindex}.log") # " && rm -f {root1} {root2}"
        print(f"$MCTOOLS/mctools/common/CombLayer/diff/hist-diff.py {root1} h3 {root2} h3 > /dev/null") # > hist-diff{zindex}.log") # " && rm -f {root1} {root2}"
        zindex += 1

if __name__ == "__main__":
    exit(main())
