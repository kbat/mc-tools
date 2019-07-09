#!/usr/bin/python -W all
#
# https://github.com/kbat/mc-tools
#

from __future__ import print_function
import argparse
from sys   import exit
from array import array
from math  import sqrt
import ROOT
from mctools.common import FlipTH2
ROOT.PyConfig.IgnoreCommandLineOptions = True

# runs in both Python 2 and 3
try:
        input = raw_input
except NameError:
        pass

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
        parser.add_argument("-plane",type=str, dest='plane', help='Plane', default="xy", choices=['xy','xz','yx','yz','xz','zy'])
        parser.add_argument("-scale", type=float, dest='scale', help='Scale', default=1.0)
        parser.add_argument("-doption", type=str, dest='doption', help='Data draw option', default="colz")
        parser.add_argument("-goption", type=str, dest='goption', help='Geometry draw option', default="cont3")
        parser.add_argument("-dcont", type=int, dest='dcont', help='Set the number of contour levels for data', default=200)
        parser.add_argument("-gcont", type=int, dest='gcont', help='Set the number of contour levels for geometry', default=25)
        parser.add_argument("-glwidth", type=int, dest='glwidth', help='Geometry line width', default=2)
        parser.add_argument("-glcolor", type=str, dest='glcolor', help='Geometry line color (ROOT names)', default="kBlack")
        parser.add_argument("-title", type=str, dest='title',   help='Plot title',   default=None)
        parser.add_argument("-xtitle", type=str, dest='xtitle', help='x-axis title', default=None)
        parser.add_argument("-ytitle", type=str, dest='ytitle', help='y-axis title', default=None)
        parser.add_argument("-ztitle", type=str, dest='ztitle', help='z-axis title', default=None)
        parser.add_argument("-width",  type=int, dest='width',  help='Canvas width',  default=800)
        parser.add_argument("-height", type=int, dest='height', help='Canvas height. If not specified, it is calculated from the width with the golden ratio rule.', default=None)
        parser.add_argument("-right-margin", type=float, dest='right_margin',
                            help='Right margin of the canvas in order to allocate enough space for the z-axis title. \
                            Used only if ZTITLE is set and DOPTION="colz"', default=0.17)
        parser.add_argument("-logz", action='store_true', default=True, dest='logz', help='Set log scale for the data colour axis')
        parser.add_argument("-flip", action='store_true', default=False, dest='flip', help='Flip the vertical axis')
        parser.add_argument("-bgcol", action='store_true', default=False, dest='bgcol', help='Set the frame background colour to some hard-coded value')
        parser.add_argument("-o", type=str, dest='output', help='Output file name. If given then the canvas is not shown.', default="")

	args = parser.parse_args()

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

        df = ROOT.TFile(args.dfile)
        dh = df.Get(args.dhist)

        dh2 = dh.Project3D(args.plane)
        dh2.Scale(args.scale)

        if args.flip:
                dh2 = FlipTH2(dh2)

        if args.title:
            dh2.SetTitle(args.title)

        if args.xtitle:
            dh2.SetXTitle(args.xtitle)
            
        if args.ytitle:
            dh2.SetYTitle(args.ytitle)
            
        if args.ztitle:
            if args.doption == 'colz':
                c1.SetRightMargin(args.right_margin);
            dh2.SetZTitle(args.ztitle)
        
        dh2.Draw(args.doption)
        dh2.SetContour(args.dcont)

        if args.logz:
            ROOT.gPad.SetLogz()

        if args.gfile is not None:
            gf = ROOT.TFile(args.gfile)
            gh = gf.Get(args.ghist)
            gh2 = gh.Project3D(args.plane)
            if args.flip:
                    gh2 = FlipTH2(gh2)
            gh2.SetLineWidth(args.glwidth)
            gh2.SetLineColor(eval("ROOT.%s" % args.glcolor))
            gh2.SetContour(args.gcont)
            gh2.Draw("same %s" % args.goption)

        ci = ROOT.TColor.GetFreeColorIndex()
        color = ROOT.TColor(ci,0.27843137254900002, 0.27843137254900002, 0.6)

        if args.bgcol:
                c1.Update()
                c1.GetFrame().SetFillColor(ci)
                dh2.GetXaxis().SetAxisColor(ci)
                dh2.GetYaxis().SetAxisColor(ci)

        if args.output:
                ROOT.gPad.Print(args.output)
        else:
                ROOT.gPad.GetCanvas().ToggleEventStatus()
                input()

if __name__ == "__main__":
    exit(main())
