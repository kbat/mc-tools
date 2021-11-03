#!/usr/bin/env python3

import sys, argparse, os, struct
from array import array
from mctools.fluka.flair import fortran
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True


def main():
    """ Converts PLOTGEOM output into a ROOT TMuiltiGraph object """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('plotgeom', type=str, nargs='*', help='list of plotgeom files')
    parser.add_argument('-o', dest='root', type=str, help='output ROOT file name', default="")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')
    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite', help='overwrite the output ROOT file')


    args = parser.parse_args()

    for f in args.plotgeom:
        if not os.path.isfile(f):
            sys.exit("plotgeom2root: File %s does not exist." % f)

    wlength = 0
    title = ""
    for plotgeom in args.plotgeom:
        if args.root == "":
            rootFileName = "%s%s" % (plotgeom,".root")
        else:
            rootFileName = args.root

        if not args.overwrite and os.path.isfile(rootFileName):
            sys.exit("%s exists. Use '-f' to overwrite it." % rootFileName)

        with open(plotgeom, 'rb') as f:
            data = fortran.read(f)
            size = len(data)
            if size != 80:
                sys.exit("Format error [title]")
            title = struct.unpack("=80s", data)[0].decode('utf-8').strip()
            if args.verbose:
                print(title)

            data = fortran.read(f)
            size = len(data)
            if size != 14*4:
                print("Format error [basis]")
            X0,Y0,Z0,X1,Y1,Z1,TYX,TYY,TYZ,TXX,TXY,TXZ,XAXLEN,YAXLEN = struct.unpack("=14f", data) # http://www.fluka.org/fluka.php?id=man_onl&sub=63
            if not args.verbose:
                print("Bottom left corner:",X0,Y0,Z0)
                print("Top right corner:",X1,Y1,Z1)
                print("Direction cosines of the x-axis:",TXX,TXY,TXZ)
                print("Direction cosines of the y-axis:",TYX,TYY,TYZ)
                print("x and y axis length:",XAXLEN,YAXLEN)
#                print(X0,Y0,Z0,X1,Y1,Z1,TYX,TYY,TYZ,TXX,TXY,TXZ,XAXLEN,YAXLEN)

            plane = "unknown"
            if abs(X0-X1)<0.001:
                plane="zx"
            elif abs(Y0-Y1)<0.001:
                plane="zy"
            elif abs(Z0-Z1)<0.001:
                plane="xy"

            print(plane)

            for i in range(1):
                data = fortran.read(f)
                size = len(data)
                if args.verbose:
                    print("size: ",size)
                if size==8:
                    NWORMS,dummy = struct.unpack("=2i", data)
                    if args.verbose:
                        print("NWORMS:",NWORMS,dummy)
#                elif size==12: # this is never called
#                    NWORMS,dummy,dummy1 = struct.unpack("=3i", data)
#                    print(NWORMS,dummy,dummy1)

            i = 0
            fout = ROOT.TFile(rootFileName, "recreate", plotgeom)
            mg = ROOT.TMultiGraph("mg", title)
            while True:
                i = i + 1
                data = fortran.read(f)
                if data is None:
                    break
                size = len(data)
                if args.verbose:
                    print("\nsize:",size)

                if size == 12:
                    windex,dummy,wlength = struct.unpack("=3i",data)
                    if args.verbose:
                        print(windex,dummy,wlength)
                elif size==8:
                    tmp = struct.unpack("=2i", data)
                    if args.verbose:
                        print("size8:",tmp)
##                    break
                elif size==24:
                    tmp = struct.unpack("=3i3f", data)
                    if args.verbose:
                        print("size24:",tmp)
                else:
                    if args.verbose:
                        print("a",wlength)
                    coord = struct.unpack("=%df" % (wlength*2),data) # pairs of x,y
                    if args.verbose:
                        print(coord[:10])

                    if plane == "xy":
                        x = list(map(lambda x:x+Y0, coord[::2]))
                        y = list(map(lambda y:y+X0, coord[1::2]))
                    elif plane=="zy":
                        x = list(map(lambda x:x+X0, coord[::2]))
                        y = list(map(lambda y:y+Z0, coord[1::2]))
                    elif plane=="zx":
                        x = list(map(lambda x:x+Y0, coord[::2]))
                        y = list(map(lambda y:y+Z0, coord[1::2]))
                    else:
                        print(f"ERROR: Plane is {plane} - not supported", file=sys.stderr)
                        return 1

                    g = ROOT.TGraph(len(x), array('f', x), array('f', y))
                    g.SetName("g%d" % i)
                    mg.Add(g)

        mg.Write()
        fout.Close()


if __name__=="__main__":
    sys.exit(main())
