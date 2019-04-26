#! /usr/bin/python
from __future__ import print_function
import re

def getPar(masterfile, parname, pos=3):
    """
    Return parameter 'parname' from MCNP master file 'masterfile' (the syntax of pstudy is assumed)
    pos - optional argument, specifies the position of the value in the THEparname string
    """
    f = open(masterfile)
    val = ""
    for line in f.readlines():
        if re.search("\Ac THE%s" % parname, line, re.IGNORECASE):
            val = float(line.split()[pos])
#            print(line.strip(), val)
    f.close()
    if val is "":
        raise IOError("Value of %s not found in %s" % (parname, masterfile))
    return val

 

def GetParticleNames(a):
    """Convert the array of 1 and 0 to the list of particles
       according to the Table 4-1 on page 4-10 (48) of the MCNP 2.7.0 Manual
    """
    # '!' stands for 'anti'
    names = ['neutron', '-neutron', 'photon', 'electron', 'positron',
             'mu-', '!mu-', 'tau-', 'nue', '!nue', 'num', 'nut',
             'proton', '!proton', 'lambda0', 'sigma+', 'sigma-', 'cascade0', 'cascade-', 'omega-', 'lambdac+', 'cascadec+', 'cascadec0', 'lambdab0',
             'pion+', 'pion-', 'pion0', 'kaon+', 'kaon-', 'K0short', 'K0long', 'D+', 'D0', 'Ds+', 'B+', 'B0', 'Bs0',
             'deuteron', 'triton', 'He3', 'He4', 'heavy ions']
    vals = []
    print("a", a)
    if isinstance(a, int):
        print(a)
    else:
        for i in range(len(a)):
            if a[i] == 1: vals.append(names[i])
            elif a[i] != 0:
                print('strange values (not 0 or 1) found in the list of particles:', a)
    return vals
