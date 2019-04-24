#! /usr/bin/python2 -W all
# $Id$
# $URL$

import sys, argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True



def main():
    """Lists a ROOT file contents"""

    parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: http://code.google.com/p/mc-tools", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('rootfname', type=str, help='ROOT file name')
    parser.add_argument('objname', type=str, nargs='?', help='Name of object to print')
    parser.add_argument('option', type=str, nargs='?', default='""', help='Option to use when printing the object')
    arguments = parser.parse_args()

    f = ROOT.TFile(arguments.rootfname)

    if arguments.objname:
        obj = f.Get(arguments.objname)
        obj.Print(arguments.option)
        if obj.Class_Name() == "TDirectoryFile":
            obj.ls()
    else:
        f.ls()



    f.Close()


if __name__ == "__main__":
        sys.exit(main())
