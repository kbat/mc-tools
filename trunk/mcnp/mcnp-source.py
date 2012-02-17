#! /usr/bin/python -W all

import fileinput
import sys
from string import join

def getParabola(fullwidth, x):
    """
    Return the value of PDF of parabolic distribution:
    p(x) = 3/4d * (1-x^2/d^2)
    where d is half-width of parabola.
    Currently returns the non-normalized value (3/4d is ONE)
    """
    d = fullwidth/2.0
    return 1.0-(x*x)/(d*d)

def main():
    for line in fileinput.input():
        print line.rstrip()
        if line[2:25] == "### SOURCE 2D PARABOLIC":
            words = line.split()
            AA = float(words[5])
            BB = float(words[6])
            NX = int(words[7])
            NY = int(words[8])
            xmin = -AA/2.0
            dx = AA/NX
            ymin = -BB/2.0
            dy = BB/NY
            print "c     Full x-width:", AA, "     Number of x-bins:", NX
            print "c     Full y-width:", BB, "     Number of y-bins:", NY
            for x in range(NX+1):
                if x == 0:
                    print "SI1  A  ", xmin + x*dx
                else:
                    print " "*8, xmin + x*dx
            for x in range(NX+1):
                if x == 0:
                    print "SP1     ", getParabola(AA, xmin+x*dx)
                else:
                    print " "*8, getParabola(AA, xmin+x*dx)
            for y in range(NY+1):
                if y == 0:
                    print "SI2  A  ", ymin + y*dy
                else:
                    print " "*8, ymin + y*dy
            for y in range(NY+1):
                if y == 0:
                    print "SP2     ", getParabola(BB, ymin+y*dy)
                else:
                    print " "*8, getParabola(BB, ymin+y*dy)


if __name__ == "__main__":
    sys.exit(main())
