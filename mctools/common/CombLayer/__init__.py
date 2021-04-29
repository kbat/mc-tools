##
## Comblayer-related functions
##
import re, math
from ROOT import TFile, Double_t

def getIntegral(fname, tname, axis, bmin, bmax):
    """
    Return integral and error of a projection of THnSparseF
    """
    f = TFile(fname)
    t = f.Get(tname)
    h = t.Projection(axis)
    val = 0
    err = Double_t(0)
    val = h.IntegralAndError(bmin, bmax, err)
    return Double_t(val), Double_t(err)



def distance(x1, y1, z1, x2, y2, z2 ):
    """
    Return Euclidian metrics between two points (x1, y1, z1) and (x2, y2, z2)
    """
    return math.sqrt(pow(x2-x1, 2) + pow(y2-y1, 2) + pow(z2-z1, 2))


def getPar(masterfile, parname, pos=2, comment="c"):
    """
    Return parameter 'parname' from MCNP master file 'masterfile' (the syntax of CombLayer is assumed)
    pos - optional argument, specifies the position of the value in the THEparname string
    """
    f = open(masterfile)
    val = ""
    if comment == "*":
        comment = "\*"
    for line in f.readlines():
        if re.search("\A%s %s " % (comment, parname), line, re.IGNORECASE):
            # print (line.strip(), val)
            try:
                val = float(line.split()[pos])
            except ValueError:
                val = line.split()[pos] # non-float
    f.close()
    if val is "":
        raise IOError("Value of %s not found in %s" % (parname, masterfile))
    return val

def getOmega(fname, f5name):
    """Return solid angle of a F5 collimator"""
    XB = getPar(fname, "%sXB" % f5name)
    YB = getPar(fname, "%sYB" % f5name)
    ZB = getPar(fname, "%sZB" % f5name)
    ZG = getPar(fname, "%sZG" % f5name)
    XC = getPar(fname, "%sXC" % f5name)
    YC = getPar(fname, "%sYC" % f5name)
    ZC = ZB
    x0 = getPar(fname, "%sX" % f5name)
    y0 = getPar(fname, "%sY" % f5name)
    z0 = getPar(fname, "%sZ" % f5name)
    XM = (XB+XC)/2.0
    YM = (YB+YC)/2.0
    ZM = (ZB+ZG)/2.0
    L = distance(XM, YM, ZM, x0, y0, z0)
    S = distance(XB, YB, ZB, XC, YC, ZC)*distance(XB, YB, ZB, XB, YB, ZG)
    omega = S/L/L
    return omega
