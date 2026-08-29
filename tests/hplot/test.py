#!/usr/bin/env python3

"""
Regression test for hplot.

Every test runs hplot in batch mode (-o), reads back the canvas it wrote and
compares the drawn TH2 bin by bin against the expected projection of the input
TH3.  ROOT notation is used throughout: for a plane "vh" the first character is
the *vertical* axis of the TH2 (its y axis) and the second one is the
*horizontal* axis (its x axis).
"""

from os import system, remove
from os.path import exists
from sys import exit
import ROOT

ROOT.gROOT.SetBatch(True)

nx, xmin, xmax = (4, -2, 2)
ny, ymin, ymax = (6, -3, 3)
nz, zmin, zmax = (8, -4, 4)

OUT = "hplot.root"


def content(i, j, k):
    return k*100 + j*10 + i


def error(i, j, k):
    return k*50 + j*5 + i


def check(i, j, k, val, hval, err, herr):
    nerrors = 0
    if val != hval:
        nerrors += 1
        print(i,j,k,"Value is wrong:", hval, val)
    if err != herr:
        nerrors += 1
        print(i,j,k,"Error is wrong", herr, err)
    return nerrors


def checkClose(what, expected, actual, tol=1e-4):
    """Compare floating point values."""
    if abs(expected-actual) > tol*max(1.0, abs(expected)):
        print(what, "is wrong:", actual, "expected", expected)
        return 1
    return 0


def bins(nbins, x1, x2):
    width = (x2-x1)/nbins
    return [x1+width*(i-0.5) for i in range(1, nbins+1)]


def build(fname, hname):

    h = ROOT.TH3I(hname, ";x;y;z", nx, xmin, xmax, ny, ymin, ymax, nz, zmin, zmax)

    for i in range(1,nx+1):
        for j in range(1,ny+1):
            for k in range(1,nz+1):
                h.SetBinContent(i,j,k, content(i,j,k))
                h.SetBinError(i,j,k, error(i,j,k))

    h.SaveAs(fname)


def buildFloat(fname, hname, relerr=None):
    """TH3F data.  If relerr is given it is called as relerr(i) and returns the
    relative error to assign to the bin - used by the -maxerror test."""

    h = ROOT.TH3F(hname, ";x;y;z", nx, xmin, xmax, ny, ymin, ymax, nz, zmin, zmax)

    for i in range(1,nx+1):
        for j in range(1,ny+1):
            for k in range(1,nz+1):
                val = content(i,j,k)
                h.SetBinContent(i,j,k, val)
                if relerr is None:
                    h.SetBinError(i,j,k, k*10+j+i)
                else:
                    h.SetBinError(i,j,k, val*relerr(i))

    h.SaveAs(fname)


# A FLUKA geometry sized for the binning of build(): a TARGET box
# x = [-1,1], y = [-2,2], z = [-3,3] inside a vacuum box reaching well beyond
# the histogram, so that the only boundary in the picture is the target's.
BOX = {"x": 1.0, "y": 2.0, "z": 3.0}

GEOMETRY = """TITLE
hplot geometry test
GEOBEGIN                                                              COMBNAME
    0    0
RPP world     -100.0 100.0 -100.0 100.0 -100.0 100.0
RPP outer      -10.0  10.0  -10.0  10.0  -10.0  10.0
RPP inner       -1.0   1.0   -2.0   2.0   -3.0   3.0
END
BLKHOLE      5 +world -outer
VOID         5 +outer -inner
TARGET       5 +inner
END
GEOEND
ASSIGNMA    BLCKHOLE   BLKHOLE
ASSIGNMA      VACUUM      VOID
ASSIGNMA        IRON    TARGET
STOP
"""


def buildGeometry(fname):
    """The FLUKA input file hplot cuts to get the outlines."""

    with open(fname, "w") as f:
        f.write(GEOMETRY)


