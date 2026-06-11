#!/usr/bin/env python3
#
# alias fluka2root-dir="parallel 'cd {} && fluka2root *.inp' ::: *"

import sys, re, os, argparse
import glob
import subprocess
from tempfile import NamedTemporaryFile
from shutil import which

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

ESTIMATORS = (("USRBDX",   "usxsuw"),
              ("USRBIN",   "usbsuw"),
              ("USRCOLL",  "ustsuw"),
              ("USRTRACK", "ustsuw"),
              ("DETECT",   "detsuw"),
              ("USRYIELD", "usysuw"),
              ("RESNUCLE", "usrsuw"))

class Converter:
    def __init__(self, args):
        self.inp        = args.inp # all input files
        self.overwrite  = args.overwrite
        self.verbose    = args.verbose
        self.keep       = args.keep
        self.clean      = args.clean
        self.parallel   = which("parallel") is not None
        self.njobs      = args.njobs
        self.estimators = [Estimator(name, converter) for name, converter in ESTIMATORS]
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
        self.validateDataFiles()
        self.validateExecutables()

        if self.verbose:
            print("input files:", self.inp)
            print("output ROOT file:", self.root)

    def Clean(self):
        if self.verbose:
            print("Cleaning tmp files...")
        for f in self.inp:
            n = "[0-9][0-9][0-9]"
            inp = os.path.splitext(f)[0]
            basename = inp + n
            patterns = []
            patterns.append("ran"+basename)
            patterns.append(basename + ".err")
            patterns.append(inp + ".error")
            patterns.append(inp + ".output")
            patterns.append(inp + ".slurm")
            patterns.append(basename + ".log")
            patterns.append(basename + ".out")
            patterns.append(basename + "_fort.*")
            for pattern in patterns:
                for path in glob.glob(pattern):
                    if self.verbose:
                        printincolor("rm -f %s" % path)
                    os.unlink(path)

    def getROOTFileName(self):
        """ Generate the output ROOT file name based on the input files """
        root = os.path.splitext(self.inp[0])[0]+".root"
        if len(self.inp)>1:
            root = re.sub(r'[0-9]+\.root','.root', root)
        if root == '.root':
            root = self.inp[0][0]+root
        return os.path.basename(root)

    def checkInputFiles(self):
        """Do some checks of the input files

           - check if all input files exist
           - check whether input follows the standard Fluka format (free format is not supported)
        """
        if self.verbose:
            print("Checking input files...")

        for f in self.inp:
            if not os.path.isfile(f):
                print("Error: %s does not exist" % f, file=sys.stderr)
                return 1

        for input_file in self.inp:
            with open(input_file) as f:
                for line in f.readlines():
                    if re.search(r"\AFREE", line):
                        print("Error:\tFree-format input is not supported in %s." % input_file, file=sys.stderr)
                        return 2

        return 0

    def getRunTitle(self):
        """ Return the run title as specified in the first provided input file

        """

        found = False
        with open(self.inp[0]) as f:
            for line in f:
                line = line.strip()
                if found:
                    return line
                if line.startswith("TITLE"):
                    found = True

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
        return self.getOpenedUnitsForInput(self.inp[0])

    def getOpenedUnitsForInput(self, input_file):
        inp = open(input_file, "r")
        isname = False
        opened = {}
        for line in inp.readlines():
            if isname is True:
                name = line.strip()
                opened[unit] = name
                isname = False

            if re.search(r"\AOPEN", line) and line.split()[-1] == "NEW": # NEW: interested only in the newly created files where the estimator output is written
                unit = str2int(line[11:20].strip())
                isname = True

        inp.close()

        if len(opened):
            print("Opened (named) units: ", opened)

        return opened

    def createEstimators(self):
        return [Estimator(name, converter) for name, converter in ESTIMATORS]

    def parseEstimators(self, input_file):
        opened = self.getOpenedUnitsForInput(input_file)
        if len(opened):
            units = ", ".join("%s=%s" % (unit, name) for unit, name in opened.items())
            sys.exit("Opened units not yet supported in %s: %s" % (input_file, units))

        estimators = self.createEstimators()
        with open(input_file, "r") as inp:
            for line in inp.readlines():
                for e in estimators:
                    if e.name == "EVENTDAT": # EVENTDAT card has a different format than the other estimators
                        if re.search(r"\A%s" % e.name, line):
                            unit = str2int(line[10:20].strip())
                            if unit<0: # we are interested in binary files only
                                if not unit in e.units:
                                    e.addUnit(unit)
                    elif e.name == "DETECT":
                        if re.search(r"\A%s" % e.name, line):
                            unit = 17
                            if not unit in e.units:
                                e.addUnit(unit)
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
        return estimators

    def estimatorMap(self, estimators):
        return {e.name: sorted(e.units.keys()) for e in estimators if len(e.units)}

    def assignUnits(self):
        """Assigns units to estimators
        """
        if self.verbose:
            print("Assigning units to estimators...")

        self.estimators = self.parseEstimators(self.inp[0])
        reference = self.estimatorMap(self.estimators)
        for input_file in self.inp[1:]:
            current = self.estimatorMap(self.parseEstimators(input_file))
            if current != reference:
                print("Error: estimator/unit layout differs between input files.", file=sys.stderr)
                print("%s: %s" % (self.inp[0], reference), file=sys.stderr)
                print("%s: %s" % (input_file, current), file=sys.stderr)
                sys.exit(4)

    def assignFileNames(self):
        """Assign file names to units
        """
        if self.verbose:
            print("Assigning file names to units...")

        for e in self.estimators:
            for u in e.units:
                for inp in self.inp:
                    pattern = "%s[0-9][0-9][0-9]_fort.%d" % (os.path.splitext(inp)[0], abs(u))
                    for f in sorted(glob.glob(pattern)):
                        if f not in e.units[u]: # TODO: why do we need this check?
                            e.addFile(u,f)

    def validateExecutables(self):
        missing = []
        if which("mc-tools-fluka-merge") is None:
            missing.append("mc-tools-fluka-merge")

        if "FLUPRO" not in os.environ:
            missing.append("FLUPRO environment variable")
        else:
            converters = sorted(set(e.converter for e in self.estimators if len(e.units)))
            for converter in converters:
                merge_tool = os.path.join(os.environ["FLUPRO"], "flutil", converter)
                if not os.path.isfile(merge_tool):
                    missing.append(merge_tool)

        if which("hadd") is None:
            missing.append("hadd")

        for converter in sorted(set(e.converter for e in self.estimators if len(e.units))):
            if which(converter + "2root") is None:
                missing.append(converter + "2root")

        if self.parallel and which("parallel") is None:
            missing.append("parallel")

        if missing:
            print("Error: missing required tools:", file=sys.stderr)
            for item in missing:
                print("  %s" % item, file=sys.stderr)
            sys.exit(5)

    def validateDataFiles(self):
        missing = []
        has_units = False
        for e in self.estimators:
            for u in e.units:
                has_units = True
                if not e.units[u]:
                    missing.append("%s unit %d" % (e.name, u))
        if not has_units:
            print("fluka2root: no datafiles found -> exit")
            print("            Have you defined any estimators?")
            sys.exit(3)
        if missing:
            print("Error: no FLUKA binary files found for:", file=sys.stderr)
            for item in missing:
                print("  %s" % item, file=sys.stderr)
            sys.exit(6)

    def runCommand(self, args, stdout=None):
        if self.verbose:
            printincolor(" ".join(args))
        return subprocess.run(args, stdout=stdout).returncode

    def Merge(self):
        """ Merge all data with standard FLUKA tools
        """
        if self.verbose:
            print("Merging data files...")

        tmpfiles=[]
        try:
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

            stdout = None if self.verbose else subprocess.DEVNULL
            if self.parallel:
                command = ["parallel"]
                if self.njobs > 0:
                    command += ["-j", str(self.njobs)]
                command += ["--max-args=1", "mc-tools-fluka-merge", ":::"]
                command += tmpfiles
                return_value = self.runCommand(command, stdout=stdout)
                if return_value:
                    sys.exit(2)
            else:
                for f in tmpfiles:
                    return_value = self.runCommand(["mc-tools-fluka-merge", f], stdout=stdout)
                    if return_value:
                        sys.exit("Could not merge an estimator")
        finally:
            if not self.keep:
                for f in tmpfiles:
                    if os.path.exists(f):
                        os.unlink(f)

    def Convert(self):
        """Convert merged files into ROOT
        """
        if self.verbose:
            print("Converting to ROOT...")

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
                command = ["parallel"]
                if self.njobs > 0:
                    command += ["-j", str(self.njobs)]
                command += ["--max-args=1", e.converter + "2root"]
                if v:
                    command.append(v)
                command += ["{}", ":::"]
                command += datafiles
                return_value = self.runCommand(command)
                if return_value:
                    sys.exit(2)
            else:
                for u in e.units:
                    suwfile = self.getSuwFileName(e,u)
                    rootfile = suwfile + ".root"
                    command = [e.converter + "2root"]
                    if v:
                        command.append(v)
                    command += [suwfile, rootfile]
                    return_value = self.runCommand(command)
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
        command = ["hadd"]
        if f:
            command.append(f)
        command += [self.root] + self.out_root_files
        stdout = None if self.verbose else subprocess.DEVNULL
        return_value = self.runCommand(command, stdout=stdout)
        if return_value == 0 and not self.keep:
            for f in self.out_root_files + [item for sublist in self.datafiles for item in sublist]:
                if os.path.exists(f):
                    if self.verbose:
                        printincolor("rm -f %s" % f)
                    os.unlink(f)

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
    parser.add_argument('-j', default=0, dest='njobs', type=int, help='Run n jobs in parallel (valid only if the GNU parallel script is available)')

    args = parser.parse_args()

    c = Converter(args)
    c.Merge()
    val = c.Convert()
#    print(c.root)

#    title = c.getRunTitle()

    return val



if __name__ == "__main__":
    sys.exit(main())
