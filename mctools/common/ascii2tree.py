#! /usr/bin/python2

from ROOT import ROOT, TFile, TTree
from sys import argv, exit

name_in = argv[1]
name_out = argv[2]
branchDescriptor=""
if len(argv)==4:
        branchDescriptor=argv[3]
        print branchDescriptor

fout = TFile(name_out, "recreate")
T = TTree("T", branchDescriptor)
T.ReadFile(name_in, branchDescriptor)
T.Write()
fout.Close()

