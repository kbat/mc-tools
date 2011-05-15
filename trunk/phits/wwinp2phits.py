#! /usr/bin/python -W all
#
# Convertw wwinp file to the Wheight Window format of PHITS
#
#

import re, sys
from string import join, replace

def print_weights(weights, ni):
    """
    Print weights for ni energy/time intervals
    """

def main():
    """Usage: wwin2phits wwinp [wwinp.phits]
    """
    particle = {"n" : "neutron", "h":"proton", "/":"pion", "z":"z", "d":"d", "t":"t", "s":"s", "a":"a"}
    energies = []
    weights = {}
    wwe = False
    wwn = False
    i = 0 # energy/time interval

    fin = open("wwinp")

    
    for line in fin.readlines():
        line = line.rstrip()
        if re.search("^wwe", line):
            wwe = True
            wwn = False

            print "\n[Weight Window]"
            tmp = join(line.split(":")[1]).split()
            p = tmp[0]
            print "  part = %s" % particle[p]
            del energies[:]
            for w in line.split()[1:]:
                energies.append(w)
            continue
        if re.search("^wwn", line):
            wwn = True
            wwe = False
            

            if weights.has_key(i):
                print weights[i]

            print "   eng = %d" % len(energies)
            print "         %s" % join(energies)

            i = replace(line.split(":")[0], "wwn", "") # energy / time interval
            weights[i] = []
            for w in line.split()[1:]:
                weights[i].append(w)
            continue

        if wwn and not wwe:
            for w in line.split():
                weights[i].append(w)

        if wwe and not wwn:
            for w in line.split():
                energies.append(w)
                continue

if __name__ == "__main__":
    sys.exit(main())
