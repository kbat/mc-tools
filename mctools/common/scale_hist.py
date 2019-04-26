#! /usr/bin/python -W all
#
# scales all histos in the given ROOT file by a given factor
#

from __future__ import print_function
from sys import argv, exit
from ROOT import TFile, TH1, TObject

def main():
    """
    Usage: scale-hist factor old-file.root new-file.root
    """
    factor   = float(argv[1])
    oldfname = argv[2]
    newfname = argv[3]

    oldfile = TFile(oldfname, "update")
    oldfile.ls()
    h0 = oldfile.Get("h0")
    h0.SetDirectory(0)
    oldfile.Close()

    print(h0.GetBinContent(1))
    h0.Scale(10)
    print(h0.GetBinContent(1))

    newfile = TFile(newfname, "recreate")
    h0.Write()
    newfile.Write()
    newfile.Close()

if __name__ == '__main__':
    exit(main())
