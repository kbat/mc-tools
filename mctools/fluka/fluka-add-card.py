#!/usr/bin/env python

import sys, re
import argparse
from mctools.fluka import line

def main():
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('card', type=str, help='card to add')
    parser.add_argument('inp', type=str, help='FLUKA input file name')
    parser.add_argument('-before', dest='before', type=str, help='input file line pattern which should directly follow the card being inserted', default="STOP")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

    args = parser.parse_args()

    with open(args.inp) as f:
        for l in f.readlines():
            l = l.strip()
            if re.search(f"\A{args.before}", l):
                line(*args.card.split())
            print(l)

if __name__ == "__main__":
    sys.exit(main())
