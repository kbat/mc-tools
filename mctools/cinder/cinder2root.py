#! /usr/bin/python -W all
#
# https://github.com/kbat/mc-tools
#

import sys, argparse
from cinder.alltabs import AllTabs
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


def main():
    """
    Convert CINDER output into ROOT
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('fin', type=str, help='CINDER file to convert')
    parser.add_argument('-o', dest='fout', type=str, help='ROOT output file', required=True)
#    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

    args = parser.parse_args()

    a = AllTabs(args.fin)

    f = ROOT.TFile(args.fout, "recreate")

    for t in a.tables:
        h = t.getHist()
        if h:
            h.Write()
    f.Close()


if __name__=="__main__":
    sys.exit(main())
