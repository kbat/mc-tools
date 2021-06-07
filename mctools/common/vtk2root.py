#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

from decimal import Decimal
import os,sys,re,numpy,argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class VTK:
    def __init__(self, fname, htype):
        self.fname=fname
        self.htype=htype
        self.read()

    def Print(self):
        print(self.fname)

    def read(self):
        "Read vtk file"
        f = open(self.fname)
        f.readline()
        title = f.readline().strip()
        form = f.readline().strip()
        dataset = f.readline().strip().split()[1]

        if dataset != 'RECTILINEAR_GRID':
            sys.exit("Error: Unsupported format")
        self.nx,self.ny,self.nz = list(map(int, f.readline().strip().split()[1:]))
        f.close()

#        print(title,form, dataset)
        self.x = self.readCoordinates("X")
        self.y = self.readCoordinates("Y")
        self.z = self.readCoordinates("Z")
        self.table = self.readTable()
        self.N = self.nx*self.ny*self.nz
        if len(self.table) != self.N:
            sys.exit("Error: LOOKUP_TABLE size does not match number of points")

    def readCoordinates(self, c):
        "Read the list of coordinates (bin centres)"
        found = False
        centres = []
        d = {}
        f = open(self.fname)
        for line in f:
            l = line.strip()
            if re.search("\A%s_COORDINATES" % c,l):
                n = l.split()[1]
                found = True
                continue
            if found:
                if re.search("_COORDINATES", l) or re.search("DATA", l): # => end reading coordinates
                    break
                else:
                    for v in l.split():
                        centres.append(float(v))
        f.close()

        # at this point 'centres' contains bin centres, while we need low/up edges
        if len(centres) == 1:
            dx = 1.0 # arbitrary fix for single bin axis
            centres[0] = centres[0] - dx/2.0
            centres.append(centres[0]+dx/2.0)
            return centres
        else:
            edges = []
            # if (c == "Z"):
            #     print("centres", centres)
            dx = centres[1] - centres[0]
            edges.append(centres[0]-dx/2.0)
            for i in range(len(centres)-1):
                edges.append((centres[i]+centres[i+1])/2.0)
            edges.append(edges[-1]+dx)
            # if (c == "Z"):
            #     print("edges: ",edges)
            return edges

    def readTable(self):
        "Read LOOKUP_TABLE"
        found = False
        val = []
        with open(self.fname) as f:
            for line in f:
                l = line.strip()
                if re.search("\ALOOKUP_TABLE", l):
                    found = True
                    continue
                if found:
                    for v in l.split():
                        if self.htype[-1] == "F":
                            val.append(float(v))
                        elif self.htype[-1] == "D":
                            val.append(Decimal(v))
                        else:
                            try:
                                val.append(int(v));
                            except:
                                raise TypeError(f"Trying to fill the {self.htype} histogram with non-integer data. Use the -type argument to set the correct TH3 type.")

        return val

    def getTH3(self):
#        print(self.nz, self.z)
        title = os.path.splitext(os.path.basename(self.fname))[0]
        h = eval("ROOT."+self.htype)("h3", "%s;x;y;z" % title, self.nx, numpy.array(self.x), self.ny, numpy.array(self.y), self.nz, numpy.array(self.z))
        ii = 0
        for k in range(self.nz):
            for j in range(self.ny):
                for i in range(self.nx):
                    h.SetBinContent(i+1,j+1,k+1, self.table[ii])
                    ii = ii+1
        return h

def main():
    """
    VTK -> ROOT converter
    """
    allowed_types = ("TH3C", "TH3D", "TH3F", "TH3I", "TH3S");
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('vtk', type=str, help='VTK input file name')
    parser.add_argument("-type", type=str, dest='htype',   help='TH3 type', default="TH3I", choices=allowed_types)
    parser.add_argument('root', type=str, nargs='?', help="ROOT output file name",default=None)
    args = parser.parse_args()

    if args.root is None:
        args.root = os.path.splitext(os.path.basename(args.vtk))[0] + ".root"

    fin = VTK(args.vtk,args.htype)
    h = fin.getTH3()
    h.SaveAs(args.root)



if __name__=="__main__":
    sys.exit(main())
