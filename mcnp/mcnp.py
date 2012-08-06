#! /usr/bin/python
import re

def getPar(masterfile, parname, pos=3):
    """
    Return parameter 'parname' from MCNP master file 'masterfile' (the syntax of pstudy is assumed)
    pos - optional argument, specifies the position of the value in the THEparname string
    """
    f = open(masterfile)
    for line in f.readlines():
        if re.search("\AC THE%s" % parname, line):
            val = float(line.split()[pos])
#            print line.strip(), val
    f.close()
    return val
