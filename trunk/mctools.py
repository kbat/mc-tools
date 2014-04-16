#! /usr/bin/python -W all

from scipy import constants

def L2E(l, m=constants.physical_constants['neutron mass'][0]):
    """
    Angstrom to MeV converter.
    m = particle mass in kg. Default is neutron mass.
    """
    l = l*1.0E-10 # Angstrom -> meter
    e = constants.physical_constants['atomic unit of charge'][0]
    h = constants.physical_constants['Planck constant'][0]
    p = h/l
    energy = p*p/(2*m)
    return energy/e/1.0E+6

    

def LambdaBins(nbins, lmin, lmax):
    """
    Return array of energy boundaries in order to make equal binning in wavelength
    """
    l = [] # lambda bins
    e = [] # energy bins
    dl = (lmax-lmin)/nbins  # lambda bin width
    
    for i in range(nbins+1): l.append(lmin+i*dl)
#    print l

    for i in range(nbins+1):
        e.append(L2E(l[nbins-i]))
    return e

print LambdaBins(100, 0.1, 20)
