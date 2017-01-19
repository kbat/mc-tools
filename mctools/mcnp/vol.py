#! /usr/bin/python
# generates the vol cards

N = 1509 # total number of cells
cell = 881
vol = 2.43904E+05
print "vol 1 %dr %g 1 %dr" % (cell-2, vol, N-cell-3)

vols = {}
vols[881] = 88.1
#vols[882] = 88.2
#vols[885] = 88.5
print vols


s = "vol"
c_prev = 0
for i,c in enumerate(sorted(vols.iterkeys())):
    v = vols[c]
    dist_to_prev=c-c_prev
    print "%d:" % i, c,v, dist_to_prev
    if dist_to_prev==1:
        s += " %g | " % v
    if dist_to_prev==2:
        s += " 1 %g | " % (v)
    elif dist_to_prev>2:
        s += " 1 %dr %g | " % (dist_to_prev-2, v)
    c_prev = c

s += " 1 %d r" % (N-c-3)
print s
