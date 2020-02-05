#! /usr/bin/python -W all

import argparse, re
from sys import exit
from os import path

def getCombLayerObject(cell):
    """Return CombLayer object name based on its cell number"""

    fname = "ObjectRegister.txt"
    if not path.isfile(fname):
        fname = path.join("case001", fname);

    if not path.isfile(fname):
        print("ObjectRegister not found")
        return None

    with open(fname) as f:
        for line in f.readlines():
            words = line.strip().split()
            pos = words.index('::')
            cells = words[pos+1:]
            if words[0] != 'World':
                if len(cells) == 2: # min/max range is given
                    cmin,cmax = map(int,(cells[0][1:], cells[1][:-1]))
                    if cell >= cmin and cell <= cmax:
                        print(line.strip())
                        return words[0]
            # if l in [7,8]:
            #     if words[0] != 'World':
            #         cmin,cmax = map(int,(words[l-2][1:], words[l-1][:-1]))
            #         if cell >= cmin and cell <= cmax:
            #             print(line.strip())
            #             return words[0]
            #     elif cell == int(words[l-1]): # World
            #         print(line.strip())
            #         return words[0]

    print("Object not found")
    return None
    
                
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

    if obj is None:
        exit(1)

if __name__ == "__main__":
    exit(main())

