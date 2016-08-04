#! /usr/bin/python -W all

import argparse, re
from sys import exit
from os import path

def getCombLayerSurf(mcnpsurf):
    """Return CombLayer surf number"""

    clsurf = 0 #  CombLayer surf number
    
    fname = "Renumber.txt"
    if not path.isfile(fname):
        fname = path.join("case001", fname)
    f = open(fname)
        
    for line in f.readlines():
        if re.search("^Surf Change", line):
            words = line.strip().split()
            if int(words[-1]) == int(mcnpsurf):
                print words
                clsurf = int(words[1].split(":")[1])
    f.close()
    return clsurf

                
def main():
    """
    Finds a CombLayer surf number
    """
    parser = argparse.ArgumentParser(description=main.__doc__, epilog="")
    parser.add_argument('surf', type=int, help='MCNP(X) surface number to find')

    arguments = parser.parse_args()
    mcnpsurf = arguments.surf

    clsurf = getCombLayerSurf(mcnpsurf)
#    obj = getCombLayerObject(clsurf)
    print clsurf
                

if __name__ == "__main__":
    exit(main())

