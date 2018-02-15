#! /usr/bin/python -Qwarn
import sys, getopt, re, string, os
import glob
import tempfile

def usage():
    print main.__doc__

def notsupported():
    printincolor("fluka2root:\tFree-format input is not yet supported.\n\t\tYou might consider writing a feature request at http://readfluka.googlecode.com.")

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
    print "\033[1;%dm%s\033[0m" % (col, s)

def merge_files(thelist, suffix, thecommand, N, M, inpname):
    suwfile = inpname.replace(".inp", "%.3d-%.3d_%s" % (N, M, suffix) )
    temp_path = tempfile.mktemp()
    tmpfile = open(temp_path, "w")

    for f in thelist:
        tmpfile.write("%s\n" % f)
    tmpfile.write("\n")
    tmpfile.write("%s\n" % suwfile)
    tmpfile.close()
    os.system("cat %s" % tmpfile.name)
    command = "cat %s | $FLUTIL/%s" % (tmpfile.name, thecommand)
    printincolor(command)
    return_value = os.system(command)
    if return_value:
        sys.exit(1);
    os.unlink(tmpfile.name)
    command = "%s2root %s" % (thecommand, suwfile)
    printincolor(command)
    return_value = os.system(command)
    if return_value:
        sys.exit(2)
    return "%s.root" % suwfile

def findNM(inpname):
    """
    Find the N and M-numbers used when a FLUKA job with input file 'inpname' was run
    """
    inpname = inpname.replace(".inp", "")
    N = 1
# the same without using glob:
# len([f for f in os.listdir(myPath) 
#     if f.endswith('.tif') and os.path.isfile(os.path.join(myPath, f))])
    M = len(glob.glob1(".", "%s???.out" % inpname))
    return N,M

def main(argv=None):
    """
fluka2root - a script to convert the output of all FLUKA estimators (supported by readfluka) to a single ROOT file.
Usage: There are several ways to run this program:
 1. fluka2root inpfile.inp N M
 \tN - number of previous run plus 1. The default value is 1.
 \tM - number of final run plus 1. The default value is N.
 2. fluka2root inpfile.inp M
 \tN assumed to be 1
 3. fluka2root inpfile.inp
 \tscript will try to guess N and M based on the files inpfile???.out in the current folder
    """
    if argv is None:
        argv = sys.argv

    if len(argv) is 1:
        usage()
        sys.exit(1)

#    printincolor("Note that the corresponding USRBIN histograms from different ROOT files will be summed up but not averaged unless it is implemented in the ROOT's hadd. All the other supported histograms should work fine", 33)

    estimators = {"EVENTDAT" : [], "USRBDX" : [], "USRBIN" : [], "RESNUCLE" : [], "USRTRACK" : []} # dictionary of supported estimators and their file units
#    estimators = {"USRBIN" : [], "USRTRACK" : []} # dictionary of supported estimators and their file units
    opened = {} # dictionary of the opened units (if any)
    out_root_files = [] # list of output ROOT files
    
    inpname = argv[1]

    N,M = findNM(inpname)

#    N = 1
    if len(argv) > 2:
        try:
            N = str2int(argv[2])
        except ValueError:
            print main.__doc__
            sys.exit(1)
#    M = N
    if len(argv) == 4:
        try:
            M = str2int(argv[3])
        except ValueError:
            print main.__doc__
            sys.exit(1)
#    print N, M
#    sys.exit(0)

    inp = open(argv[1], "r")
#    print "Input file: %s" % inpname
    isname = False
    for line in inp.readlines():
        if re.search("\AFREE", line):
            notsupported()
            sys.exit(2)

        if isname is True:
            name = line[0:10].strip()
            opened[str2int(unit)] = name
            isname = False

        if re.search("\AOPEN", line):
            unit = line[11:20].strip()
            isname = True

    if len(opened):
        print "Opened units: ", opened

    inp.seek(0)
    print "Supported estimators:"
    for line in inp.readlines():
        for e in estimators:
            if e == "EVENTDAT": # EVENTDAT card has a different format than the other estimators
                if re.search("\A%s" % e, line):
                    unit = line[10:20].strip()
                    name = "" #line[0:10].strip() # actually, name for EVENTDAT does not matter - the Tree name will be used
