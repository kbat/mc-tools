#! /usr/bin/python -W all

import os, sys, argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
        """ Converts ASCII to TTree.

        TTree::ReadFiule syntax is explained in the ROOT manual:
        https://root.cern.ch/doc/master/classTTree.html#a9c8da1fbc68221b31c21e55bddf72ce7
        """
        parser = argparse.ArgumentParser(description=main.__doc__,
                                         epilog="Homepage: https://github.com/kbat/mc-tools")
        parser.add_argument('txt', type=str, help='input file name')
        parser.add_argument('root', type=str, nargs='?', help='output ROOT file name', default="")
        parser.add_argument('-branch', type=str, dest='branch', help='Branch descriptor. If not given, the first input line is used.', default="")

        args = parser.parse_args()

        if args.root == "":
                fout = os.path.splitext(args.txt)[0] + ".root"
        else:
                fout = args.root

        f = ROOT.TFile(fout, "recreate", args.txt)
        T = ROOT.TTree("T", args.branch)
        T.ReadFile(args.txt, args.branch)
        T.Write()
        f.Close()

if __name__ == "__main__":
        sys.exit(main())

