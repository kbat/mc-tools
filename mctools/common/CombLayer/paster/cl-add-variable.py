#!/usr/bin/env python3
#

import argparse, os, re, sys
import fileinput
from mctools.mctools import checkPaths

def checkName(n, t):
    """ Check if name can be omitted for the given type.
    Normally, name can be omitted for the variables which are not populated in the *Variables.cxx file
    (like vectors or pointers)
    """
    if len(n) == 0:
        if not re.search("vector",t) and not re.search("shared_ptr", t):
            print("Argument '-name' must be specified for type '%s'" % t, file=sys.stderr)
            sys.exit(4)

def main():
    """
    Add variable in the CL component class
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-var', dest='var', type=str, help='variable name', required=True)
    parser.add_argument('-name', dest='name', type=str, help='variable name in *Variables.cxx. If not specified, the record in the populate method is not added.', required=False, default="")
    parser.add_argument('-type', dest='type', type=str, help='variable type', required=True)
    parser.add_argument('-comment', dest='comment', type=str, help='variable description', required=True)
    parser.add_argument('-after', dest='after', type=str, help='the variable will be put after the given one', required=True)
    parser.add_argument('-model', dest='model', type=str, help='model name (= folder with .cxx file)', required=True)
    parser.add_argument('-class', dest='className', type=str, help='class name', required=True)

    args = parser.parse_args()

    checkName(args.name, args.type)

    cxxDir = args.model
    hDir   = cxxDir+'Inc'
    
    cxx = os.path.join(cxxDir, args.className + ".cxx")
    h   = os.path.join(hDir,   args.className + ".h")
    
    if checkPaths([hDir, cxxDir], [h,cxx]) > 0:
        sys.exit(1)

    print(h)
    print(cxx)
    mat = False
    hFixed = False
    ccFixed = False
    equalFixed = False
    evalFixed = False

    if args.type == "int" and args.name[-3:] == "Mat":
        mat = True

    isPointer = re.search("shared_ptr", args.type)

# fix the header
    for line in fileinput.input(h, inplace=True, backup='.bak'):
       print(line.rstrip())
       if re.search(" %s;" % args.after, line):
           hFixed = True
           print("  %s %s; ///< %s" % (args.type, args.var, args.comment))

# fix implementation
    for line in fileinput.input(cxx, inplace=True, backup='.bak'):
#    for line in fileinput.input(cxx):
        l = ""
        line = line.rstrip()

# copy constructor
        if re.search(r"%s\(A.%s\)" % (args.after, args.after), line) or re.search(r"%s\(new .*\(\*A.%s\)\)" % (args.after, args.after), line):
            ccFixed = True
            if isPointer:
                try:
                    cls = re.search("shared_ptr<(.*?)>", args.type).group(1)
                except AttributeError:
                    cls = 'XXX'
                l = "  %s(new %s(*A.%s))" % (args.var, cls, args.var)
            else:
                l = "  %s(A.%s)" % (args.var, args.var)

            if line[-1:] == ",": # comma after
                l = l + ","
            else:
                line = line + ","

# operator =
        if re.search(r"\*?%s=\*?A.%s;" % (args.after, args.after), line):
            equalFixed = True
            star=""
            if isPointer:
                star="*"
            l = "      %s%s=%sA.%s;" % (star, args.var, star, args.var)

# populate
        if len(args.name) and not isPointer and (re.search("%s=Control.EvalVar" % args.after, line) or re.search("%s=ModelSupport::EvalMat" % args.after, line)):
            evalFixed = True
            if mat:
                l = "  %s=ModelSupport::EvalMat<%s>(Control,keyName+\"%s\");" % (args.var, args.type, args.name)
            elif args.var == "engActive":
                l = "  %s=Control.EvalPair<int>(keyName,\"\",\"EngineeringActive\")'" % (args.var)
            else:
                l = "  %s=Control.EvalVar<%s>(keyName+\"%s\");" % (args.var, args.type, args.name)

        print(line)
        if l:
            print(l)

    if not hFixed:
        print("!!! No record added in the header", file=sys.stderr)
    if not ccFixed:
        print("!!! No record added in the copy constructor", file=sys.stderr)
    if not equalFixed:
        print("!!! No record added in the operator=", file=sys.stderr)
    if not evalFixed:
        print("!!! No record added in the %s::populate() method." % args.className, file=sys.stderr)
                
if __name__ == "__main__":
    sys.exit(main())
    
