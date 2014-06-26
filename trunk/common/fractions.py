#! /usr/bin/python -W all
# Calculation of atomic fractions for given volume fractions
# http://mc-tools.googlecode.com

import sys

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
#        print "mass fractions:", mf
#        print "atomic fractions:", af

        # normalisation:
        s = sum(af)
        for i,v in enumerate(af):
            af[i] = v/s

        return dict(zip(iname, af)), sum(af)

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

def main():
    """ """
    H = Isotope("H", 1.00794)
    O = Isotope("O", 15.999)
    Be = Isotope("Be", 9.012)

    beryllium = Material("Beryllium", 1.85)
    beryllium.AddIsotope(Be)

    water = Material("H2O", 1.0)
    water.AddIsotope(H, 2)
    water.AddIsotope(O, 1)

    waterfrac = 0.5
    BeWater = Compound("BeH2O")
    BeWater.AddMaterial(water, waterfrac)
    BeWater.AddMaterial(beryllium, 1.0-waterfrac)
#    BeWater.Print()
    print "Atomic fractions in %s with water fraction %g %%:" % (BeWater.name, waterfrac*100), BeWater.GetAtomicFractions()

    Fe54 = Isotope("Fe54", 53.9396127)
    Fe56 = Isotope("Fe56", 55.9349393)
    Fe57 = Isotope("Fe57", 56.9353958)
    Fe58 = Isotope("Fe58", 57.9332773)

    Fe = Material("Iron", 7.85)
    Fe.AddIsotope(Fe54, 0.05845)
    Fe.AddIsotope(Fe56, 0.91754)
    Fe.AddIsotope(Fe57, 0.02119)
    Fe.AddIsotope(Fe58, 0.00282)
    
    waterfrac = 0.1
    FeWater = Compound("FeH2O")
    FeWater.AddMaterial(water, waterfrac)
    FeWater.AddMaterial(Fe, 1.0-waterfrac)
    print "Atomic fractions in %s with water fraction %g %%:" % (FeWater.name, waterfrac*100), FeWater.GetAtomicFractions()
    

if __name__=="__main__":
    sys.exit(main())
