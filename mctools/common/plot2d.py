#!/usr/bin/python -W all
#
# https://github.com/kbat/mc-tools
#

import sys, argparse
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

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
        parser.add_argument("-dcont", type=int, dest='dcont', help='Set the number of contour levels', default=200)
        parser.add_argument("-glwidth", type=int, dest='glwidth', help='Geometry line width', default=2)
        parser.add_argument("-glcolor", type=str, dest='glcolor', help='Geometry line color (ROOT names)', default="kBlack")
        parser.add_argument("-title", type=str, dest='title',   help='Plot title',   default=None)
        parser.add_argument("-xtitle", type=str, dest='xtitle', help='x-axis title', default=None)
        parser.add_argument("-ytitle", type=str, dest='ytitle', help='y-axis title', default=None)
        parser.add_argument("-ztitle", type=str, dest='ztitle', help='z-axis title', default=None)
        parser.add_argument("-right-margin", type=float, dest='right_margin',
                            help='Right margin of the canvas in order to allocate enough space for the z-axis title. \
                            Used only if ZTITLE is set and DOPTION="colz"', default=0.17)
        parser.add_argument("-logz", action='store_true', default=True, dest='logz', help='Set log scale for the colour axis')
	parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

	args = parser.parse_args()

        ROOT.gStyle.SetOptStat(False)
        ROOT.gStyle.SetPalette(ROOT.kTemperatureMap)
        
        
        df = ROOT.TFile(args.dfile)
        dh = df.Get(args.dhist)

        dh2 = dh.Project3D(args.plane)
        dh2.Scale(args.scale)

        if args.title:
            dh2.SetTitle(args.title)

        if args.xtitle:
            dh2.SetXTitle(args.xtitle)
            
        if args.ytitle:
            dh2.SetYTitle(args.ytitle)
            
        if args.ztitle:
            if args.doption == 'colz':
                ROOT.gStyle.SetPadRightMargin(args.right_margin);
            dh2.SetZTitle(args.ztitle)
        
        dh2.Draw(args.doption)
        dh2.SetContour(args.dcont)

        if args.logz:
            ROOT.gPad.SetLogz()


        print "a", args.gfile
        if args.gfile is not None:
            gf = ROOT.TFile(args.gfile)
            gh = gf.Get(args.ghist)
            gh2 = gh.Project3D(args.plane)
            gh2.SetLineWidth(args.glwidth)
            gh2.SetLineColor(eval("ROOT.%s" % args.glcolor))
            gh2.Draw("same %s" % args.goption)

        ROOT.gPad.GetCanvas().ToggleEventStatus()
        
        input()

if __name__ == "__main__":
    sys.exit(main())
