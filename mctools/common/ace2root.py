#! /usr/bin/python2

#%matplotlib inline
from __future__ import print_function
from pylab import savefig
import matplotlib.pyplot as plt
from pyne import ace
import inspect
import ROOT, sys, argparse, os
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """ Converts ACE files into the ROOT format"""

    parser = argparse.ArgumentParser(description=main.__doc__, epilog='Homepage: https://github.com/kbat/mc-tools')
    parser.add_argument('acefile', type=str, help='input ACE file name')
    parser.add_argument('rootfile', type=str, default="", nargs='?', help='output ROOT file name')
    args = parser.parse_args()

    if not os.path.isfile(args.acefile):
        print("ace2root: File %s does not exist." % args.acefile, file=sys.stderr)
        sys.exit(1)

    if args.rootfile == "":
        rootFileName = "%s%s" % (args.acefile,".root")
    else:
        rootFileName = args.rootfile

    lib = ace.Library(args.acefile)
    lib.read()

    ntables = len(lib.tables)

    if not ntables:
        print("ace2root: no tables found in", args.acefile, file=sys.stderr)
        sys.exit(2)
#    else:
#        print(ntables, "tables found")

    rootfile = ROOT.TFile(rootFileName, "recreate")

    for tname in lib.tables:
        table = lib.tables[tname]
#        print(tname, table.reactions)
        newdir = ROOT.gDirectory.mkdir(tname, "");
        newdir.cd()
        for mt in table.reactions:
            reaction = table.find_reaction(mt)
#            print(reaction.text)
            gr = ROOT.TGraph(len(table.energy), table.energy, reaction.sigma)
            gr.SetName("mt%s" % str(mt))
            gr.SetTitle("%s #bullet MT=%d;Enegy [MeV];#sigma [barn]" % (tname, mt))
            gr.Write()
        rootfile.cd()
    rootfile.Close()

if __name__ == "__main__":
        sys.exit(main())
