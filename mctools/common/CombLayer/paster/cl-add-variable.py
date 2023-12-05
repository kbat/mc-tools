#!/usr/bin/env python3
#

import argparse, os, re, sys
import fileinput
from mctools import checkPaths

def checkNameTitle(n,t):
    """ Check if name/title is consistent with CombLayer logic """
    if n == "airMat":
        print("ERROR: use 'voidMat' for the air material name", file=sys.stderr)
        sys.exit(5)
    if t == "AirMat":
        print("ERROR: use 'VoidMat' for the air material title", file=sys.stderr)
        sys.exit(5)

def checkTitle(n, t):
    """ Check if title can be omitted for the given type.
    Normally, title can be omitted for the variables which are not populated in the *Variables.cxx file
    (like vectors or pointers)
    """
    if len(n) == 0 and not re.search("vector",t) and not re.search("shared_ptr", t):
            print("Argument '-title' must be specified for type '%s'" % t, file=sys.stderr)
            sys.exit(4)

def isMaterial(args):
    """ Return True if variable is material """
    return args.type == "int" and args.title[-3:] == "Mat"

def printDeclaration(args, t, offset=32):
    """ Prints variable declaration in the header file
    offset: column number where the comment should start
    """
    print(("{indent}{t} {name}; {cc:>%d} {comment}" % abs(offset-1-len(t)-len(args.name))).format(indent=" "*args.indent,
                                                                                                  t=t, name=args.name, cc="///<", comment=args.comment))

def genSource(cxx, args):
    """ Fixes the generator implementation (the .cxx file).
    Return True if succeeded.
    """
    ccFixed = False
    hFixed = False
    for line in fileinput.input(cxx, inplace=True, backup='.bak'):
        l = ""
        line = line.rstrip()
        if re.search(f"{args.after}\(", line):
            ccFixed = True
            if args.type == "std::string" or (args.type == "int" and isMaterial(args)):
                l = f"  {args.name}(\"{args.value}\")"
            else:
                l = f"  {args.name}({args.value})"
            if line[-1:] == ',':
                l = l + ','
            else:
                line = line + ','
        elif re.search("Control\.addVariable\(keyName\+.*,%s\);" % args.after, line):
            hFixed = True
            l = f"  Control.addVariable(keyName+\"{args.title}\",{args.name});"
        print(line)
        if l:
            print(l)

    return (ccFixed, hFixed)

def genHeader(h, args):
    """ Fix the generator header. Return True if succeeded """
    hFixed = False
    t = "std::string" if isMaterial(args) else args.type

    for line in fileinput.input(h, inplace=True, backup='.bak'):
       print(line.rstrip())
       if re.search(" %s;" % args.after, line):
           hFixed = True
           printDeclaration(args,t)
    return hFixed


def header(h, args):
    """ Fix the header. Return True if fixed """
    hFixed = False
    for line in fileinput.input(h, inplace=True, backup='.bak'):
       print(line.rstrip())
       if re.search(" %s;" % args.after, line):
           hFixed = True
           printDeclaration(args, args.type)
    return hFixed

def source(cxx, args):
    """ Fix implementation. Return list of fixed/non fixed flags. """
    ccFixed = False
    equalFixed = False
    evalFixed = False
    indent = " "*args.indent

    isPointer = re.search("shared_ptr", args.type)

    mat = isMaterial(args)

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
                l = "%s%s(new %s(*A.%s))" % (indent, args.name, cls, args.name)
            else:
                l = "%s%s(A.%s)" % (indent, args.name, args.name)

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
            l = "    %s%s%s=%sA.%s;" % (indent, star, args.name, star, args.name)

