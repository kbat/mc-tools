#!/usr/bin/env python3
#
# A helper script to submit PHITS jobs to a cluster
# Usage: submit.sh inputfile njobs command [arguments]
#
# Each job is submitted from a separate folder, so remember to use '../' with the file names, e.g.
#      submit.sh inp.phits 100 llsubmit ../single.job
# 

from sys import argv, exit
from os  import system

if len(argv)<4:
	print("wrong usage")
	exit(100)

command = argv[3:]
njobs = int(argv[2])
inp = argv[1]
prefix = 'dir'

if system("test -e %s" % inp):
	print("input file '%s' not found" % inp)
	exit(1)

if njobs<=0:
	print("number of jobs must be positive: %d" % njobs)
	exit(2)

if system("grep rseed %s" % inp):
	print("Error: rseed must be negative in the input file '%s'" % inp)
	exit(3)

for i in range(njobs):
	dir = "%s%.3d" % (prefix, i)
	print(dir)
	if system("mkdir %s" % dir): exit(4)
        if system("cp %s %s" % (inp, dir)): exit(6)
        if system("cd %s && %s" % (dir, ' '.join(command))):
		print("Error: can't submit job")
		exit(7)
