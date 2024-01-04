#!/usr/bin/env python3
#
# alias fluka2root-dir="parallel 'cd {} && fluka2root *.inp' ::: *"

import sys, re, os, argparse
import glob
from tempfile import NamedTemporaryFile
from distutils.spawn import find_executable

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
        self.units = {} # dictionary of units and corresponding files

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

    def __str__(self):
        return self.name+" "+self.converter+" "+str(self.units)

class Converter:
    def __init__(self, args):
        self.inp        = args.inp # all input files
        self.overwrite  = args.overwrite
        self.verbose    = args.verbose
        self.keep       = args.keep
        self.clean      = args.clean
        self.parallel   = find_executable("parallel") is not None
        self.estimators = [Estimator("USRBIN",   "usbsuw"),
                           Estimator("USRBDX",   "usxsuw"),
                           Estimator("USRTRACK", "ustsuw"),
                           Estimator("RESNUCLE", "usrsuw")]
        self.opened = {}         # dict of opened units (if any)

        self.out_root_files = [] # list of output ROOT files
        self.datafiles = [] # list of data files (to delete)

        # Generate the output root file name:
        self.root  = self.getROOTFileName()
        self.basename = os.path.splitext(self.root)[0]

        if not self.overwrite and os.path.isfile(self.root):
            sys.exit("Can't overwrite %s. Remove it or use the '-f' argument." % self.root)

        if self.checkInputFiles():
            sys.exit("Input file check failed")

        self.assignUnits()
        self.assignFileNames()

        if self.verbose:
            print("input files:", self.inp)
            print("output ROOT file:", self.root)

    def Clean(self):
        v = "-v" if self.verbose else ""
        for f in self.inp:
            n = "[0-9][0-9][0-9]"
            inp = os.path.splitext(f)[0]
            basename = inp + n
            vec = []
            vec.append("ran"+basename)
            vec.append(basename + ".err")
            vec.append(inp + ".error")
            vec.append(inp + ".output")
            vec.append(inp + ".slurm")
            vec.append(basename + ".log")
            vec.append(basename + ".out")
            vec.append(basename + "_fort.*")
            for c in vec:
                command = "rm -f %s %s " % (v, c)
                if self.verbose:
                    printincolor(command)
                os.system(command)

    def getROOTFileName(self):
        """ Generate the output ROOT file name based on the input files """
        root = os.path.splitext(self.inp[0])[0]+".root"
        if len(self.inp)>1:
            root = re.sub(r'[0-9]+\.root','.root', root)
        return os.path.basename(root)

    def checkInputFiles(self):
        """Does some checks of the input files

           - check if all input files exist
           - check whether input follows the standard Fluka format (free format is not supported)
        """

        for f in self.inp:
            if not os.path.isfile(f):
                print("Error: %s does not exist" % f, file=sys.stderr)
                return 1

        with open(self.inp[0]) as f:
            for line in f.readlines():
                if re.search(r"\AFREE", line):
                    print("Error:\tFree-format input is not supported.", file=sys.stderr)
                    return 2

        return 0

    def getSuwFileName(self, e, u):
        """Reuturn suw file name for the given estimator
        Parameters:
        e: estimator
        u: unit
        """
        return "%s.%d.%s" % (self.basename, abs(u), e.name.lower())

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

            if re.search(r"\AOPEN", line):
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
                    if re.search(r"\A%s" % e.name, line):
                        unit = str2int(line[10:20].strip())
                        name = "" #line[0:10].strip() # actually, name for EVENTDAT does not matter - the Tree name will be used
                        if unit<0: # we are interested in binary files only
                            if not unit in self.estimators[e]:
                                self.estimators[e].addUnit("%s" % unit)
                else:
                    if re.search(r"\A%s" % e.name[:8], line) and not re.search(r"\&", line[70:80]):
                        if e.name[:8] == "RESNUCLE":
                            unit = line[20:30]
                        else:
                            unit = line[30:40]
                        unit = str2int(unit.strip())
                        name = line[70:80].strip()
                        if unit<0: # we are interested in binary files only
                            if not unit in e.units:
                                e.addUnit(unit)
                        else:
                            print("Warning: text output files are not supported", unit, name, file=sys.stderr)
        inp.close()

    def assignFileNames(self):
        """Assign file names to units
        """
        for e in self.estimators:
            for u in e.units:
                for inp in self.inp:
                    for f in glob.glob("%s[0-9][0-9][0-9]_fort.%d" % (os.path.splitext(inp)[0], abs(u))):
                        if f not in e.units[u]: # TODO: this can be done smarter
                            e.addFile(u,f)

    def Merge(self):
        """ Merge all data with standard FLUKA tools
        """
        if self.verbose:
            print("Merging...")

        tmpfiles=[]
        for e in self.estimators:
            if not len(e.units):
                continue

            for u in e.units:
                with NamedTemporaryFile(suffix="."+e.converter, mode="w", delete=False) as tmpfile:
                    if self.verbose:
                        print("unit=%d" % u, e.name, tmpfile.name)
                    suwfile = self.getSuwFileName(e,u)
                    if self.verbose:
                        print(suwfile)

                    for f in e.units[u]:
                        tmpfile.write("%s\n" % f)

                    tmpfile.write("\n")
                    tmpfile.write("%s\n" % suwfile)

                    tmpfiles.append(tmpfile.name)

        verbose = "" if self.verbose else ">/dev/null"
        if self.parallel:
            command="parallel --max-args=1 mc-tools-fluka-merge ::: " + " ".join(tmpfiles) + verbose
            if self.verbose:
                printincolor(command)
            return_value = os.system(command)
            if return_value:
                sys.exit(2)
        else:
            for f in tmpfiles:
                command = "mc-tools-fluka-merge %s %s" % (f, verbose)
                if self.verbose:
                    printincolor(command)
                return_value = os.system(command)
                if return_value:
                    sys.exit(printincolor("Coult not convert an estimator"));

        if not self.keep:
            for f in tmpfiles:
                os.unlink(f)

    def Convert(self):
        """Convert merged files into ROOT
        """
        if self.verbose:
            print("Converting...")

        v = "-v" if self.verbose else ""

        for e in self.estimators:
            if not len(e.units):
                continue

            datafiles = []
            for u in e.units:
                suwfile = self.getSuwFileName(e,u)
                rootfile = suwfile + ".root"
                self.out_root_files.append(rootfile)
                datafiles.append(suwfile)

            if self.parallel:
                command="parallel --max-args=1 %s2root %s {} ::: %s" % (e.converter,v,' '.join(datafiles))
                if self.verbose:
                    printincolor(command)
                return_value = os.system(command)
                if return_value:
                    sys.exit(2)
            else:
                for u in e.units:
                    suwfile = self.getSuwFileName(e,u)
                    rootfile = suwfile + ".root"
                    command = "%s2root %s %s %s" % (e.converter, v , suwfile, rootfile)
                    if self.verbose:
                        printincolor(command)
                    return_value = os.system(command)
                    if return_value:
                        sys.exit(2)
            self.datafiles.append(datafiles)

        if len(self.datafiles) == 0:
            print("fluka2root: no datafiles found -> exit")
            print("            Have you defined any estimators?")
            sys.exit(3)

        if self.verbose:
            print("ROOT files produced: ", self.out_root_files)


        f = "-f" if self.overwrite else ""
        command = "hadd %s %s %s" % (f, self.root, ' '.join(self.out_root_files)) + ("" if self.verbose else " > /dev/null")
        if self.verbose:
            printincolor(command)
        return_value = os.system(command)
        if return_value == 0 and not self.keep:
            command = "rm -f %s %s" % (v, ' '.join(self.out_root_files + [item for sublist in self.datafiles for item in sublist]))
            if self.verbose:
                printincolor(command)
            return_value = os.system(command)

        if self.clean:
            if return_value == 0:
                self.Clean()
            elif self.verbose:
                print("Warning: FLUKA output files not deleted since the previous command did not return 0")

        return return_value

def main():
    """fluka2root - a script to convert the output of some FLUKA estimators (supported by the mc-tools project) into a single ROOT file.
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('inp', type=str, nargs="+", help='FLUKA input file(s). If multiple files are given, the script will assume the input files differ only in the random seed and average all corresponding data files.')
    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite', help='overwrite the output ROOT files produced by hadd')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')
    parser.add_argument('-keep', '--keep-files', action='store_true', default=False, dest='keep', help='do not delete temporary files')
    parser.add_argument('-clean', action='store_true', default=False, dest='clean', help='remove FLUKA-generated data files')

    args = parser.parse_args()

    c = Converter(args)
    c.Merge()
    val = c.Convert()
    print(c.root)

    return val



if __name__ == "__main__":
    sys.exit(main())
