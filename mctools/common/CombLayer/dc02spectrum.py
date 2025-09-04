#!/usr/bin/env python

import sys
import argparse

def checkUnits(w):
    if w == ["eV", "ph/s/mr^2/0.1%", "F.Dens/mm^2", "ph/s/0.1%", "ph/s/eV", "ph/s", "kW", "m", "m", "rad", "rad"]:
        return True
    return False


def main():

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('dc0', type=str, help='Data file from the undulator team')
    parser.add_argument('-energy', type=int, default=0, help='energy column number (counting from zero)')
    parser.add_argument('-flux', type=int, default=3, help='flux column number (counting from zero)')
    parser.add_argument('-divx', type=int, default=9, help='x-divergence column number (counting from zero)')
    parser.add_argument('-divy', type=int, default=10, help='y-divergence column number (counting from zero)')
    parser.add_argument('-happ', type=float, help='last FM horizontal aperture [rad]', required=True)
    parser.add_argument('-vapp', type=float, help='last FM vertical aperture [rad]', required=True)
    parser.add_argument('-power', type=float, default=1200.0, help='beam power guess')

    args = parser.parse_args()

    data = False
    S = 0.0 # sum
    sumB = 0.0
    sumC = 0.0
    EPrev = 0.0

    with open(args.dc0) as f:
        for line in f:
            w = line.strip().split()
            if len(w) == 11 and checkUnits(w):
                data = True
                continue
            if data:
                energy = float(w[args.energy])
                flux = float(w[args.flux])
                S += flux
                EGap = energy - EPrev
                y = flux/(energy*0.001) # ev/ph/s/0.1%
                HSize = float(w[args.divx])
                VSize = float(w[args.divy])
                AScale = 1.0
                AScale *= args.happ/HSize if (HSize<args.happ) else 1.0;
                AScale *= args.vapp/VSize if (VSize<args.vapp) else 1.0;
                print(energy, y*EGap*AScale)

                sumB += energy*(y*EGap*AScale)
                sumC += y*EGap
                EPrev = energy

    Qe = 1.6021766208e-19
    print("Energy: ", sumB*Qe, file=sys.stderr)
    print("Sum: ", sumC*Qe, file=sys.stderr)
    print("Div: ", args.power/(sumC*Qe))


if __name__ == "__main__":
    sys.exit(main())
