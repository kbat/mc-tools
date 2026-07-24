#!/usr/bin/env python

import sys, re
import argparse
import fileinput
from mctools.fluka import line

def main():
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('inp', type=str, help='FLUKA input file name')
    parser.add_argument('-card', type=str, nargs='+', required=True, help='card(s) to add. Each card corresponds to a single line of the FLUKA input and must contain 8 words. Empty WHATs are marked with a dash (-) symbol.')
    parser.add_argument('-before', dest='before', type=str, help='input file line pattern which should directly follow the card(s) being inserted', default="STOP")
    parser.add_argument('-replace', action='store_true', default=False, dest='replace', help='replace the BEFORE pattern with the given card(s)')

    args = parser.parse_args()

    for l in fileinput.input(args.inp, inplace=True, backup='.bak'):
        l = l.strip()
        if re.search(f"\A{args.before}", l):
            for card in args.card:
                line(*card.split(), f=sys.stdout)
            if not args.replace:
                print(l)
        else:
            print(l)

if __name__ == "__main__":
    sys.exit(main())
