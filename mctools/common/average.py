#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import argparse, tempfile
import logging
import math
from sys import exit
import os
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """ Merge and average ROOT files
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")

    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite',
                        help='overwrite the target output ROOT file')
    parser.add_argument('-o', dest='target', type=str, help='target file')
    parser.add_argument('sources', type=str, help='source files', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done   ')

    args = parser.parse_args()

    if not args.overwrite and os.path.exists(args.target):
        logging.critical("File %s exists. Use -f to overwrite" % args.target)
        exit(1)

    sources = args.sources

    for f in sources:
        if not os.path.exists(f):
            print(f"WARNING: {f} does not exits - skipping")
            sources.remove(f)

    if args.verbose:
        print(sources)

    n = len(sources)

    with tempfile.TemporaryDirectory() as tmp:
        unscaled = os.path.join(tmp, "unscaled.root")
        print(unscaled)
        cmd = "hadd %s %s" % (unscaled, " ".join(sources))
        os.system(cmd)
        cmd = f"scale -n {n} {unscaled} -o {args.target}"
        os.system(cmd)

if __name__ == "__main__":
    exit(main())
