#! /usr/bin/python -W all
# Some examples of calculation of atomic fractions for given volume fractions
# https://github.com/kbat/mc-tools

from mctools import Isotope, Material, Compound

H   = Isotope("01001.70c", 1.00794)
D   = Isotope("01002.70c", 2.01410178)
He3 = Isotope("02003.70c", 3.0160293)
He4 = Isotope("02004.70c", 4.002602)
O   = Isotope("08016.70c", 15.999)
Be  = Isotope("04009.70c", 9.012)

Fe54 = Isotope("26054.70c", 53.9396127)
Fe56 = Isotope("26056.70c", 55.9349393)
Fe57 = Isotope("26057.70c", 56.9353958)
Fe58 = Isotope("26058.70c", 57.9332773)

Zr90 = Isotope("40090.70c", 89.9047026)
Zr91 = Isotope("40091.70c", 90.9056439)
Zr92 = Isotope("40092.70c", 91.9050386)
Zr94 = Isotope("40094.70c", 93.9063148)
Zr96 = Isotope("40096.70c", 95.908275)

Pb204 = Isotope("82204.70c", 203.973020)
Pb206 = Isotope("82206.70c", 205.974440)
Pb207 = Isotope("82207.70c", 206.975872)
Pb208 = Isotope("82208.70c", 207.976627)

beryllium = Material("Beryllium", 1.85)
beryllium.AddIsotope(Be)

water = Material("H2O", 1.0)
water.AddIsotope(H, 2)
water.AddIsotope(O, 1)

D2O = Material("D2O", 1.107)
D2O.AddIsotope(D, 2)
D2O.AddIsotope(O, 1)
D2O.Print()

print "\n04005"
waterfrac = 0.05
BeWater = Compound("BeH2O")
BeWater.AddMaterial(water, waterfrac)
BeWater.AddMaterial(beryllium, 1.0-waterfrac)
#    BeWater.Print()
print "Atomic fractions in %s with water vol fraction %g %%:" % (BeWater.name, waterfrac*100)
BeWater.PrintAtomicFractions()

print "\n04020"
waterfrac = 0.1
BeD2O10 = Compound("BeD2O10%")
BeD2O10.AddMaterial(D2O, waterfrac)
BeD2O10.AddMaterial(beryllium, 1.0-waterfrac)
print "Atomic fractions in %s with D2O vol fraction %g %%:" % (BeD2O10.name, waterfrac*100)
BeD2O10.PrintAtomicFractions()


Fe = Material("Iron", 7.85)
Fe.AddIsotope(Fe54, 0.05845)
Fe.AddIsotope(Fe56, 0.91754)
Fe.AddIsotope(Fe57, 0.02119)
Fe.AddIsotope(Fe58, 0.00282)

waterfrac = 0.1
FeWater = Compound("IronH2O")
FeWater.AddMaterial(water, waterfrac)
FeWater.AddMaterial(Fe, 1.0-waterfrac)
print "Atomic fractions in %s with water vol fraction %g %%:" % (FeWater.name, waterfrac*100)
FeWater.PrintAtomicFractions()

Zirconium = Material("Zirconium", 6.49)
Zirconium.AddIsotope(Zr90, 0.5145)
Zirconium.AddIsotope(Zr91, 0.1122)
Zirconium.AddIsotope(Zr92, 0.1715)
Zirconium.AddIsotope(Zr94, 0.1738)
Zirconium.AddIsotope(Zr96, 0.0280)

waterfrac = 0.1
ZrWater = Compound("ZrH2O")
ZrWater.AddMaterial(water, waterfrac)
ZrWater.AddMaterial(Zirconium, 1.0-waterfrac)
print "Atomic fractions in %s with water vol fraction %g %%:" % (ZrWater.name, waterfrac*100)
ZrWater.PrintAtomicFractions()

Lead = Material("Lead", 11.4)
Lead.AddIsotope(Pb204, 1.4)
Lead.AddIsotope(Pb206, 24.1)
Lead.AddIsotope(Pb207, 22.1)
Lead.AddIsotope(Pb208, 52.4)

print "\n82010"
PbWater = Compound("PbH2O")
PbWater.AddMaterial(water, waterfrac)
PbWater.AddMaterial(Lead, 1.0-waterfrac)
print "Atomic fractions in %s with water vol fraction %g %%:" % (PbWater.name, waterfrac*100)
PbWater.PrintAtomicFractions()

print "\n82020"
waterfrac = 0.1
PbD2O = Compound("PbD2O20%")
PbD2O.AddMaterial(D2O, waterfrac)
PbD2O.AddMaterial(Lead, 1.0-waterfrac)
print "Atomic fractions in %s with D2O vol fraction %g %%:" % (PbD2O.name, waterfrac*100)
PbD2O.PrintAtomicFractions()

print "\nHelium"
Helium = Material("Helium", 0.1786E-3)
Helium.AddIsotope(He3, 0.00000137)
Helium.AddIsotope(He4, 0.99999863)
Helium.Print()