def addMacro(fname, macro):
    """Store the same input file as a TMacro inside the data file, the way
    fluka2root does - hplot reads it from there when no file of that name
    exists."""

    m = ROOT.TMacro(macro, macro+".inp")
    for line in GEOMETRY.splitlines():
        m.AddLine(line)

    f = ROOT.TFile(fname, "UPDATE")
    m.Write()
    f.Close()


def buildUniform(fname, hname, n1, n2, n3):
    """Histogram filled with 1.0 everywhere - used by the -rebin test, where
    averaging a uniform histogram must leave it uniform."""

    h = ROOT.TH3F(hname, ";x;y;z", n1, -2, 2, n2, -3, 3, n3, -1, 1)

    for i in range(1,n1+1):
        for j in range(1,n2+1):
            for k in range(1,n3+1):
                h.SetBinContent(i,j,k, 1.0)

    h.SaveAs(fname)


def run(args, nprim=1):
    """Run hplot in batch mode and return (file, [histograms]).

    Returns the first nprim TH2 primitives of the canvas in drawing order: the
    data histogram first, then the geometry one if a geometry file was given.
    They are picked by type rather than by position because options such as
    -flipwithaxis add other primitives (a TFrame, a TGaxis) to the canvas.

    The caller must close the file when done - the histograms belong to the
    canvas inside it.
    """
    if exists(OUT):
        remove(OUT)

    command = "hplot %s -o %s" % (args, OUT)
    rc = system(command)
    if rc != 0 or not exists(OUT):
        print("FAILED to run:", command)
        return None, [None]*nprim

    f = ROOT.TFile(OUT)
    c1 = f.Get("hplot")
    prims = [p for p in c1.GetListOfPrimitives() if isinstance(p, ROOT.TH2)]
    prims += [None] * (nprim-len(prims))
    return f, prims[:nprim]


def multigraph(f):
    """The geometry outlines drawn on the canvas of the file run() returned,
    as the list of their (x,y) point lists.  None if no TMultiGraph was drawn,
    an empty list if it holds no outline."""

    c1 = f.Get("hplot")
    for p in c1.GetListOfPrimitives():
        if isinstance(p, ROOT.TMultiGraph):
            graphs = p.GetListOfGraphs()
            if not graphs:
                return []
            return [[(g.GetX()[i], g.GetY()[i]) for i in range(g.GetN())]
                    for g in graphs]
    return None


def checkOutline(points, hhalf, vhalf, tol=0.02):
    """Every point must sit on the outline of the rectangle
    [-hhalf,hhalf] x [-vhalf,vhalf], and the outline must reach all four of
    its sides."""

    nerrors = 0
    for h, v in points:
        onh = abs(abs(h)-hhalf) < tol and abs(v) <= vhalf+tol
        onv = abs(abs(v)-vhalf) < tol and abs(h) <= hhalf+tol
        if not (onh or onv):
            print("Outline point (%g, %g) is not on the %gx%g rectangle"
                  % (h, v, hhalf, vhalf))
            nerrors += 1

    if not points:
        print("The outline has no points")
        return nerrors+1

    for what, expected, actual in (("outline xmin", -hhalf, min(h for h,v in points)),
                                   ("outline xmax",  hhalf, max(h for h,v in points)),
                                   ("outline ymin", -vhalf, min(v for h,v in points)),
                                   ("outline ymax",  vhalf, max(v for h,v in points))):
        nerrors += checkClose(what, expected, actual, tol)

    return nerrors


def testXY(fname="test.root", hname="h3"):

    nerrors = 0
    offset = bins(nz, zmin, zmax)
    for plane in ("xy", "yx"):
        print("Testing ", plane)
        for k,off in enumerate(offset,1):
            f, (h,) = run("%s %s -plane %s -offset %g" % (fname, hname, plane, off))
            if not f:
                nerrors += 1
                continue

            for i in range(1,nx+1):
                for j in range(1,ny+1):
                    val = content(i,j,k)
                    err = error(i,j,k)
                    if plane == "yx":
                        hval = h.GetBinContent(i,j)
                        herr = h.GetBinError(i,j)
                    else:
                        hval = h.GetBinContent(j,i)
                        herr = h.GetBinError(j,i)
                    nerrors += check(i,j,k,val,hval,err,herr)
            f.Close()

    return nerrors


