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

def printincolor(s,col=33):
    """
    Print a string with a given color using ANSI/VT100 Terminal Control Escape Sequences
    http://www.termsys.demon.co.uk/vtansi.htm
    """
    print "\033[1;%dm%s\033[0m" % (col, s)

def merge_files(thelist, suffix, thecommand, N, M, args):
    inpname = args.inp
    suwfile = inpname.replace(".inp", "%.3d-%.3d_%s" % (N, M, suffix) )
    temp_path = tempfile.mktemp()
    tmpfile = open(temp_path, "w")

    for f in thelist:
        tmpfile.write("%s\n" % f)
    tmpfile.write("\n")
    tmpfile.write("%s\n" % suwfile)
    tmpfile.close()
    verbose = "" if args.verbose else ">/dev/null"
    os.system("cat %s %s" % (tmpfile.name, verbose))
    command = "cat %s | $FLUTIL/%s %s" % (tmpfile.name, thecommand, verbose)
    if args.verbose:
        printincolor(command)
    return_value = os.system(command)
    if return_value:
        sys.exit(1);
    os.unlink(tmpfile.name)
    command = "%s2root %s.bnn %s.root" % (thecommand, suwfile, suwfile)
    if args.verbose:
        printincolor(command)
    return_value = os.system(command)
    if return_value:
        sys.exit(2)
    return "%s.root" % suwfile

def findNM(inpname):
    """
    Find the N and M-numbers used when a FLUKA job with input file 'inpname' was run
    """
    return 1,len(glob.glob1(".", "%s???.out" % os.path.splitext(inpname)[0]))

def main():
    """
    fluka2root - a script to convert the output of all FLUKA estimators (supported by the mc-tools project) into a single ROOT file.
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('inp', type=str, help='FLUKA input file')
    parser.add_argument('-N',  dest='N',  type=int, help='number of previous run plus 1 (1 if omitted)', required=False, default=-1)
    parser.add_argument('-M',  dest='M',  type=int, help='number of final run plus 1 (if omitted, guessed based on the files in the current folder)', required=False, default=-1)
    parser.add_argument('-f', action='store_true', default=False, dest='force_overwrite', help='overwrite the ROOT files produced by hadd')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')

    args = parser.parse_args()

    out_root_file = os.path.splitext(args.inp)[0]+".root"
    if not args.force_overwrite and os.path.isfile(out_root_file):
        sys.exit("Can't overwrite %s. Remove it or use the '-f' argument." % out_root_file)

    #    estimators = {"EVENTDAT" : [], "USRBDX" : [], "USRBIN" : [], "RESNUCLE" : [], "USRTRACK" : []} # dictionary of supported estimators and their file units
    estimators = {"USRBIN" : [], "USRBDX" : []} # dictionary of supported estimators and their file units
    opened = {} # dictionary of the opened units (if any)
    out_root_files = [] # list of output ROOT files
    
    # guess N and M from the output file
    N,M = findNM(args.inp)

    if args.N>0:
        N = args.N

    if args.M>0:
        M = args.M

    if N>=M:
        sys.exit("Error: M>=N")

    inp = open(args.inp, "r")
    isname = False
    for line in inp.readlines():
        if re.search("\AFREE", line):
            sys.exit("fluka2root:\tFree-format input is not supported.")

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
    if args.verbose:
        print "Supported estimators:"
    for line in inp.readlines():
        for e in estimators:
            if e == "EVENTDAT": # EVENTDAT card has a different format than the other estimators
                if re.search("\A%s" % e, line):
                    unit = line[10:20].strip()
                    name = "" #line[0:10].strip() # actually, name for EVENTDAT does not matter - the Tree name will be used
                    if str2int(unit)<0: # we are interested in binary files only
                        if not unit in estimators[e]:
                            estimators[e] = ["%s" % unit]
            else:
                if re.search("\A%s" % e, line) and not re.search("\&", line[70:80]):
                    if e == "RESNUCLE":
                        unit = line[20:30].strip()
                    else:
                        unit = line[30:40].strip()
                    name = line[70:80].strip()
                    if str2int(unit)<0: # we are interested in binary files only
                        if not unit in estimators[e]:
                            estimators[e].append(unit)

    if args.verbose:
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

    if args.verbose:
        print estimators

    inp.close()

# run converters
    return_value = 0
    resnuclei_binary_files = []
    usrbin_binary_files = []
    usrbdx_binary_files = []
    usrtrack_binary_files = []
    for run in range(N, M+1):
        binfilename = ""
        rootfilenames = []
        command = ""
        for e in estimators:
            for s in estimators[e]:
                binfilename = args.inp.replace(".inp", "%.3d%s" % (run, s))
                if os.path.isfile(binfilename):
                    if re.search("RESNUCLE", e): # RESNUCLE = RESNUCLEi = RESNUCLEI
                        e = "RESNUCLEI"
                        resnuclei_binary_files.append(binfilename)
                    elif re.search("USRBIN", e):
                        usrbin_binary_files.append(binfilename)
                    elif re.search("USRTRACK", e):
                        usrtrack_binary_files.append(binfilename)
                    elif re.search("USRBDX", e):
                        usrbdx_binary_files.append(binfilename)
                    else:
                        rootfilenames.append(binfilename + ".root")
                        command =  "%s2root %s" % (e.lower(), binfilename)
                        if args.verbose:
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
        out_root_files.append(merge_files(resnuclei_binary_files, "resnuclei", "usrsuw", N, M, args))

    if len(usrbin_binary_files):
        out_root_files.append(merge_files(usrbin_binary_files, "usrbin", "usbsuw", N, M, args))
    if len(usrbdx_binary_files):
        out_root_files.append(merge_files(usrbdx_binary_files, "usrbdx", "usxsuw", N, M, args))
    if len(usrtrack_binary_files):
        out_root_files.append(merge_files(usrtrack_binary_files, "usrtrack", "ustsuw", N, M, args))

    if args.verbose:
        print "ROOT files produced: ", out_root_files

    if return_value is 0 and len(out_root_files)>1:
        out_root_file = args.inp.replace(".inp", ".root");
        force = ""
        if args.force_overwrite:
            force = "-f"
        verbose = "-v 0"
        if args.verbose:
            verbose = "-v 99"
        command = "hadd %s %s %s %s" % (force, verbose, out_root_file, string.join(out_root_files))
        if args.verbose:
            printincolor(command)
        return_value = os.system(command)
        if return_value is 0:
            verbose = ""
            if args.verbose:
                verbose = "-v"
            command = "rm -f %s %s" % (verbose, string.join(out_root_files))
            if args.verbose:
                printincolor(command)
            return_value = os.system(command)

    return return_value

if __name__ == "__main__":
    sys.exit(main())
