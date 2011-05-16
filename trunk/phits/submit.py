#! /usr/bin/python -W all

from sys import argv, exit
from os  import system

njobs = int(argv[1])
inp = argv[2]
prefix = 'dir'
submit_command = 'submit.sh 1'

if system("grep rseed %s" % inp):
	print "Error: rseed must be negative in the input file '%s'" % inp
	exit(1)

for i in range(njobs):
	dir = "%s%.3d" % (prefix, i)
	print dir
	if system("mkdir %s" % dir): exit(4)
        if system("cp %s %s" % (inp, dir)): exit(3)
        system("cd %s && echo file = %s > phits.in && %s phits \< phits.in" % (dir, inp, submit_command))
