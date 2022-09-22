#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import sys, argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

def main():
    """
    A tool to diff two ROOT histograms. Assume they are of TH3I type. Return the number of different bins found.
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('h1', type=str, nargs=2, help='Path to the first histogram file and its name')
    parser.add_argument('h2', type=str, nargs=2, help='Path to the second histogram file and its name')

    args = parser.parse_args()

    f1 = ROOT.TFile.Open(args.h1[0])
    h1 = f1.Get(args.h1[1])
    h1.SetName("h1")
    # h1.SetDirectory(0)
    # f1.Close()

    f2 = ROOT.TFile.Open(args.h2[0])
    h2 = f2.Get(args.h2[1])
    h2.SetName("h2")
    # h2.SetDirectory(0)
    # f2.Close()

    nx, ny, nz = h1.GetNbinsX(), h1.GetNbinsY(), h1.GetNbinsZ()

    assert nx == h2.GetNbinsX()
    assert ny == h2.GetNbinsY()
    assert nz == h2.GetNbinsZ()

    print(args.h1, args.h2)

    hdiff = h1.Clone("hdiff")
    hdiff.Reset()
    hdiff.SetTitle(f"{args.h1[0]} vs {args.h2[0]}")
    hdiff.SetDirectory(0)

    retval = 0
    for i in range(1,nx+1):
        for j in range(1,ny+1):
            for k in range(1,nz+1):
                val1 = h1.GetBinContent(i,j,k)
                val2 = h2.GetBinContent(i,j,k)
                if val1 != val2:
                    x = h1.GetXaxis().GetBinCenter(i)
                    y = h1.GetYaxis().GetBinCenter(j)
                    z = h1.GetZaxis().GetBinCenter(k)
                    dx = h1.GetXaxis().GetBinWidth(i)
                    dy = h1.GetYaxis().GetBinWidth(j)
                    dz = h1.GetZaxis().GetBinWidth(k)
                    hdiff.SetBinContent(i,j,k,1.0)
                    print(f"ERROR: {x:.2f} {y:.2f} {z:.2f}:\t{val1} {val2}\t\tbin size: {dx:.2f} {dy:.2f} {dz:.2f}")
                    retval += 1

    if retval == 0:
        print(f"OK: {args.h1} {args.h2}")

    f2.Close()
    f1.Close()


    fdiff = ROOT.TFile(args.h2[0].replace("exe1_","hist_diff_"), "recreate")
    hdiff.Write()
    fdiff.Close()

    return retval

if __name__ == "__main__":
    exit(main())
