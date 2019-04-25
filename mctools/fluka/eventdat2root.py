#! /usr/bin/python -W all

from __future__ import print_function
import sys, argparse, os, struct
from array import array
from mctools.fluka.flair import fortran
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


def main():
    """ Converts ustsuw output into a ROOT TH1F histogram """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('eventdat', type=str, nargs='*', help='list of eventdat files')
    parser.add_argument('-o', dest='root', type=str, help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')
    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite', help='overwrite the output ROOT file')

    
    args = parser.parse_args()

    for f in args.eventdat:
        if not os.path.isfile(f):
            print("eventdat2root: File %s does not exist." % f, file=sys.stderr)
            return 1

    if not args.overwrite and os.path.isfile(args.root):
        sys.exit("%s exists. Use '-f' to overwrite it." % args.root)

    first = True
    for eventdat in args.eventdat:
        with open(eventdat, 'rb') as f:
            print(eventdat)
            while True:
                data = fortran.read(f)
                if data is None:
                    break
                size = len(data)
                print("\nsize:",size)
                
                if first:
                    first = False

                    title, time, nregs, nsco, dist = struct.unpack("=80s32siii", data)

                    print("title:", title)
                    print("time:", time)
                    print("number of regions:",nregs)
                    print("number of scoring distributions:", nsco)
                    print("distribution:",dist)

                    DATA = array('f', nsco*nregs*[0.0])
                    
                    fout = ROOT.TFile(args.root, "recreate", title)
                    T = ROOT.TTree("EVENTDAT", time)
                    T.Branch("DATA", DATA, "d%d[%d]/F" % (dist,nsco*nregs))
                elif size == 12:
                    pass
                elif size == 48:
                    pass
                elif size == 8:
                    pass
                elif size == nregs*nsco*4:
                    val = struct.unpack("%df" % nregs*nsco, data)
                    for i,v in enumerate(val):
                        DATA[i] = v
                    T.Fill()
            
    T.Write()
    fout.Close()
    

if __name__=="__main__":
    sys.exit(main())
