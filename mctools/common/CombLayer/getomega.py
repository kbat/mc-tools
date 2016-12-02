#! /usr/bin/python -W all

from comblayer import getOmega, getPar
import argparse, sys

def main():
    parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='include input file and F5 collimator names in the output')
    parser.add_argument('-inv', '--inverse', action='store_true', default=False, dest='inv', help='If set, prints the inverse value: 1/omega (to be used with the FMn cards)')
    parser.add_argument('inp', type=str, help='Comblayer-generated MCNP input file name', default="inp")
    parser.add_argument('col', type=str, help='F5 collimator name', default="F5Cold")
    args = parser.parse_args()

    omega = getOmega(args.inp, args.col)
    if args.inv:
        omega = 1.0/omega
    if args.verbose:
        print args.inp, args.col, omega, "sr"
    else:
        print omega

if __name__=="__main__":
    sys.exit(main())
