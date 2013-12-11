#! /usr/bin/python -W all
import sys
from nbmctal import MCTAL
from nbtestsuite import TestSuite

if len(sys.argv) == 3 and sys.argv[2] == "-v":
	verbose = True
else:
	verbose = False

m = MCTAL(sys.argv[1],verbose)
m.Read()

t = TestSuite(m,verbose)
sys.exit(t.Test())

