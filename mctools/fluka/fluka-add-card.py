#!/usr/bin/env python

import sys, re
import argparse
from mctools.fluka import line

def main():
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('inp', type=str, help='FLUKA input file name')
    parser.add_argument('-card', type=str, nargs='+', help='card(s) to add. Each card corresponds to a single line of the FLUKA input and must contain 8 words. Empty WHATs are marked with a dash (-) symbol.')
    parser.add_argument('-before', dest='before', type=str, help='input file line pattern which should directly follow the card(s) being inserted', default="STOP")

    args = parser.parse_args()

    with open(args.inp) as f:
        for l in f.readlines():
            l = l.strip()
            if re.search(f"\A{args.before}", l):
                for card in args.card:
                    n = len(card.split())
                    assert n == 8, f"{card}: incorrect card length of {n}"
                    line(*card.split())
            print(l)

if __name__ == "__main__":
    sys.exit(main())
