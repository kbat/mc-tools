#! /usr/bin/python -W all

import sys, re, string
from array import array
from mctal import MCTAL

def main():
    """
    readmctal - An example how to read mctal files.
    Usage: readmctal mctal
    mctal.Read() reads tallies from the 'mctal' file, and returns array with these tallies (as objects of the 'Tally' class).
    See the source code of mctal.py for available methods of the 'Tally' class.

    Homepage: http://code.google.com/p/mc-tools
    """

    fname_in = sys.argv[1]
    if len(sys.argv) == 3:
        fname_out = sys.argv[2]
    else:
        fname_out = re.sub("\....$", ".root", fname_in)
    if fname_in == fname_out:
        fname_out = fname_in + ".root"

    mctal = MCTAL(fname_in)
    mctal.Read()
#    mctal.GetTally(12).Print()

if __name__ == '__main__':
    sys.exit(main())
