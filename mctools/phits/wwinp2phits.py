#! /usr/bin/python -W all
#
# Converts wwinp file to the Wheight Window format of PHITS
#
#

import re, sys
from string import join
from phits import mcnp_phits_particles as particle

def getCells(fname):
    """
    Return array with cell numbers from the input file named fname.
    Used in wwinp2phits.py
    """
    isCellSection = False
    f = open(fname)
    cells = []
    c = 0 # current cell
    for line in f.readlines():
        if re.search("\[cell\]", line):
            isCellSection = True
        elif isCellSection and re.search("^\[", line):
            isCellSection = False
            break

        words = line.split()
        if len(words) == 0:
            continue
        try:
            c = int(words[0])
        except ValueError:
            continue

        cells.append(c)
        
    f.close()
    return cells

def get_weight_titles(ni):
    tmparray = ["     reg"]
    for i in range(ni):
        tmparray.append("%9s%d" % ('ww', i+1))
    return join(tmparray)

def print_weights(weights, cells):
    """
    Print weights for ni energy/time intervals
    """
    weights = dict(weights)
    intervals = weights.keys()
    ncells = len(cells)-4
    
    tmparray = []
#    outarray = []
    for icell in range(1,ncells+1):
        for i in intervals:
            tmparray.append(weights[i][icell-1])
        if len(tmparray) != 0:
            print "    %4d" % cells[icell-1], join(tmparray)
#        outarray.append("    %4d %s" % (icell, join(tmparray)))
        del tmparray[:]
#    return outarray

def my_print_weights(weights, cells):
    """
    Print weights for ni energy/time intervals
    also print my weights 442-462
    """
    weights = dict(weights)
    intervals = weights.keys()
    ncells = len(cells)-4
    
    tmparray = []
#    outarray = []
    w442, w460, w461, w462 = None, None, None, None
    the_line = None
    for icell in range(1,ncells+1):
        for i in intervals:
            tmparray.append(weights[i][icell-1])
        if len(tmparray) != 0:
            the_line = "    %4d %s"  % (cells[icell-1], join(tmparray))
            print the_line
            if cells[icell-1] == 242: w442 = "    %4d %s"  % (442, join(tmparray))
            if cells[icell-1] == 260: w460 = "    %4d %s"  % (460, join(tmparray))
            if cells[icell-1] == 260: w461 = "    %4d %s"  % (461, join(tmparray))
            if cells[icell-1] == 260: w462 = "    %4d %s"  % (462, join(tmparray))
        del tmparray[:]
    print w442
    print w460
    print w461
    print w462
#    return outarray

def main():
    """Converts wwinp file to the Wheight Window format of PHITS.
The output can be forwarded in a separate file and included in the PHTIS input by
      infl: {file-name}
Usage: wwin2phits input.phits wwinp [ > wwinp.phits ]
       input.phits - the PHITS input file - needed to optain the cell numbers
    """
    energies = []
    weights = {}
    wwe = False
    wwn = False
    ncells = 0
    ncells_tmp = 0
    i = 0 # energy/time interval

    if len(sys.argv) != 3:
        print main.__doc__
        sys.exit(1)

    cells = getCells(sys.argv[1])
#    print cells, len(cells)
#    sys.exit(0)

    fin = open(sys.argv[2])
    
    for line in fin.readlines():
        line = line.rstrip()
        if re.search("^wwe", line):
            wwe = True
            my_print_weights(weights, cells)
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
                print get_weight_titles(len(energies))

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

    my_print_weights(weights, cells)

    fin.close()

if __name__ == "__main__":
    sys.exit(main())