def testXZ(fname="test.root", hname="h3"):

    nerrors = 0
    offset = bins(ny, ymin, ymax)
    for plane in ("xz", "zx"):
        print("Testing ", plane)
        for j,off in enumerate(offset,1):
            f, (h,) = run("%s %s -plane %s -offset %g" % (fname, hname, plane, off))
            if not f:
                nerrors += 1
                continue

            for i in range(1,nx+1):
                for k in range(1,nz+1):
                    val = content(i,j,k)
                    err = error(i,j,k)
                    if plane == "xz":
                        hval = h.GetBinContent(k,i)
                        herr = h.GetBinError(k,i)
                    else:
                        hval = h.GetBinContent(i,k)
                        herr = h.GetBinError(i,k)
                    nerrors += check(i,j,k,val,hval,err,herr)
            f.Close()

    return nerrors


def testYZ(fname="test.root", hname="h3"):

    nerrors = 0
    offset = bins(nx, xmin, xmax)
    for plane in ("yz", "zy"):
        print("Testing ", plane)
        for i,off in enumerate(offset,1):
            f, (h,) = run("%s %s -plane %s -offset %g" % (fname, hname, plane, off))
            if not f:
                nerrors += 1
                continue

            for j in range(1,ny+1):
                for k in range(1,nz+1):
                    val = content(i,j,k)
                    err = error(i,j,k)
                    if plane == "yz":
                        hval = h.GetBinContent(k,j)
                        herr = h.GetBinError(k,j)
                    else:
                        hval = h.GetBinContent(j,k)
                        herr = h.GetBinError(j,k)
                    nerrors += check(i,j,k,val,hval,err,herr)
            f.Close()

    return nerrors


def testFlip(fname="test.root", hname="h3"):
    """-flip mirrors the TH3 along the vertical axis of the projection, so the
    vertical bin v shows what bin (n+1-v) held before.  -flipwithaxis must
    produce identical bin contents (it only redraws the y axis)."""

    nerrors = 0
    offset = bins(nz, zmin, zmax)
    for option in ("-flip", "-flipwithaxis"):
        for plane in ("xy", "yx"):
            print("Testing ", plane, option)
            for k,off in enumerate(offset[:2],1):
                f, (h,) = run("%s %s -plane %s -offset %g %s" %
                              (fname, hname, plane, off, option))
                if not f:
                    nerrors += 1
                    continue

                for i in range(1,nx+1):
                    for j in range(1,ny+1):
                        if plane == "xy":       # vertical axis is x
                            val = content(nx+1-i,j,k)
                            err = error(nx+1-i,j,k)
                            hval = h.GetBinContent(j,i)
                            herr = h.GetBinError(j,i)
                        else:                   # vertical axis is y
                            val = content(i,ny+1-j,k)
                            err = error(i,ny+1-j,k)
                            hval = h.GetBinContent(i,j)
                            herr = h.GetBinError(i,j)
                        nerrors += check(i,j,k,val,hval,err,herr)
                f.Close()

    return nerrors


def testMax(fname="test.root", hname="h3"):
    """-max takes, for each (vertical, horizontal) bin, the largest value along
    the normal axis together with its error.  content() grows with k, so the
    maximum always sits in the last bin of the normal axis."""

    nerrors = 0
    print("Testing  -max")
    for plane in ("xy", "yx"):
        f, (h,) = run("%s %s -plane %s -max" % (fname, hname, plane))
        if not f:
            nerrors += 1
            continue

        for i in range(1,nx+1):
            for j in range(1,ny+1):
                val = content(i,j,nz)
                err = error(i,j,nz)
                if plane == "yx":
                    hval, herr = h.GetBinContent(i,j), h.GetBinError(i,j)
                else:
                    hval, herr = h.GetBinContent(j,i), h.GetBinError(j,i)
                nerrors += check(i,j,nz,val,hval,err,herr)
        f.Close()

    return nerrors


