#!/usr/bin/env python3

import sys, argparse, os, struct
from array import array
from mctools.fluka.flair import fortran
from mctools.fluka import particle
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
#                print("\nsize:",size)

                if first:
                    first = False

                    n = (size-120)//4
                    fmt = "=80s32sii"
                    n = struct.calcsize(fmt)
                    title, time, nregs, nsco  = struct.unpack(fmt, data[:n])
                    dist = struct.unpack("=%di"%(len(data[n:])//4),  data[n:])

                    title = title.decode('utf-8').strip()
                    time  = time.decode('utf-8').strip()

                    print("title:", title)
                    print("time:", time)
                    print("number of regions:",nregs)
                    print("number of scoring distributions:", nsco)
                    print("distribution:",dist)


                    data = {}
                    nbins = nsco*nregs
                    for d in dist:
                        data[d] = array('f', nbins*[0.0])

                    fout = ROOT.TFile(args.root, "recreate", title)
                    T = ROOT.TTree("EVENTDAT", time)
                    for d in dist:
                        T.Branch(particle[d], data[d], f"d{d}[{nbins}]/F")

                elif size == n*4:
                    print("size:",size)
                    val = struct.unpack(f"{nbins}f", data)
                    size = len(val)
                    print(size)
                    # for i,v in enumerate(val):
                    #     DATA[i] = v
                    T.Fill()
                elif size == 12:
                    # print(size)
                    pass
                elif size == 48:
                    # print(size)
                    pass
                elif size == 8:
                    print(size)
                    pass

    T.Write()
    fout.Close()


if __name__=="__main__":
    sys.exit(main())