# populate
        if len(args.title) and not isPointer and (re.search("%s=Control.EvalVar" % args.after, line) or re.search("%s=ModelSupport::EvalMat" % args.after, line)):
            evalFixed = True
            if mat:
                l = "%s%s=ModelSupport::EvalMat<%s>(Control,keyName+\"%s\");" % (indent, args.name, args.type, args.title)
            elif args.name == "engActive":
                l = "%s%s=Control.EvalPair<int>(keyName,\"\",\"EngineeringActive\")'" % (indent, args.title)
            else:
                l = "%s%s=Control.EvalVar<%s>(keyName+\"%s\");" % (indent, args.name, args.type, args.title)

        print(line)
        if l:
            print(l)
    return (ccFixed, equalFixed, evalFixed)

def main():
    """
    Add variable in the CL component class
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-name', dest='name', type=str, help='variable name', required=True)
    parser.add_argument('-title', dest='title', type=str,required=False, default="",
                        help='variable name in *Variables.cxx. If not specified, the record in the populate method is not added.')
    parser.add_argument('-type', dest='type', type=str, help='variable type', required=True)
    parser.add_argument('-comment', dest='comment', type=str, help='variable description', required=True)
    parser.add_argument('-after', dest='after', type=str, help='the variable will be put after the given one', required=True)
    parser.add_argument('-model', dest='model', type=str, help='model name (= folder with .cxx file)', required=True)
    parser.add_argument('-class', dest='className', type=str, help='class name', required=True)
    parser.add_argument('-value', dest='value', type=str,default="", required=False,
                        help='default value (if set, the generator for variables is created and this value is set as default)')
    parser.add_argument('-indent', dest='indent', type=int, help='number of initial spaces', default=2, required=False)
    parser.add_argument('-generator', dest='generator', type=str, help='path to file with generator implementation (.cxx)', default="", required=False)

    args = parser.parse_args()

    checkNameTitle(args.name,args.title)
    checkTitle(args.title, args.type)

    cxxDir = args.model
    hDir   = cxxDir+'Inc'


    cxx = os.path.join(cxxDir, args.className + ".cxx")
    h   = os.path.join(hDir,   args.className + ".h")

    if args.generator == "":
        cxxGenDir = os.path.join('',*cxxDir.split('/')[:-1], "commonGenerator")
        hGenDir = cxxGenDir + 'Inc'
        cxxGen = os.path.join(cxxGenDir, args.className + "Generator.cxx")
        hGen   = os.path.join(hGenDir,   args.className + "Generator.h")
    else:
        t = args.generator.split('/')
        cxxGenDir = os.path.join(*t[:-1])
        hGenDir = cxxGenDir + 'Inc'
        cxxGen = args.generator
        hGen = re.sub("cxx", "h", t[-1])
        hGen = os.path.join(hGenDir, hGen)

    if checkPaths([hDir, cxxDir], [h,cxx]) > 0:
        sys.exit(1)

    print(h)
    print(cxx)

    if args.value:
        if checkPaths([hGenDir, cxxGenDir], [hGen, cxxGen]) > 0:
            sys.exit(2)
        print(hGen)
        print(cxxGen)

    mat = False
    hFixed = False
    ccFixed = False
    equalFixed = False
    evalFixed = False

    hFixed = header(h, args)
    ccFixed, equalFixed, evalFixed = source(cxx, args)

    if not hFixed:
        print("!!! No record added in the header", file=sys.stderr)
    if not ccFixed:
        print("!!! No record added in the copy constructor", file=sys.stderr)
    if not equalFixed:
        print("!!! No record added in the operator=", file=sys.stderr)
    if not evalFixed:
        print("!!! No record added in the %s::populate() method." % args.className, file=sys.stderr)

    if args.value: # generator is needed
        hFixed = genHeader(hGen, args)
        if not hFixed:
            print("!!!: No record added in the generator header", file=sys.stderr)

        ccFixed, hFixed = genSource(cxxGen, args)
        if not ccFixed:
            print("!!! No record added in the generator copy constructor", file=sys.stderr)
        if not hFixed:
            print("!!!: No record added in the generator implementation", file=sys.stderr)

if __name__ == "__main__":
    sys.exit(main())
