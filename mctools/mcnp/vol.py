#! /usr/bin/python
# Generates the MCNP vol cards

import sys

# total number of cells:
N = 3019

vols = {}
vols[985] = 2.43687E+5
vols[1780] = 7.27140E+04
vols[1776] = 3.69161E+05
vols[6] = 1.96631E+04
vols[8] = 1.97065E+04
vols[10] = 1.95215E+04
vols[12] = 1.64029E+04
vols[14] = 1.64034E+04
vols[16] = 1.65427E+04
#print vols


s = "vol"
c_prev = 0
for i,c in enumerate(sorted(vols.iterkeys())):
    v = vols[c]
    dist_to_prev=c-c_prev
    
    if dist_to_prev==0:
        print "Error: dist_to_prev is 0"
        sys.exit(1)

#    print "%d:" % i, c,v, dist_to_prev
    
    if dist_to_prev==1:
        s += " %g " % v
    if dist_to_prev==2:
        s += " 1 %g " % (v)
    elif dist_to_prev>2:
        s += " 1 %dr %g " % (dist_to_prev-2, v)
    c_prev = c

s += " 1 %dr" % (N-c-3)
print s
