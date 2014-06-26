#! /usr/bin/python -W all
# Calculation of atomic fractions for given volume fractions

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
            rho += m.density*self.vf[j]/100.0
        return rho

    def GetMassFraction(self, material):
        """ Return mass fraction of the given material """
        mf = None
        for im, m in enumerate(self.materials):
            if m == material:
                mf = m.density*self.vf[im]/self.GetDensity()/100.0
        if mf == None:
            raise IOError("Compound %s does not contain material %s" % (self.name, material.name))
        return mf
        

    def GetMassFractions(self):
        """ Calculates mass fractions """
        vf = [] # volume fractions of isotopes
        mf = [] # mass fractions of isotopes
        af = [] # atomic fractions of isotopes
        iname = [] # isotope names
        for im,m in enumerate(self.materials):
            for ii, i in enumerate(m.isotopes):
                curvf = m.GetVolumeFraction(i)*self.vf[im]/100.0 # current volume fraction
                vf.append(curvf)
                curmf = self.GetMassFraction(m)*i.A*m.nn[ii]/m.GetA() # current mass fraction
                mf.append(curmf)
                af.append(curmf/i.A)
                iname.append(i.name)
#        print "mass fractions:", mf
#        print "atomic fractions:", af
        print dict(zip(iname, af))

    def Print(self):
        print "Compound:", self.name
        print " Density:", self.GetDensity()
        for j,m in enumerate(self.materials):
            print "", self.vf[j], "%"
            m.Print()
        print " Mass fractions:"
        self.GetMassFractions()

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
                vf = 100.0*self.nn[j]/sum(self.nn)
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

    waterfrac = 10
    BeWater = Compound("Be+10%H2O")
    BeWater.AddMaterial(water, waterfrac)
    BeWater.AddMaterial(beryllium, 100-waterfrac)
#    BeWater.Print()
    BeWater.GetMassFractions()

#    print BeWater.GetMassFraction(beryllium)


if __name__=="__main__":
    sys.exit(main())
