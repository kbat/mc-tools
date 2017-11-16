#! /usr/bin/python -W all

# from scipy import constants
import subprocess, os, sys
from math import sqrt

def L2E(l, m=1.674927351e-27): #constants.physical_constants['neutron mass'][0]):
    """
    Angstrom to MeV converter.
    m = particle mass in kg.
    """
    l = l*1.0E-10 # Angstrom -> meter
    e = 1.602176565e-19 # constants.physical_constants['atomic unit of charge'][0]
    h = 6.62606957e-34 # constants.physical_constants['Planck constant'][0]
    p = h/l
    energy = p*p/(2*m)
    return energy/e/1.0E+6

def E2L(energy, m=1.674927351e-27): #constants.physical_constants['neutron mass'][0]):
    """
    MeV to Angstrom converter
    m = particle mass in kg
    """
    e = 1.602176565e-19 # constants.physical_constants['atomic unit of charge'][0]
    h = 6.62606957e-34 # constants.physical_constants['Planck constant'][0]
    l = h/sqrt(2*m*energy*e)*1.0E+7
    return l

    
def GetVariable(f, var):
    """
    Return the variable value from the CombLayer-generated xml file
    """
    p = subprocess.Popen("getvariable %s %s" % (f, var), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pid = p.pid
    output, error = p.communicate()
    return output

def checkPaths(dirs, files, verbose=True):
    """
    Checks if folders/files exist
    """
    for d in dirs:
        if not os.path.isdir(d):
            if verbose:
                print>>sys.stderr, d, "does not exist"
            return 1

    for f in files:
        if not os.path.isfile(f): 
            print>>sys.stderr, f, "does not exist"
            return 2
    return 0


### MIXTURES ###

class Compound:
    """ Compound is a mixture of materials with given volume fractions """
    def __init__(self, name):
        self.name = name
        self.materials = []
        self.vf = [] # volume fractions of corresponding materials

    def AddMaterial(self, m, vf):
        """ Adds material m with given volume fraction vf """
        self.materials.append(m)
        self.vf.append(vf)

    def GetDensity(self):
        """ Return density of compound """
        rho = 0.0
        for j,m in enumerate(self.materials):
            rho += m.density*self.vf[j]
        return rho

    def GetMassFraction(self, material):
        """ Return mass fraction of the given material """
        mf = None
        for im, m in enumerate(self.materials):
            if m == material:
                mf = m.density*self.vf[im]/self.GetDensity()
        if mf == None:
            raise IOError("Compound %s does not contain material %s" % (self.name, material.name))
        return mf
        

    def GetAtomicFractions(self):
        """ Calculates mass fractions """
        vf = [] # volume fractions of isotopes
        mf = [] # mass fractions of isotopes
        af = [] # atomic fractions of isotopes
        iname = [] # isotope names
        for im,m in enumerate(self.materials):
            for ii, i in enumerate(m.isotopes):
                curvf = m.GetVolumeFraction(i)*self.vf[im] # current volume fraction
                vf.append(curvf)
                curmf = self.GetMassFraction(m)*i.A*m.nn[ii]/m.GetA() # current mass fraction
                mf.append(curmf)
                af.append(curmf/i.A)
                iname.append(i.name)

        # normalisation:
        s = sum(af)
        for i,v in enumerate(af):
            af[i] = v/s

        return dict(zip(iname, af))

    def PrintAtomicFractions(self):
        for i,f in sorted(self.GetAtomicFractions().iteritems()):
            print i,f
        print "Density: ", -self.GetDensity()

    def Print(self):
        print "Compound:", self.name
        print " Density:", self.GetDensity()
        for j,m in enumerate(self.materials):
            print "", self.vf[j], "%"
            m.Print()
        print " Mass fractions:"
        self.GetAtomicFractions()

class Material:
    """ Material is made of isotopes """
    def __init__(self, name, density):
        self.name = name
        self.isotopes = []
        self.nn = [] # number of corresponding isotopes
        self.density = density

    def AddIsotope(self, i, n=1):
        self.isotopes.append(i)
        self.nn.append(n)

    def GetA(self):
        """ Return atomic weight """
        s = 0.0;
        for j,i in enumerate(self.isotopes):
            s += self.nn[j]*i.A;
        return s

    def GetVolumeFraction(self, isotope):
        """ Return volume fraction of the given isotope """
        vf = None
        for j,i in enumerate(self.isotopes):
            if i == isotope:
                vf = self.nn[j]/sum(self.nn)
                pass
        if vf == None:
            raise IOError("Material %s does not have isotope %s" % (self.name, isotope.name))
        return vf

    def Print(self):
        print " Material:", self.name
        print "  Density:", self.density
        print "  Atomic weight: ", self.GetA()
        print "  Isotopes:"
        for j,i in enumerate(self.isotopes):
            print " "*2, self.nn[j],
            i.Print()
            print "   Volume fraction in %s: %g" % (self.name, self.GetVolumeFraction(i))

class Isotope:
    """ Isotopes form material """
    def __init__(self, name, A):
        self.name = name
        self.A = A # atomic weight

    def Print(self):
        print "\t%s %g" % (self.name, self.A)

### END MIXTURES ###
