#! /usr/bin/python -W all
import sys, argparse
from mctools.mcnp.mctal import MCTAL
from mctools.mcnp.testsuite import TestSuite

def main():
	"""
	A script to test how we are able to read and reproduce the mctal file structure. It reads the original mctal file into a binary object, generates another mctal file based on this object and then compares both files using GNU diffutils.
	Exit status is 0 if both files are the same, 1 if different.
	"""
	parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: https://github.com/kbat/mc-tools")
	parser.add_argument('-v', '--verbose', action='store_true',  default=False, dest='verbosity', help='explain what is being done')
	parser.add_argument('mctal', type=str, help='mctal file to use for test')

	arguments = parser.parse_args()

	m = MCTAL(arguments.mctal, arguments.verbosity)
	m.Read()

	t = TestSuite(m, arguments.verbosity)
	return t.Test()


if __name__ == "__main__":
	sys.exit(main())
