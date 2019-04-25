#! /usr/bin/python -W all
# $Id$
# $URL$

from __future__ import print_function, absolute_import
import sys
from .fluka import USXSUW

def main():
    """Converts usxsuw binary output to ASCII"""

    if len(sys.argv) != 2:
        print("Usage: usxsuw2txt.py usxsuw_file")
        sys.exit(1)

    fin_name = sys.argv[1]
    fout_name = fin_name + ".txt"

    u = USXSUW(fin_name)
    u.Read()
    u.Print()

if __name__ == "__main__":
        sys.exit(main())
