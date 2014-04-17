#! /usr/bin/python -W all

from scipy import constants
import subprocess

def L2E(l, m=constants.physical_constants['neutron mass'][0]):
    """
    Angstrom to MeV converter.
    m = particle mass in kg.
    """
    l = l*1.0E-10 # Angstrom -> meter
    e = constants.physical_constants['atomic unit of charge'][0]
    h = constants.physical_constants['Planck constant'][0]
    p = h/l
    energy = p*p/(2*m)
    return energy/e/1.0E+6

    
def GetVariable(f, var):
    """
    Return the variable value from the CombLayer-generated xml file
    """
    p = subprocess.Popen("getvariable %s %s" % (f, var), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pid = p.pid
    output, error = p.communicate()
    return output
