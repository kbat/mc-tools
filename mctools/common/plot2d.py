#!/usr/bin/env python3
#
# https://github.com/kbat/mc-tools
#

import argparse
from sys   import exit
from array import array
from math  import sqrt
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from mctools.common import FlipTH2, DynamicSlice, ErrorHist

# runs in both Python 2 and 3
try:
        input = raw_input
except NameError:
        pass

def checkMinMax(parser,vmin,vmax,title):
        """ Checks min/max values """
        if vmin != None and vmax is None:
                parser.error("Both %smin and %smax must be set." % (title,title))
        elif vmax != None and vmin is None:
                parser.error("Both %smin and %smax must be set." % (title,title))
        elif vmin != None and vmax !=None and vmin >= vmax:
                parser.error("%smin must be < %smax" % (title,title))

def setColourMap():
        """ Sets the colour map used at MAX IV """

        # PView is exported from ParaView
        PView = (0, 0.27843137254900002, 0.27843137254900002, 0.85882352941200002, 0.143, 0, 0, 0.36078431372500003, 0.285, 0, 1, 1, 0.429, 0, 0.50196078431400004, 0, 0.571, 1, 1, 0, 0.714, 1, 0.38039215686299999, 0, 0.857, 0.419607843137, 0, 0, 1, 0.87843137254899994, 0.30196078431399997, 0.30196078431399997)

        NCont = 99
        NRGBs = 8
        stops = []
        red = []
        green = []
        blue = []

        for i in range(NRGBs):
                stops.append(PView[4*i])
                red.append(PView[4*i+1])
                green.append(PView[4*i+2])
                blue.append(PView[4*i+3])

        stops = array('d',stops)
        red   = array('d',red)
        green = array('d',green)
        blue  = array('d',blue)

        ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
        ROOT.gStyle.SetNumberContours(NCont)

