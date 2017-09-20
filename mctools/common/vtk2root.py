#! /usr/bin/python -W all
#
# https://github.com/kbat/mc-tools
#

import os,sys,re,numpy,argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

class VTK:
    def __init__(self, fname):
        self.fname=fname
        self.read()

    def Print(self):
        print self.fname

    def read(self):
        "Read vtk file"
        f = open(self.fname)
        f.readline()
        title = f.readline().strip()
        form = f.readline().strip()
        dataset = f.readline().strip().split()[1]
        
        if dataset != 'RECTILINEAR_GRID':
            sys.exit("Error: Unsupported format")
        self.nx,self.ny,self.nz = map(int, f.readline().strip().split()[1:])
        f.close()

#        print title,form, dataset,nx,ny,nz
        self.x = self.readCoordinates("X")
        self.y = self.readCoordinates("Y")
        self.z = self.readCoordinates("Z")
        self.table = self.readTable()
        self.N = self.nx*self.ny*self.nz
        if len(self.table) != self.N:
            sys.exit("Error: LOOKUP_TABLE size does not match number of points")

    def readCoordinates(self, c):
        "Read the list of coordinates"
        found = False
        val = []
        d = {}
        f = open(self.fname)
        for line in f:
            l = line.strip()
            if re.search("\A%s_COORDINATES" % c,l):
                n = l.split()[1]
                found = True
                continue
            if found:
                if re.search("_COORDINATES", l) or re.search("DATA", l):
                    dx = val[-1]-val[-2]
                    val.append(val[-1]+dx)
                    d[n] = val
                    return val
                else:
                    for v in l.split():
                        val.append(float(v))
        f.close()

    def readTable(self):
        "Read LOOKUP_TABLE"
        found = False
        val = []
        f = open(self.fname)
        for line in f:
            l = line.strip()
            if re.search("\ALOOKUP_TABLE", l):
                found = True
                continue
            if found:
                for v in l.split():
                    val.append(float(v))
        return val

    def getTH3(self):
        title = os.path.splitext(os.path.basename(self.fname))[0]
        h = ROOT.TH3D("h3", "%s;x;y;z" % title, self.nx, numpy.array(self.x), self.ny, numpy.array(self.y), self.nz, numpy.array(self.z))
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
    parser = argparse.ArgumentParser(description=main.__doc__,epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('vtk', type=str, help='VTK input file name')
    parser.add_argument('root', type=str, nargs='?', help="ROOT output file name",default="")
    args = parser.parse_args()

    if args.root == "":
        args.root = os.path.splitext(os.path.basename(args.vtk))[0] + ".root"

    fin = VTK(args.vtk)
    h = fin.getTH3()
    h.SaveAs(args.root)

    

if __name__=="__main__":
    sys.exit(main())