def testErrors(fname="testf.root", hname="h3"):
    """-errors replaces every bin value by its relative error in percent."""

    nerrors = 0
    print("Testing  -errors")
    k, off = 3, bins(nz, zmin, zmax)[2]
    f, (h,) = run("%s %s -plane xy -offset %g -errors" % (fname, hname, off))
    if not f:
        return 1

    for i in range(1,nx+1):
        for j in range(1,ny+1):
            val = content(i,j,k)
            err = k*10+j+i                 # as set by buildFloat()
            expected = 100.0*err/val
            nerrors += checkClose("relative error (%d,%d,%d)" % (i,j,k),
                                  expected, h.GetBinContent(j,i))
            nerrors += checkClose("error of the error (%d,%d,%d)" % (i,j,k),
                                  0.0, h.GetBinError(j,i))
    f.Close()

    return nerrors


def testMaxError(fname="testerr.root", hname="h3"):
    """-maxerror suppresses bins whose relative error is at or above the limit.
    The input gives odd i a 1% error and even i a 50% error, so with
    -maxerror 0.1 only the odd-i bins survive."""

    nerrors = 0
    print("Testing  -maxerror")
    k, off = 3, bins(nz, zmin, zmax)[2]
    f, (h,) = run("%s %s -plane xy -offset %g -maxerror 0.1" % (fname, hname, off))
    if not f:
        return 1

    for i in range(1,nx+1):
        for j in range(1,ny+1):
            expected = content(i,j,k) if i % 2 else 0.0
            nerrors += checkClose("bin (%d,%d,%d)" % (i,j,k),
                                  expected, h.GetBinContent(j,i))
    f.Close()

    return nerrors


def testRebin(fname="uniform.root", hname="h3"):
    """-rebin averages the projection down to at most width x height bins.
    A uniform histogram must stay uniform, and the bin counts must shrink by
    ceil(nbins/size)."""

    nerrors = 0
    print("Testing  -rebin")
    width, height = 10, 10
    f, (h,) = run("%s %s -plane xy -offset 0 -rebin -width %d -height %d" %
                  (fname, hname, width, height))
    if not f:
        return 1

    # horizontal axis is y (60 bins -> 10), vertical axis is x (40 bins -> 10)
    if h.GetNbinsX() != width:
        print("Rebinned horizontal axis has", h.GetNbinsX(), "bins, expected", width)
        nerrors += 1
    if h.GetNbinsY() != height:
        print("Rebinned vertical axis has", h.GetNbinsY(), "bins, expected", height)
        nerrors += 1

    for i in range(1, h.GetNbinsX()+1):
        for j in range(1, h.GetNbinsY()+1):
            nerrors += checkClose("rebinned bin (%d,%d)" % (i,j),
                                  1.0, h.GetBinContent(i,j))
    f.Close()

    return nerrors


