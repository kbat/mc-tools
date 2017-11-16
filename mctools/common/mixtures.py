#! /usr/bin/python -W all
# Some examples of calculation of atomic fractions for the given volume fractions
# https://github.com/kbat/mc-tools

from mctools import Isotope, Material, Compound

H   = Isotope("01001.70c", 1.00794)
D   = Isotope("01002.70c", 2.01410178)
He3 = Isotope("02003.70c", 3.0160293)
He4 = Isotope("02004.70c", 4.002602)
C   = Isotope("06000.71c", 12.011)
O   = Isotope("08016.70c", 15.999)
Be  = Isotope("04009.70c", 9.012)
Al  = Isotope("13027.70c", 26.981539)

Si28 = Isotope("14028.71c", 27.9769265325) # wiki
Si29 = Isotope("14029.71c", 28.976494700) # wiki
Si30 = Isotope("14030.71c", 29.97377017) # wiki

P31  = Isotope("15031.71c", 30.97376163) # wiki

S32  = Isotope("16032.71c", 31.97207100) # wiki
S33  = Isotope("16033.71c", 32.97145876) # wiki
S34  = Isotope("16034.71c", 33.96786690) # wiki
S36  = Isotope("16036.71c", 35.96708076) # wiki

Cr50 = Isotope("24050.71c", 49.9460442) # wiki
Cr52 = Isotope("24052.71c", 51.9405075) # wiki
Cr53 = Isotope("24053.71c", 52.9406494) # wiki
Cr54 = Isotope("24054.71c", 53.9388804) # wiki

Mn55 = Isotope("25055.71c", 54.9380451) # wiki

Fe54 = Isotope("26054.70c", 53.9396127)
Fe56 = Isotope("26056.70c", 55.9349393)
Fe57 = Isotope("26057.70c", 56.9353958)
Fe58 = Isotope("26058.70c", 57.9332773)

Co59 = Isotope("27059.71c", 58.9331950) # wiki

Ni58 = Isotope("28058.71c", 57.9353429) # wiki
Ni60 = Isotope("28060.71c", 59.9307864) # wiki
Ni61 = Isotope("28061.71c", 60.9310560) # wiki
Ni62 = Isotope("28062.71c", 61.9283451) # wiki
Ni64 = Isotope("28064.71c", 63.9279660) # wiki

Zr90 = Isotope("40090.70c", 89.9047026)
Zr91 = Isotope("40091.70c", 90.9056439)
Zr92 = Isotope("40092.70c", 91.9050386)
Zr94 = Isotope("40094.70c", 93.9063148)
Zr96 = Isotope("40096.70c", 95.908275)

Mo92  = Isotope("42092.71c", 91.906811) # wiki
Mo94  = Isotope("42094.71c", 93.9050883) # wiki
Mo95  = Isotope("42095.71c", 94.9058421) # wiki
Mo96  = Isotope("42096.71c", 95.9046795) # wiki
Mo97  = Isotope("42097.71c", 96.9060215) # wiki
Mo98  = Isotope("42098.71c", 97.9054082) # wiki
Mo100 = Isotope("42100.71c", 99.907477) # wiki

Pb204 = Isotope("82204.70c", 203.973020)
Pb206 = Isotope("82206.70c", 205.974440)
Pb207 = Isotope("82207.70c", 206.975872)
Pb208 = Isotope("82208.70c", 207.976627)

##### Materials ####


beryllium = Material("Beryllium", 1.85)
beryllium.AddIsotope(Be)

water = Material("H2O", 1.0)
water.AddIsotope(H, 2)
water.AddIsotope(O, 1)

D2O = Material("D2O", 1.107)
D2O.AddIsotope(D, 2)
D2O.AddIsotope(O, 1)
D2O.Print()

Hydrogen = Material("Hydrogen", 0.07)
Hydrogen.AddIsotope(H, 1)

Aluminium = Material("Aluminium", 2.7) # cold Al: 2.73
Aluminium.AddIsotope(Al, 1)

SS316L = Material("SS316L", 7.76)
SS316L.AddIsotope(C,  0.001392603)
SS316L.AddIsotope(Si28,  0.007323064)
SS316L.AddIsotope(Si29,  0.000372017)
SS316L.AddIsotope(Si30,  0.000245523)
SS316L.AddIsotope(P31,  0.000360008)
SS316L.AddIsotope(S32,  0.000165168)
SS316L.AddIsotope(S33,  0.000001304)
SS316L.AddIsotope(S34,  0.000007390)
SS316L.AddIsotope(S36,  0.000000017)
SS316L.AddIsotope(Cr50,  0.007920331)
SS316L.AddIsotope(Cr52,  0.152735704)
SS316L.AddIsotope(Cr53,  0.017319003)
SS316L.AddIsotope(Cr54,  0.004311066)
SS316L.AddIsotope(Mn55,  0.018267327)
SS316L.AddIsotope(Fe54,  0.038344779)
SS316L.AddIsotope(Fe56,  0.601931034)
SS316L.AddIsotope(Fe57,  0.013901213)
SS316L.AddIsotope(Fe58,  0.001849996)
SS316L.AddIsotope(Co59,  0.000283816)
SS316L.AddIsotope(Ni58,  0.080834464)
SS316L.AddIsotope(Ni60,  0.031137291)
SS316L.AddIsotope(Ni61,  0.001353516)
SS316L.AddIsotope(Ni62,  0.004315603)
SS316L.AddIsotope(Ni64,  0.001099057)
SS316L.AddIsotope(Mo92,  0.002145890)
SS316L.AddIsotope(Mo94,  0.001341000)
SS316L.AddIsotope(Mo95,  0.002310064)
SS316L.AddIsotope(Mo96,  0.002423388)
SS316L.AddIsotope(Mo97,  0.001388944)
SS316L.AddIsotope(Mo98,  0.003514494)
SS316L.AddIsotope(Mo100,  0.001404926)
SS316L.Print()


##### Compounds ####

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

waterfrac = float(0.2)
print "\nSS316L and %.0f%% of water" % (waterfrac*100)
SS316LH2O = Compound("SS316L20H2O")
SS316LH2O.AddMaterial(water, waterfrac)
SS316LH2O.AddMaterial(SS316L, 1-waterfrac)
SS316LH2O.PrintAtomicFractions()


print "\nWater and Al"

waterfrac = 1-0.07 #
waterAl = Compound("WaterAl")
waterAl.AddMaterial(water, waterfrac)
waterAl.AddMaterial(Aluminium, 1-waterfrac)
waterAl.PrintAtomicFractions()


print "\nHydrogen and Al"
Alfrac = 2.9 # %
ParaHAl = Compound("ParaHAl")
ParaHAl.AddMaterial(Aluminium,Alfrac/100.0)
ParaHAl.AddMaterial(Hydrogen,1-Alfrac/100.0)
ParaHAl.PrintAtomicFractions()
