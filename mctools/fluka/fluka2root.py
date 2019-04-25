#! /usr/bin/python -Qwarn
from __future__ import print_function
import sys, re, os, argparse
import glob
import tempfile

def str2int(s):
    try:
        ret = int(s)
    except ValueError:
        ret = int(float(s))
    return ret

def printincolor(s,col=33):
    """
    Print a string with a given color using ANSI/VT100 Terminal Control Escape Sequences
    http://www.termsys.demon.co.uk/vtansi.htm
    """
    print("\033[1;%dm%s\033[0m" % (col, s))


class Estimator:
    def __init__(self, name, converter):
        self.name = name
        self.converter = converter
        self.units = {} # dictionary of units corresponding files

    def addUnit(self, u):
        """ Adds a key with the given unit in the units dictionary
        """
        self.units[u] = []

    def addFile(self, u, f):
        """ Adds the given file name to the unit
        """
        self.units[u].append(f)

    def Print(self):
        print(self.name)
        print(" ", self.converter)
        print(" units: ", self.units)

class Converter:
    def __init__(self, inp, overwrite, verbose):
        self.inp = inp # input files
        self.overwrite = overwrite
        self.verbose = verbose
        self.estimators = [Estimator("USRBIN",   "usbsuw"),
                           Estimator("USRBDX",   "usxsuw"),
                           Estimator("USRTRACK", "ustsuw")]
        self.opened = {}         # dict of opened units (if any)

        self.out_root_files = [] # list of output ROOT files

        # Generate the output root file name:
        self.root = os.path.splitext(self.inp[0])[0]+".root"
        self.root = re.sub(r'[0-9]+\.root','.root', self.root)
        self.basename = os.path.splitext(self.root)[0]
        
        if not self.overwrite and os.path.isfile(self.root):
            sys.exit("Can't overwrite %s. Remove it or use the '-f' argument." % self.root)

        if self.checkInputFiles():
            sys.exit(1)

        self.assignUnits()
        self.assignFileNames()
        return 

        if self.verbose:
            print("input files:", self.inp)
            print("output ROOT files:", self.root)

    def checkInputFiles(self):
        """Does some checks of the input files

           - check if all input files exist
           - check whether input follows the standard Fluka format (free format is not supported)
        """

        for f in self.inp:
            if not os.path.isfile(f):
                print("Error: %s does not exist" % f, sys=sys.stderr)
                return 1

        with open(self.inp[0]) as f:
            for line in f.readlines():
                if re.search("\AFREE", line):
                    print("Error:\tFree-format input is not supported.", sys=sys.stderr)
                    return 2
                    
        return 0

    def getSuwFileName(self, e, u):
        """Reuturn suw file name for the given estimator
        Parameters:
        e: estimator
        u: unit
        """
        return "%s.%d.%s" % (os.path.splitext(self.inp[0])[0], abs(u), e.name.lower())

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
                print("Opened (named) units: ", opened)
        inp.close()
    
        return opened

    def assignUnits(self):
        """Assigns units to estimators
        """
        self.opened = self.getOpenedUnits()
        if len(self.opened):
            sys.exit("Opened units not yet supported")

        inp = open(self.inp[0], "r")
        for line in inp.readlines():
            for e in self.estimators:
                if e.name == "EVENTDAT": # EVENTDAT card has a different format than the other estimators
                    if re.search("\A%s" % e.name, line):
                        unit = str2int(line[10:20].strip())
                        name = "" #line[0:10].strip() # actually, name for EVENTDAT does not matter - the Tree name will be used
                        if unit<0: # we are interested in binary files only
                            if not unit in self.estimators[e]:
                                self.estimators[e].addUnit("%s" % unit)
                else:
                    if re.search("\A%s" % e.name, line) and not re.search("\&", line[70:80]):
                        if e.name == "RESNUCLE":
                            unit = line[20:30]
                        else:
                            unit = line[30:40]
                        unit = str2int(unit.strip())
                        name = line[70:80].strip()
                        if unit<0: # we are interested in binary files only
                            if not unit in e.units:
                                e.addUnit(unit)
                        else:
                            print("Warning: ascii files not supported", unit, name, sys=sys.stderr)
        inp.close()

    def assignFileNames(self):
        """Assign file names to units
        """
        for e in self.estimators:
            for u in e.units:
                for f in glob.glob("%s*_fort.%d" % (self.basename, abs(u))):
                    e.addFile(u,f)
                    
    def Merge(self):
        """ Merge all data with standard FLUKA tools
        """
        if self.verbose:
            print("Merging...")
        
        for e in self.estimators:
            if not len(e.units):
                continue

            for u in e.units:
                temp_path = tempfile.mktemp()
                if self.verbose:
                    print(e.name, temp_path)
                with open(temp_path, "w") as tmpfile:
                    suwfile = self.getSuwFileName(e,u)
                    if self.verbose:
                        print(suwfile)

                    for f in e.units[u]:
                        tmpfile.write("%s\n" % f)
                    
                    tmpfile.write("\n")
                    tmpfile.write("%s\n" % suwfile)

                verbose = "" if self.verbose else ">/dev/null"
                #os.system("cat %s %s" % (tmpfile.name, verbose))
            
                command = "cat %s | $FLUTIL/%s %s" % (tmpfile.name, e.converter, verbose)
                if self.verbose:
                    printincolor(command)
                
                return_value = os.system(command)
                if return_value:
                    sys.exit(printincolor("Coult not convert %s" % e.name));
                
                if not self.verbose:
                    os.unlink(tmpfile.name)

    def Convert(self):
        """Convert merged files into ROOT
        """
        if self.verbose:
            print("Converting...")

        v = "-v" if self.verbose else ""
            
        for e in self.estimators:
            if not len(e.units):
                continue

            for u in e.units:
                suwfile = self.getSuwFileName(e,u)
                rootfile = suwfile + ".root"
                command = "%s2root %s %s %s" % (e.converter, v , suwfile, rootfile)
                if self.verbose:
                    printincolor(command)
                return_value = os.system(command)
                if return_value:
                    sys.exit(2)

                self.out_root_files.append(rootfile)

        if self.verbose:
            print("ROOT files produced: ", self.out_root_files)

        f = "-f" if self.overwrite else ""
        command = "hadd %s %s %s" % (f, self.root, ' '.join(self.out_root_files)) + (" > /dev/null" if self.verbose else "")
        if self.verbose:
            printincolor(command)
        return_value = os.system(command)
        if return_value is 0:
            command = "rm -f %s %s" % (v, ' '.join(self.out_root_files))
            if self.verbose:
                printincolor(command)
            return_value = os.system(command)

        return return_value

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
    val = c.Convert()

    return val



if __name__ == "__main__":
    sys.exit(main())