def testGeometry(fname="test.root", hname="h3", gname="geometry.inp"):
    """With a geometry file hplot cuts it on the plane the data are projected
    on and draws the material boundaries as a TMultiGraph on top.

    Plane "xy" puts y on the horizontal axis and x on the vertical one, so the
    target box shows up as a 4x2 rectangle - but only where the cut crosses
    it, which is what the offset selects."""

    nerrors = 0
    print("Testing  geometry overlay")

    # a cut through the target: the outline is its y-x cross section
    f, (data,) = run("%s %s %s -plane xy -offset 0" % (fname, hname, gname))
    if not f:
        return 1

    outlines = multigraph(f)
    if not outlines:
        print("Geometry outlines were not drawn:", outlines)
        nerrors += 1
    else:
        for points in outlines:
            nerrors += checkOutline(points, BOX["y"], BOX["x"])

    # the data must still be the projection at that offset
    for i in range(1,nx+1):
        for j in range(1,ny+1):
            nerrors += check(i,j,5, content(i,j,5), data.GetBinContent(j,i),
                             error(i,j,5), data.GetBinError(j,i))
    f.Close()

    # a cut past the end of the target (z = 3.5): nothing to outline
    f, _ = run("%s %s %s -plane xy -offset 3.5" % (fname, hname, gname))
    if not f:
        return nerrors+1

    outlines = multigraph(f)
    if outlines is None or outlines:
        print("Outlines drawn for a cut outside the target:", outlines)
        nerrors += 1
    f.Close()

    return nerrors


def testGeometryMacro(fname="test.root", hname="h3", gname="geo.inp"):
    """When no file of that name exists, the geometry comes from the TMacro
    named after it inside the data file, and gives the same outlines."""

    nerrors = 0
    print("Testing  geometry from a TMacro")

    if exists(gname):
        print(gname, "exists - the test would read the file, not the TMacro")
        return 1

    f, _ = run("%s %s %s -plane xy -offset 0" % (fname, hname, gname))
    if not f:
        return 1

    outlines = multigraph(f)
    if not outlines:
        print("Geometry outlines were not drawn:", outlines)
        nerrors += 1
    else:
        for points in outlines:
            nerrors += checkOutline(points, BOX["y"], BOX["x"])
    f.Close()

    return nerrors


def testGeometryMax(fname="test.root", hname="h3", gname="geometry.inp"):
    """With -max the data lose their normal axis and the offset applies to the
    geometry alone, which is how a representative cut is chosen.  For plane
    "yz" the normal axis is x, not z."""

    nerrors = 0
    print("Testing  geometry with -max")

    # x = 0.5 crosses the target: the outline is its z-y cross section
    f, (data,) = run("%s %s %s -plane yz -max -offset 0" % (fname, hname, gname))
    if not f:
        return 1

    outlines = multigraph(f)
    if not outlines:
        print("Geometry outlines were not drawn:", outlines)
        nerrors += 1
    else:
        for points in outlines:
            nerrors += checkOutline(points, BOX["z"], BOX["y"])

    for j in range(1,ny+1):
        for k in range(1,nz+1):
            # the largest value along x is the one at i = nx
            nerrors += checkClose("max data (%d,%d)" % (j,k),
                                  content(nx,j,k), data.GetBinContent(k,j))
    f.Close()

    # x = 1.5 is past the end of the target: nothing to outline
    f, _ = run("%s %s %s -plane yz -max -offset 1.5" % (fname, hname, gname))
    if not f:
        return nerrors+1

    outlines = multigraph(f)
    if outlines is None or outlines:
        print("Outlines drawn for a cut outside the target:", outlines)
        nerrors += 1
    f.Close()

    return nerrors


def main():
    build("test.root", "h3")
    buildFloat("testf.root", "h3")
    buildFloat("testerr.root", "h3", relerr=lambda i: 0.01 if i % 2 else 0.5)
    buildGeometry("geometry.inp")
    buildUniform("uniform.root", "h3", 40, 60, 2)
    addMacro("test.root", "geo")

    nerrors = 0
    nerrors += testXY()
    nerrors += testXZ()
    nerrors += testYZ()
    nerrors += testFlip()
    nerrors += testMax()
    nerrors += testErrors()
    nerrors += testMaxError()
    nerrors += testRebin()
    nerrors += testGeometry()
    nerrors += testGeometryMacro()
    nerrors += testGeometryMax()

    if nerrors == 0:
        system("rm -f hplot.root test.root testf.root testerr.root geometry.inp uniform.root")
        print("OK")
    else:
        print(nerrors, " errors found")

    return nerrors

if __name__ == "__main__":
    exit(main())
