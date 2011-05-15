#! /usr/bin/python -W all
#
# Convertw wwinp file to the Wheight Window format of PHITS
#
#

import re, sys
from string import join, replace
from phits import mcnp_phits_particles as particle

def print_weights(weights, ncells):
    """
    Print weights for ni energy/time intervals
    """
    weights = dict(weights)
    intervals = weights.keys()
    
    tmparray = []
    for icell in range(1,ncells+1):
        for i in intervals:
            tmparray.append(weights[i][icell-1])
        print "    %4d" % icell, join(tmparray)
        del tmparray[:]

def main():
    """Usage: wwin2phits wwinp [wwinp.phits]
    """
    energies = []
    weights = {}
    wwe = False
    wwn = False
    ncells = 0
    ncells_tmp = 0
    i = 0 # energy/time interval

    fin = open("wwinp")

    
    for line in fin.readlines():
        line = line.rstrip()
        if re.search("^wwe", line):
            wwe = True
            print_weights(weights, ncells)
            for k in weights.keys():
                del weights[k][:]
            weights = {}
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
            

            if ncells == 0 and ncells_tmp != 0:
                ncells = ncells_tmp

            i = int(line.split(":")[0][3:]) # energy / time interval: wwn1 -> 1
            weights[i] = []

            if i == 1:
                print "   eng = %d" % len(energies)
                print "         %s" % join(energies)


            for w in line.split()[1:]:
                weights[i].append(w)
                ncells_tmp += 1
            continue

        if wwn and not wwe:
            for w in line.split():
                weights[i].append(w)
                ncells_tmp += 1

        if wwe and not wwn:
            for w in line.split():
                energies.append(w)
                continue

    print_weights(weights, ncells)


if __name__ == "__main__":
    sys.exit(main())
