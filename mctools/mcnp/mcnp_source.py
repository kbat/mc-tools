#! /usr/bin/python -W all
#
# Syntaxis:
### SOURCE 2D PARABOLIC AA BB NX NY ###
# or
### SOURCE UNIFORM AA BB NX NY ###
# AA and BB are full x and y widths
# NX and NY are numbers of bins along x and y axes
# or
### SOURCE GAUS SIGMAX SIGMAY NX NY TH ### - not yet implemented
#

from __future__ import print_function
import fileinput
import sys

def getParabola(fullwidth, x):
    """
    Return the value of PDF of 2D parabolic distribution:
    p(x) = 3/4d * (1-x^2/d^2)
    where d is half-width of parabola.
    Currently returns the non-normalized value (3/4d is ONE)
    """
    d = fullwidth/2.0
    return 1.0-(x*x)/(d*d)

def getUniform(fullwidth, x):
    """
    Return the p.d.f of uniform distribution:
    p(x) = 1/fullwidth  - if |x| <= fullwidth/2
    p(x) = 0            - otherwise
    """
    xmin, xmax = -fullwidth/2.0, fullwidth/2.0
    if x > xmin and x < xmax:
        return 1.0/fullwidth
    else:
        return 0
    

def main():
    is_fixed = False
    for line in fileinput.input():
        if line[0:23] == "### SOURCE 2D PARABOLIC":
            print("c %s" % line.rstrip())
            is_fixed = True
            words = line.split()
            if words[-1] != '###':
                print("ERROR in mcnp-source: wrong source definition format", file=sys.stderr)
                return 1
            AA = float(words[4])
            BB = float(words[5])
            NX = int(words[6])
            NY = int(words[7])
            xmin = -AA/2.0
            dx = AA/NX
            ymin = -BB/2.0
            dy = BB/NY
            print("c     Full x-width:", AA, "     Number of x-bins:", NX)
            print("c     Full y-width:", BB, "     Number of y-bins:", NY)
            for x in range(NX+1):
                if x == 0:
                    print("SI1  A  ", xmin + x*dx)
                else:
                    print(" "*8, xmin + x*dx)
            for x in range(NX+1):
                if x == 0:
                    print("SP1     ", getParabola(AA, xmin+x*dx))
                else:
                    print(" "*8, getParabola(AA, xmin+x*dx))
            for y in range(NY+1):
                if y == 0:
                    print("SI2  A  ", ymin + y*dy)
                else:
                    print(" "*8, ymin + y*dy)
            for y in range(NY+1):
                if y == 0:
                    print("SP2     ", getParabola(BB, ymin+y*dy))
                else:
                    print(" "*8, getParabola(BB, ymin+y*dy))
        elif line[0:18] == "### SOURCE UNIFORM":
            print("c %s" % line.rstrip())
            is_fixed = True
            words = line.split()
            if words[-1] != '###':
                print("ERROR in mcnp-source: wrong source definition format", file=sys.stderr)
                return 2
            AA = float(words[3])
            BB = float(words[4])
            NX = int(words[5])
            NY = int(words[6])
            xmin = -AA/2.0
            dx = AA/NX
            ymin = -BB/2.0
            dy = BB/NY
            print("c     Full x-width:", AA, "     Number of x-bins:", NX)
            print("c     Full y-width:", BB, "     Number of y-bins:", NY)
            for x in range(NX+1):
                if x == 0:
                    print("SI1  A  ", xmin + x*dx)
                else:
                    print(" "*8, xmin + x*dx)
            for x in range(NX+1):
                if x == 0:
                    if getUniform(AA, xmin+x*dx) != 0:
                        print("First bin is not zero", file=sys.stderr)
                        return 3
                    print("SP1     ", getUniform(AA, xmin+x*dx))
                else:
                    print(" "*8, getUniform(AA, xmin+x*dx))
            for y in range(NY+1):
                if y == 0:
                    print("SI2  A  ", ymin + y*dy)
                else:
                    print(" "*8, ymin + y*dy)
            for y in range(NY+1):
                if y == 0:
                    print("SP2     ", getUniform(BB, ymin+y*dy))
                else:
                    print(" "*8, getUniform(BB, ymin+y*dy))
        elif line[0:18] == "### SOURCE GAUS": # !!! not yet implemented - below is just copied from UNIFORM
            print("c %s" % line.rstrip())
            is_fixed = True
            words = line.split()
            if words[-1] != '###':
                print("ERROR in mcnp-source: wrong source definition format", file=sys.stderr)
                return 2
            SIGMAX = float(words[3])
            SIGMAY = float(words[4])
            NX = int(words[5])
            NY = int(words[6])
            xmin = -AA/2.0
            dx = AA/NX
            ymin = -BB/2.0
            dy = BB/NY
            print("c     Full x-width:", AA, "     Number of x-bins:", NX)
            print("c     Full y-width:", BB, "     Number of y-bins:", NY)
            for x in range(NX+1):
                if x == 0:
                    print("SI1  A  ", xmin + x*dx)
                else:
                    print(" "*8, xmin + x*dx)
            for x in range(NX+1):
                if x == 0:
                    if getUniform(AA, xmin+x*dx) != 0:
                        print("First bin is not zero", file=sys.stderr)
                        return 3
                    print("SP1     ", getUniform(AA, xmin+x*dx))
                else:
                    print(" "*8, getUniform(AA, xmin+x*dx))
            for y in range(NY+1):
                if y == 0:
                    print("SI2  A  ", ymin + y*dy)
                else:
                    print(" "*8, ymin + y*dy)
            for y in range(NY+1):
                if y == 0:
                    print("SP2     ", getUniform(BB, ymin+y*dy))
                else:
                    print(" "*8, getUniform(BB, ymin+y*dy))
        else:
            print(line.rstrip())
    
    if is_fixed == False:
        print("WARNING in mcnp-source.py: source definition not found", sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