def main():
        """A simple TH2 plotter with optional geometry overlay
        """
        parser = argparse.ArgumentParser(description=main.__doc__,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         epilog="Homepage: https://github.com/kbat/mc-tools")
        parser.add_argument('dfile', type=str, help='Data file name')
        parser.add_argument('dhist', type=str, help='Data histogram name')
        parser.add_argument('gfile', type=str, help='Geometry file name', nargs='?')
        parser.add_argument('ghist', type=str, help='Geometry histogram name', nargs='?', default='h3')
        parser.add_argument("-plane",type=str, dest='plane', help='Plane', default="xy", choices=['xy','xz','yx','yz','zx','zy'])
        parser.add_argument("-scale",   type=float, dest='scale', help='Scale', default=1.0)
        parser.add_argument("-doption", type=str, dest='doption', help='Data draw option', default="colz")
        parser.add_argument("-goption", type=str, dest='goption', help='Geometry draw option', default="cont3")
        parser.add_argument("-dcont", type=int, dest='dcont', help='Set the number of contour levels for data', default=200)
        parser.add_argument("-gcont", type=int, dest='gcont', help='Set the number of contour levels for geometry', default=25)
        parser.add_argument("-glwidth", type=int, dest='glwidth', help='Geometry line width', default=2)
        parser.add_argument("-glcolor", type=str, dest='glcolor', help='Geometry line color (ROOT names)', default="kBlack")
        parser.add_argument("-title",  type=str, dest='title',   help='Plot title',   default=None)
        parser.add_argument("-xtitle", type=str, dest='xtitle', help='horizontal axis title', default=None)
        parser.add_argument("-ytitle", type=str, dest='ytitle', help='vertical axis title', default=None)
        parser.add_argument("-ztitle", type=str, dest='ztitle', help='colour axis title', default=None)
        parser.add_argument("-xmin",   type=float, dest='xmin', help='horizontal axis min value', default=None, required=False)
        parser.add_argument("-xmax",   type=float, dest='xmax', help='horizontal axis max value', default=None, required=False)
        parser.add_argument("-ymin",   type=float, dest='ymin', help='vertical axis min value', default=None, required=False)
        parser.add_argument("-ymax",   type=float, dest='ymax', help='vertical axis max value', default=None, required=False)
        parser.add_argument("-zmin",   type=float, dest='zmin', help='colour axis min value', default=None, required=False)
        parser.add_argument("-zmax",   type=float, dest='zmax', help='colour axis max value', default=None, required=False)
        parser.add_argument("--no-logz", action='store_true', default=False, dest='nologz', help='Remove log scale for the data colour axis')
        parser.add_argument("-width",  type=int, dest='width',  help='Canvas width',  default=800)
        parser.add_argument("-height", type=int, dest='height', help='Canvas height. If not specified, it is calculated from the width with the golden ratio rule.', default=None)
        parser.add_argument("-right-margin", type=float, dest='right_margin',
                            help='Right margin of the canvas in order to allocate enough space for the z-axis title. \
                            Used only if ZTITLE is set and DOPTION="colz"', default=0.12)
        parser.add_argument("-flip", action='store_true', default=False, dest='flip', help='Flip the vertical axis')
        parser.add_argument("-bgcol", action='store_true', default=False, dest='bgcol', help='Set the frame background colour to some hard-coded value')
        parser.add_argument("-o", type=str, dest='output', help='Output file name. If given then the canvas is not shown.', default="")
        parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')
        parser.add_argument('-slice', type=int, dest='slice', nargs=2, help='Show live slice averaging the given number of bins. Left mouse click on the 2D histogram swaps axes, middle button click swaps logy. Two integer numbers are required: the first one is the number of bins to average the slice on 2D histogrm, the second one indicates how many bins of this have to be merged into one bin in the 1D histogram', default=None)
        parser.add_argument('-errors', action='store_true', default=False, dest='errors', help='Plot the histogram with relative errors instead of data')

        args = parser.parse_args()

        checkMinMax(parser, args.xmin, args.xmax, 'x')
        checkMinMax(parser, args.ymin, args.ymax, 'y')

        if args.slice != None and (args.slice[0] < 1 or args.slice[1]<1):
                parser.error("slice values must be >= 1")

        ROOT.gStyle.SetOptStat(False)
        ROOT.gStyle.SetPalette(ROOT.kTemperatureMap)

        if args.output:
                ROOT.gROOT.SetBatch(True)

        height = args.height
        if height is None:
                height = int(args.width * 2.0 / (1.0+sqrt(5.0))) # golden ratio

        c1title = args.dfile+" "+args.dhist+" "+args.plane
        c1 = ROOT.TCanvas("c1", c1title, args.width, height)
        setColourMap()

        if args.slice:
                c1.Divide(1,2)
        c1.cd(1)
        pad1 = ROOT.gPad

        df = ROOT.TFile(args.dfile)
        dh = df.Get(args.dhist)
        if not dh:
                print("ERROR: Can't find object '%s' in %s" % (args.dhist, args.dfile))
                exit(1)

        if args.verbose: print("Projecting 3D data onto 2D histogram")

        dh2 = dh.Project3D(args.plane)
        dh2.Scale(args.scale)

        if args.errors:
                if args.verbose:
                        print("Showing the histogram with errors")
                dh2 = ErrorHist(dh2)
                args.ztitle = "Relative error [%]"
                if args.zmin:
                        args.zmin = 0
                        if args.verbose: print("zmin set to 0")
                if args.zmax and args.zmax>100:
                        args.zmax = 100
                        if args.verbose: print("zmax set to 100")
                args.nologz = True

        if args.flip:
                if args.verbose: print("Flipping the data histogram")
                dh2 = FlipTH2(dh2)

        if args.title is not None:
                dh2.SetTitle(args.title)

        if args.xtitle:
            dh2.SetXTitle(args.xtitle)

        if args.ytitle:
            dh2.SetYTitle(args.ytitle)

        if args.ztitle:
                if args.doption == 'colz':
                        pad1.SetRightMargin(args.right_margin);
                dh2.SetZTitle(args.ztitle)

        if args.verbose: print("Drawing data")

        dh2.Draw(args.doption)
        dh2.SetContour(args.dcont)
        pad1.Update()

        if args.xmin is not None:
                dh2.GetXaxis().SetRangeUser(args.xmin, args.xmax)

        if args.ymin is not None:
                dh2.GetYaxis().SetRangeUser(args.ymin, args.ymax)

        if not args.nologz:
                ROOT.gPad.SetLogz()

        if args.zmin is not None:
                dh2.SetMinimum(args.zmin)

        if args.zmax is not None:
                dh2.SetMaximum(args.zmax)

        if args.gfile is not None:
            gf = ROOT.TFile(args.gfile)
            gh = gf.Get(args.ghist)
            if not gh:
                print("ERROR: Can't find object '%s' in %s" % (args.ghist, args.gfile))
                exit(1)

            if args.verbose: print("Projecting 3D geometry onto 2D histogram")
            gh2 = gh.Project3D(args.plane)
            if args.flip:
                    if args.verbose: print("Flipping the geometry histogram")
                    gh2 = FlipTH2(gh2)
            gh2.SetLineWidth(args.glwidth)
            gh2.SetLineColor(eval("ROOT.%s" % args.glcolor))
            gh2.SetContour(args.gcont)
            gh2.Draw("same %s" % args.goption)

        ci = ROOT.TColor.GetFreeColorIndex()
        color = ROOT.TColor(ci,0.27843137254900002, 0.27843137254900002, 0.6)

        if args.bgcol:
                if args.verbose: print("Setting the background color")
                pad1.Update()
                pad1.GetFrame().SetFillColor(ci)
                dh2.GetXaxis().SetAxisColor(ci)
                dh2.GetYaxis().SetAxisColor(ci)

        if args.slice:
                import __main__
                __main__.slicer = DynamicSlice.DynamicSlice(dh2, args.slice)
                pad1.AddExec('dynamic', 'TPython::Exec( "slicer()" );')

        if args.verbose: print("Done")
        if args.output:
                ROOT.gPad.Print(args.output)
        else:
                ROOT.gPad.GetCanvas().ToggleEventStatus()
                input()

if __name__ == "__main__":
    exit(main())
