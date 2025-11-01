#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import sys, argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """
    Scales a ROOT object by the given number
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('fin', type=str, help='Original ROOT file name')
    parser.add_argument('-obj', dest='obj', type=str, help='object name. Scales all supported objects if omitted.', default=None, required=False)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-scale', dest='scale', type=float, help='scaling factor (mutually exclusive with "-n")')
    group.add_argument('-n', dest='n', type=int, help='number of ROOT files (mutually exclusive and inverse of the scaling factor)', default=0)
    parser.add_argument('-o', dest='fout', type=str, help='output ROOT file name with scaled objects', required=True)
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

    args = parser.parse_args()

    vobj = []

    scale = args.scale if args.n == 0 else 1.0/args.n

    print(scale)


    f = ROOT.TFile(args.fin)
    if args.obj:
        obj = f.Get(args.obj)
        if not obj:
            print("%s not found in %s" % (args.obj, args.fin), file=sys.stderr)
            return 1
        print(obj.GetName())
        obj.Sumw2() # needed for TH1 to have correct errors
        obj.Scale(scale)
        vobj.append(obj)
    else:
        for key in f.GetListOfKeys():
            obj = key.ReadObj()
            if obj.InheritsFrom(ROOT.THnSparse.Class()) or obj.InheritsFrom(ROOT.TH1.Class()):
                print(obj.GetName())
                obj.Sumw2() # needed for TH1 to have correct errors
                obj.Scale(scale)
                vobj.append(obj)
            else:
                print("%s not scaled" % h.GetName(), file=sys.stderr)
                return 1

    fout = ROOT.TFile(args.fout, "recreate")
    for obj in vobj:
        obj.Write()
    fout.Close()


if __name__=="__main__":
    sys.exit(main())
