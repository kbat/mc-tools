#! /usr/bin/python -Qwarn
import sys, re, string, os, argparse
import glob
import tempfile

def str2int(s):
    try:
        ret = int(s)
    except ValueError:
        ret = int(float(s))
    return ret

class Converter:
    def __init__(self, inp, overwrite, verbose):
        self.inp = inp # input files
        self.overwrite = overwrite
        self.verbose = verbose
        # dict of supported estimators and their file units
        self.estimators = {"USRBIN" : [], "USRBDX" : []}
        # dict of estimators and their file names
        # todo make a copy of self.estimators
        self.files = {"USRBIN" : [], "USRBDX" : []}
        self.converters = {"USRBIN" : ["usbsuw", "bnn"], "USRBDX" : ["usxsuw", "bnn"], "USRTRACK" : ["ustsuw", "bnn"]}
        self.opened = {}         # dict of opened units (if any)
        self.out_root_files = [] # list of output ROOT files

        # Generate the output root file name:
        # todo: mv out_root_file to root
        self.out_root_file = os.path.splitext(inp[0])[0]+".root"
        self.out_root_file = re.sub(r'[0-9]+\.root','.root', self.out_root_file)
        
        if not self.overwrite and os.path.isfile(self.out_root_file):
            sys.exit("Can't overwrite %s. Remove it or use the '-f' argument." % self.out_root_file)

        if self.checkInputFiles():
            sys.exit(1)

        self.assignUnits()
        self.assignFileNames()
            
        print self.inp
        print self.out_root_file
        print "estimators: ", self.estimators
        print "files: ", self.files

    def checkInputFiles(self):
        """Does some checks of the input files

           - check if all input files exist
           - check whether input follows standard Fluka format (free format is not supported)
        """

        for f in self.inp:
            if not os.path.isfile(f):
                print>>sys.stderr, "Error: %s does not exist" % f
                return 1

        with open(self.inp[0]) as f:
            for line in f.readlines():
                if re.search("\AFREE", line):
                    sys.exit("Error:\tFree-format input is not supported.")
                    
        return 0

    def getOpenedUnits(self):
        """Get the list of opened (named) units
        """
    
        inp = open(self.inp[0], "r")
        isname = False
        opened = []
        for line in inp.readlines():
            if isname is True:
                name = line[0:10].strip()
                opened[unit] = name
                isname = False

            if re.search("\AOPEN", line):
                unit = str2int(line[11:20].strip())
                isname = True

            if len(opened):
                print "Opened (named) units: ", opened
        inp.close()
    
        return opened

    def assignUnits(self):
        """Assigns units to estimators
        """
        opened = self.getOpenedUnits()

        inp = open(self.inp[0], "r")
        if self.verbose:
            print "Supported estimators:"
        for line in inp.readlines():
            for e in self.estimators:
                if e == "EVENTDAT": # EVENTDAT card has a different format than the other estimators
                    if re.search("\A%s" % e, line):
                        unit = line[10:20].strip()
                        name = "" #line[0:10].strip() # actually, name for EVENTDAT does not matter - the Tree name will be used
                        if str2int(unit)<0: # we are interested in binary files only
                            if not unit in self.estimators[e]:
                                self.estimators[e] = ["%s" % unit]
                else:
                    if re.search("\A%s" % e, line) and not re.search("\&", line[70:80]):
                        if e == "RESNUCLE":
                            unit = line[20:30].strip()
                        else:
                            unit = line[30:40].strip()
                        name = line[70:80].strip()
                        if str2int(unit)<0: # we are interested in binary files only
                            if not unit in self.estimators[e]:
                                self.estimators[e].append(unit)
        inp.close()
        # Convert units in the file names:
        # todo: is this piece of code really needed - it is never used!
        for e, units in self.estimators.iteritems():
            #        if e == "EVENTDAT":
            #            continue
            for u in units:
#                print u
                iu = str2int(u)
                if iu<0: # we are interested in binary files only
                    if opened and iu in opened:
                        units[units.index(u)] = str("_%s" % opened[iu])
                    else:
                        units[units.index(u)] = "_fort.%d" % abs(iu)

    def assignFileNames(self):
        """Assign file names to units
        """
        print " lists of files:"
        for e in self.estimators:
            for u in self.estimators[e]:
                for f in glob.glob("*%s" % u):
                    self.files[e].append(f)

    def mergeFiles(self, suffix, command):
        """ Merge data from different runs with standard FLUKA tools for the given estimator
        """
        suwfile = os.path.splitext(self.inp[0])[0]+"."+suffix
        print suwfile

        temp_path = tempfile.mktemp()
        print temp_path
        tmpfile = open(temp_path, "w")

                    
    def Merge(self):
        """ Merge all data
        """
        print "Merging..."
        print self.files
        for f in self.files:
            print f
        self.mergeFiles("usrbin", "usxsuw")
        



def main():
    """fluka2root - a script to convert the output of some FLUKA estimators (supported by the mc-tools project) into a single ROOT file.
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('inp', type=str, nargs="+", help='FLUKA input file(s). If one file is given, the script will average the runs between N and M. If multiple files are given, the script will assume there is one run with each input file and average all corresponding data files.')
    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite', help='overwrite the output ROOT files produced by hadd')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')

    args = parser.parse_args()

    c = Converter(args.inp, args.overwrite, args.verbose)
    c.Merge()



if __name__ == "__main__":
    sys.exit(main())
