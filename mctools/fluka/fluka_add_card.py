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
    parser.add_argument('-before', dest='before', type=str, help='input file line pattern which should directly follow the card(s) being inserted (literal string by default, see -regex)', default="STOP")
    parser.add_argument('-regex', action='store_true', default=False, dest='regex', help='treat BEFORE as a regular expression instead of a literal string')
    parser.add_argument('-replace', action='store_true', default=False, dest='replace', help='replace the BEFORE pattern with the given card(s)')

    args = parser.parse_args()

    for card in args.card:
        n = len(card.split())
        if n != 8:
            parser.error(f"'{card}': card must contain 8 words, got {n}")

    pattern = args.before if args.regex else re.escape(args.before)

    nmatches = 0
    for l in fileinput.input(args.inp, inplace=True, backup='.bak'):
        l = l.strip()
        if re.search(f"\A{pattern}", l):
            nmatches += 1
            for card in args.card:
                line(*card.split(), f=sys.stdout)
            if not args.replace:
                print(l)
        else:
            print(l)

    if nmatches == 0:
        print(f"{sys.argv[0]}: warning: pattern '{args.before}' not found in {args.inp} -- no card(s) were added", file=sys.stderr)
    else:
        action = "Replaced" if args.replace else "Added"
        print(f"{action} {len(args.card)} card(s) before {nmatches} line(s) matching '{args.before}' in {args.inp}", file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
