#! /usr/bin/python -W all

from __future__ import print_function
import argparse, re
from sys import exit
from os import path

def getCombLayerObject(cell):
    """Return CombLayer object name based on its cell number"""

    fname = "ObjectRegister.txt"
    if not path.isfile(fname):
        fname = path.join("case001", fname);

    with open(fname) as f:
        for line in f.readlines():
            words = line.strip().split()
            if len(words) == 8:
                # print(words, words[6][1:], words[7][:-1])
                if words[0] != 'World':
                    cmin,cmax = map(int,(words[6][1:], words[7][:-1]))
                    if cell >= cmin and cell <= cmax:
                        print(line.strip())
                        return words[0]
                elif cell == int(words[7]): # World
                    print(line.strip())
                    return words[0]

    return "Not found"
    
                
def main():
    """
    Finds the CombLayer object name for the given MCNP(X) cell number
    based on the CombLayer-generated object register
    argument: cell - MCNP(X) cell number
    """
    parser = argparse.ArgumentParser(description=main.__doc__, epilog="")
    parser.add_argument('cell', type=int, help=__doc__)

    args = parser.parse_args()

    obj = getCombLayerObject(args.cell)
#    print(obj)
                

if __name__ == "__main__":
    exit(main())