#                    print "eventdat: \t", e, unit,name
                    if str2int(unit)<0: # we are interested in binary files only
#                        print "here", e, unit, estimators
                        if not unit in estimators[e]:
#                            print unit
                            estimators[e] = ["%s" % unit]
#                            print estimators
            else:
                if re.search("\A%s" % e, line) and not re.search("\&", line[70:80]):
                    if e == "RESNUCLE":
                        unit = line[20:30].strip()
                    else:
                        unit = line[30:40].strip()
                    name = line[70:80].strip()
#                    print "\t", e, unit, name
                    if str2int(unit)<0: # we are interested in binary files only
                        if not unit in estimators[e]:
                            estimators[e].append(unit)

    print estimators

# Convert units in the file names:
    for e, units in estimators.iteritems():
#        if e == "EVENTDAT":
#            continue
        for u in units:
            iu = str2int(u)
            if iu<0: # we are interested in binary files only
                if iu in opened:
                    units[units.index(u)] = str("_%s" % opened[iu])
                else:
                    units[units.index(u)] = "_fort.%d" % abs(iu)

    print estimators

    inp.close()

# run converters
    return_value = 0
    resnuclei_binary_files = []
    usrbin_binary_files = []
    usrtrack_binary_files = []
    for run in range(N, M+1):
        binfilename = ""
        rootfilenames = []
        command = ""
        for e in estimators:
            for s in estimators[e]:
                binfilename = inpname.replace(".inp", "%.3d%s" % (run, s))
                if os.path.isfile(binfilename):
                    if re.search("RESNUCLE", e): # RESNUCLE = RESNUCLEi = RESNUCLEI
                        e = "RESNUCLEI"
                        resnuclei_binary_files.append(binfilename)
                    elif re.search("USRBIN", e):
#                        print "AAAAAAAAAAAAAAAAAAAAAAA"
                        usrbin_binary_files.append(binfilename)
                    elif re.search("USRTRACK", e):
                        usrtrack_binary_files.append(binfilename)
                    else:
#                        print "HHHHHHHHHHHHHHHHHHHHHHHo%so" % e
                        rootfilenames.append(binfilename + ".root")
                        command =  "%s2root %s" % (e.lower(), binfilename)
                        printincolor(command)
                        return_value = os.system(command)
                        if return_value is not 0:
                            printincolor("ERROR: " % return_value, 33)
                            sys.exit(return_value)
#                        else:
#                            printincolor("WARNING: can't open file %s" % binfilename, 33)

# hadd within one sample
        if len(rootfilenames):
            print "The following ROOT files will be hadded", rootfilenames
            out_root_file = inpname.replace(".inp", "%.3d%s" % (run, ".root"))
            command = "hadd %s %s" % (out_root_file, string.join(rootfilenames))
            printincolor(command)
            return_value = os.system(command)
# remove tmp files
            if return_value is 0:
                command = "rm -f %s" % string.join(rootfilenames)
                printincolor(command)
                return_value = os.system(command)
                if return_value is 0:
                    out_root_files.append(out_root_file)
                else:
                    sys.exit(return_value)

    if len(resnuclei_binary_files): # usrsuw to sum RESNUCLEI
        out_root_files.append(merge_files(resnuclei_binary_files, "resnuclei", "usrsuw", N, M, inpname))

    if len(usrbin_binary_files):
        out_root_files.append(merge_files(usrbin_binary_files, "usrbin", "usbsuw", N, M, inpname))
    if len(usrtrack_binary_files):
        out_root_files.append(merge_files(usrtrack_binary_files, "usrtrack", "ustsuw", N, M, inpname))

    print out_root_files
    if return_value is 0 and len(out_root_files)>1:
        out_root_file = inpname.replace(".inp", ".root");
        command = "hadd %s %s" % (out_root_file, string.join(out_root_files))
        printincolor(command)
        return_value = os.system(command)
        if return_value is 0:
            command = "rm -f %s" % string.join(out_root_files)
            printincolor(command)
            return_value = os.system(command)

    sys.exit(return_value)

if __name__ == "__main__":
    sys.exit(main())
