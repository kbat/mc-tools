#! /usr/bin/python -W all

from sys import argv, exit
from os  import system

job_file = argv[1]
njobs = int(argv[2])
inp = argv[3]
prefix = 'dir'

if system("grep rseed %s" % inp):
	print "Error: rseed must be negative in the input file '%s'" % inp
	exit(1)

for i in range(njobs):
	dir = "%s%.3d" % (prefix, i)
	print dir
	if system("mkdir %s" % dir): exit(4)
        if system("cp %s %s" % (inp, dir)): exit(3)
        system("cd %s && llsubmit ../%s" % (dir, job_file))
