#! /usr/bin/python -W all

import argparse, re
from sys import exit
from os import path

def getCombLayerCell(mcnpcell):
    """Return CombLayer cell number"""

    clcell = 0 #  CombLayer cell number
    
    fname = "Renumber.txt"
    if not path.isfile(fname):
        fname = path.join("case001", fname)
    f = open(fname)
        
    for line in f.readlines():
        if re.search("^Cell Changed", line):
            words = line.strip().split()
#            print words
            if int(words[3]) == int(mcnpcell):
                print words
                clcell = int(words[2][1:])
    f.close()
    return clcell

def getCombLayerObject(clcell):
    """Return CombLayer object name based on its cell number"""
    obj = "Not found"
    c = clcell - (clcell % 1000)
    fname = "ObjectRegister.txt"
    if not path.isfile(fname):
        fname = path.join("case001", fname);
    f = open(fname)
    for line in f.readlines():
        words = line.strip().split()
        if (int(words[1]) == c):
            print words
            obj = words[0]
    f.close()
    return obj
    
                
def main():
    """
    Finds a CombLayer cell number
    """
    parser = argparse.ArgumentParser(description=main.__doc__, epilog="")
    parser.add_argument('cell', type=int, help='MCNP(X) cell number to find')

    arguments = parser.parse_args()
    mcnpcell = arguments.cell

    clcell = getCombLayerCell(mcnpcell)
    obj = getCombLayerObject(clcell)
    print obj
                

if __name__ == "__main__":
    exit(main())

