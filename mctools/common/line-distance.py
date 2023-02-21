#! /usr/bin/env python3

import sys
import numpy as np
import argparse

class Base:
    def __init__(self, coord):
        self.coord = coord

    def __array__(self):
        return self.coord

class Point(Base):
    def __init__(self, x, y, z):
        self.coord = np.array([x,y,z])

    def __init__(self, coord):
        d = tuple(map(float, coord.split()))
        l = len(d)
        assert l == 3, f"Point must have exactly 3 coordinates, got: {l}"
        super().__init__(np.array(d))

    def __repr__(self):
        return self.coord

class Vector(Base):
    def __init__(self, x, y, z):
        self.coord = np.array([x,y,z])

    def __init__(self, coord):
        d = tuple(map(float, coord.split()))
        l = len(d)
        assert l == 3, f"Vector must have exactly 3 coordinates, got: {l}"
        # for c in d:
        #     val = abs(float(c))
        #     assert val<=1.0, f"Directon cosines must be < 1, got: {val}"
        super().__init__(np.array(d))

def GetDistance(verbose, r1, s1, r2, s2):
    '''
    Return distance between two lines defined by a point and a vector

    https://cyclowiki.org/wiki/%D0%A0%D0%B0%D1%81%D1%81%D1%82%D0%BE%D1%8F%D0%BD%D0%B8%D0%B5_%D0%BC%D0%B5%D0%B6%D0%B4%D1%83_%D0%BF%D1%80%D1%8F%D0%BC%D1%8B%D0%BC%D0%B8_%D0%B2_%D1%82%D1%80%D1%91%D1%85%D0%BC%D0%B5%D1%80%D0%BD%D0%BE%D0%BC_%D0%BF%D1%80%D0%BE%D1%81%D1%82%D1%80%D0%B0%D0%BD%D1%81%D1%82%D0%B2%D0%B5
    '''

    r21 = np.add(r1, np.multiply(r2, -1))
    if verbose:
        print("r21:",r21)

    den = np.cross(s1, s2) # denumerator
    den = np.linalg.norm(den)
    d12 = 0.0
    if den == 0.0:
        if verbose:
            print("Lines are parallel")
        v1 = np.absolute(np.cross(r21, s1))
        if verbose:
            print(v1)
        v1=np.linalg.norm(v1)
        if verbose:
            print(v1)
        return v1/np.linalg.norm(s1)
    else:
        if verbose:
            print("Lines are crossing")
        m1 = np.vstack([r21, s1, s2])
        if verbose:
            print("m1:",m1)
        m1 = np.linalg.det(m1) # numerator

        return m1/den


def main():
    '''
    Return distance between two lines defined by a point and a vector
    '''
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')
    parser.add_argument('-point1', type=str, help='First point coordinates', required=True)
    parser.add_argument('-vec1',   type=str, help='First point vector', required=True)
    parser.add_argument('-point2', type=str, help='Second point coordinates', required=True)
    parser.add_argument('-vec2',   type=str, help='Second point vector', required=True)

    args = parser.parse_args()

    # Algebra tests:
    if abs(GetDistance(False, Point("1 -5 -1"), Vector("-2 3 4"), Point("-4 3 5"), Vector("4 -6 -8"))-3.0)>1e-10:
        print("Parallel lines check failed")
        return 1
    if abs(GetDistance(False, Point("1 -5 -1"), Vector("-2 3 4"), Point("-2 1 2"), Vector("-2 2 3"))-3.0)>1e-10:
        print("Crossing lines check failed")
        return 2


    r1 = Point(args.point1)
    s1 = Vector(args.vec1)
    r2 = Point(args.point2)
    s2 = Vector(args.vec2)

    d12 = GetDistance(args.verbose, r1, s1, r2, s2)
    print(f"Distance: {d12:.2g}")



    # print(np.matrix(r21, s1, s2))

    # d12 = np.multiply(d12, s1)
    # print(d12)
    # d12 = np.multiply(d12, s2)
    # print(d12)
    # print(np.multiply(r1, -1))




if __name__ == "__main__":
    sys.exit(main())
