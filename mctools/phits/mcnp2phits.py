#!/usr/bin/env python

import sys, re, argparse

R = re.compile("(?P<number>\d+)R.*")

def main():
    """
    mcnp2phits - converts *some* parts of MCNP deck into PHITS format
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument("mcnp", type=str,
                        help="MCNP file name")
    parser.add_argument("phits", type=str,
                        help="PHITS file name")

    args = parser.parse_args()

    phits = open(args.phits, 'w')
    mcnp = open(args.mcnp, 'r')

    for line in mcnp.readlines():
        words = line.strip().split()
        for i,w in enumerate(words):
            s = R.search(w)
            if not s:
                print(w,end=" ")
            else:
                print("%s "%words[i-1]*int(s.group("number")),end=" ")
        print()


if __name__ == "__main__":
    sys.exit(main())
