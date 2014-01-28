#! /usr/bin/python -W all
import sys, argparse
from nbmctal import MCTAL
from nbroottestsuite import RootTest

def main():
	"""
	A script to test how we are able to read and convert the mctal file structure to the ROOT format. It reads the original mctal file into a binary object, then reads back the ROOT file geenrated with nbmctal2root.py, generates a test mctal file based on the contents retrieved from the ROOT file and compares the two files (the original mctal and the reproduced one) using GNU diffutils.
	Exit status is 0 if both files are the same, 1 if different.
	"""
	
	parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: http://code.google.com/p/mc-tools")
	parser.add_argument('mctal_file', type=str, help='The name (and path) to the mctal file to be converted')
	parser.add_argument('root_file', type=str, nargs='?', help='The name of the converted ROOT file', default="")
	parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Explain what is being done')

	arguments = parser.parse_args()

	m = MCTAL(arguments.mctal_file, arguments.verbose)
	m.Read()

	if not m.thereAreNaNs:

		if arguments.root_file == "":
        		rootFileName = "%s%s" % (arguments.mctal_file,".root")
		else:
		        rootFileName = arguments.root_file

		r = RootTest(m,rootFileName,arguments.verbose)
		return r.Test()

	else:

		print >> sys.stderr, " \033[31mTest on MCTAL file %s was skipped due to NaN values\033[0m\n" % arguments.mctal_file
		sys.exit(1)


if __name__ == "__main__":
	sys.exit(main())
