#!/usr/bin/env python3

from sys import argv, exit, stderr
from math import sqrt
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from mctools.common.CombLayer import getPar as getParCL
import glob, os, argparse
from array import array
from datetime import datetime

# runs in both Python 2 and 3
try:
        input = raw_input
except NameError:
        pass

def saveGraph(gr, fout):
    """
    Saves gr into fout
    """
    f = ROOT.TFile(fout, "update")
    gr.Write(gr.GetName(), ROOT.TObject.kOverwrite)
    f.Close()

def printGraph(gr):
    """ Prints TGraphErrors """
    print("# ", gr.GetTitle())
    print("# format: x ex y ey")
    N = gr.GetN()
    for i in range(N):
        print("case%03d:" % (i+1), gr.GetX()[i], gr.GetEX()[i], gr.GetY()[i], gr.GetEY()[i])

def getHistAxis(obj, i):
        """Return TH3 axis based on its number

        0: X-axis
        1: Y-axis
        2: Z-axis
        """
        if i==0:
                if obj.Class().InheritsFrom(ROOT.TH1.Class()):
                        return obj.GetXaxis()
                else:
                        raise ValueError('getHistAxis: object %s does not have x-axis', obj.GetName())
        elif i==1:
                if obj.Class().InheritsFrom(ROOT.TH2.Class()) or obj.Class().InheritsFrom(ROOT.TH3.Class()):
                        return obj.GetYaxis()
                else:
                        raise ValueError('getHistAxis: object %s does not have y-axis', obj.GetName())
        elif i==2:
                if obj.Class().InheritsFrom(ROOT.TH3.Class()):
                        return obj.GetZaxis()
                else:
                        raise ValueError('getHistAxis: object %s does not have z-axis', obj.GetName())
        else:
                raise ValueError('getHistAxis: i=%d must be <=2', i)

def getGraph(args, tname, color):
    x = []
    ex = []
    y = []
    ey = []
    for mctal in glob.glob(args.mctal):
        dirname = os.path.split(mctal)[0]
#        print(dirname)
        inp = os.path.join(dirname, args.inp)
        f = ROOT.TFile(mctal)
        obj = f.Get(tname)
        if obj.Class().InheritsFrom(ROOT.THnSparse.Class()):
                for r in args.rangebin:
                        obj.GetAxis(r[0]).SetRange(r[1], r[2])
                for r in args.rangeuser:
                        obj.GetAxis(int(r[0])).SetRangeUser(float(r[1]), float(r[2]))
                if args.axis>=0: # axis and bin are specified for th1
                        tally = obj.Projection(args.axis);
                else: # args.bin is absolute bin number
                        tally = obj
        else: # e.g. TH1, TH2 or TH3
                for r in args.rangebin:
                        getHistAxis(r[0]).SetRange(r[1], r[2])
                for r in args.rangeuser:
                        getHistAxis(int(r[0])).SetRangeUser(float(r[1]), float(r[2]))
                tally = obj

        x.append(eval("%g%s" % (getParCL(inp, args.var, int(args.varpos), args.comment), args.xscale)))
        ex.append(0.0)

        bins = args.bin.split('+')
        ytmp = 0.0
        eytmp = 0.0
        for b in bins:
            thebin = int(b.strip())
            ytmp += tally.GetBinContent(thebin)
#            print(b,thebin,ytmp)
            eytmp += pow(tally.GetBinError(thebin), 2)
        eytmp = sqrt(eytmp)
        y.append(eval("%g%s" % (ytmp, args.yscale)))
        ey.append(eval("%g%s" % (eytmp, args.yscale)))
        f.Close()
#    print(x)
#    print(y)

# sort all arrays
    x,y,ex,ey = list(zip(*sorted(zip(x,y,ex,ey))))
    gr = ROOT.TGraphErrors(len(x), array('f', x), array('f', y), array('f', ex), array('f', ey))
    gr.SetNameTitle("gr%s" % tname, args.title)
    gr.GetXaxis().SetTitle(args.xtitle)
    gr.GetYaxis().SetTitle(args.ytitle)
    gr.SetMarkerStyle(ROOT.kFullCircle)
    gr.SetMarkerColor(color)
    return gr

def getAverage(args, mg):
    """
    Return average of graphs in TMultiGraph.
    Assumed that all graphs have the same x-coordinates
    """
    x = []
    ex = []
    y = []
    ey = []
    title = "Average of "
    graphs = mg.GetListOfGraphs()
    graphs.ls()
    ngr = graphs.GetSize()
    first = True
    for gr in graphs:
        N = gr.GetN()
        title = title + " " + gr.GetTitle()
        for i in range(N):
            if first:
                x.append(gr.GetX()[i])
                ex.append(0.0)
                y.append(gr.GetY()[i]/ngr)
                ey.append(pow(gr.GetEY()[i], 2))
            else:
                y[i] = y[i] + gr.GetY()[i]/ngr
                ey[i] = ey[i] + pow(gr.GetEY()[i], 2)/ngr
        first = False
        ey = list(map(sqrt, ey))

    gr = ROOT.TGraphErrors(len(x), array('f', x), array('f', y), array('f', ex), array('f', ey))
    gr.SetNameTitle("grAverage", "%s;%s;%s" % (title, args.xtitle, args.ytitle))
#    gr.SetNameTitle("grAverage", "%s;%s;%s" % ("", args.xtitle, args.ytitle))
    gr.SetMarkerStyle(ROOT.kOpenSquare)
    gr.SetLineStyle(ROOT.kSolid)
    gr.SetMarkerColor(ROOT.kBlack)
    return gr

def main():
    """
    Plots figure-of-merit as a function of the specified variable. Supports both MCNP and FLUKA syntax / data files.
    If getfom-analysis.py file exists in the current folder, evaluates it line-by-line in the end of the script
    """
    ROOT.gStyle.SetOptFit(0)

    parser = argparse.ArgumentParser(description=main.__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter,epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-tally', dest='tally', type=str, default="f5", help='Tally name')
    parser.add_argument('-axis', dest='axis', type=int, default=6, help='axis to project THnSparse on. If<0, the absolute value of BIN must be specified (see next argument). This option make sence only for THnSparse objects.')
    parser.add_argument('-range', dest='rangebin', action="append", nargs=3, type=int, help='axis number followed by range of bins to set its range (e.g. 6 1 10 will call GetAxis(6)->SetRange(1,10)). +see also description of -range-user',default=[])
    parser.add_argument('-range-user', dest='rangeuser', action="append", nargs=3, help='axis number followed by range of values to set its user range (e.g. 6 0.5 100.5 will call GetAxis(6)->SetRangeUser(0.5,100.5)). This option can be repeated for several axes. If both -range and -range-user are specified for the same axis, the latter takes precedence. For the TH[123] histograms the [XYZ] axes are called by integer counting from zero.', default=[])
    parser.add_argument('-bin', dest='bin', type=str, default="1", help='bin number to use as the figure of merit. Plus-sign-separated list of bins is allowed: the result will be the sum over all bins. Hint for the MCNP case: the bin number is the serial number of the bin in the outp file provided that no FQ print hierarhy was used.')
    parser.add_argument('-title', dest='title', type=str, default="", help='graph title')
    parser.add_argument('-xtitle', dest='xtitle', type=str, default="par [cm]", help='x-axis title')
    parser.add_argument('-ytitle', dest='ytitle', type=str, default="Figure of Merit [a.u.]", help='y-axis title')
    parser.add_argument('-xscale', dest='xscale', type=str, help='x-scaling factor. It will be evaluated as eval(\"x XSCALE\").', default="*1")
    parser.add_argument('-yscale', dest='yscale', type=str, help='y-scaling factor. It will be evaluated as eval(\"y YSCALE\").', default="/1.0")
    parser.add_argument('-fit', dest='fit', type=str, default="", help='fitting function')
    parser.add_argument('-pdf', dest='pdf', type=str, default="do not save", help='PDF file name to save canvas to')
    parser.add_argument('-only-average', dest='average', action='store_true', help='Draws only average of all points')
    parser.add_argument('-no-footer', dest='nofooter', action='store_true', help='Do not draw footer')
    parser.add_argument('-dump', dest='dump', action='store_true', help='Dump the values in stdout')
    parser.add_argument('-save', dest='save', type=str, help='Saves resulting graph into a ROOT file', default="")
    parser.add_argument('-varpos', dest='varpos', default=2, help='position of the variable\'s value in the input file')
    parser.add_argument('-mctal', dest='mctal', default="case*/mctal.root", help='list of mctal files to use')
    parser.add_argument('-inp', dest='inp', default="inp", help='input file name')
    parser.add_argument('-comment', dest='comment', default=None, help="input file comment symbol. Default value: if file extension is 'inp' then comment is set to '*', otherwise to 'c' ")
    parser.add_argument('var', type=str, help='CombLayer variable to plot (see also -varpos). It must be written as a commented string in the MCNP input deck.')

    args = parser.parse_args()

    if args.comment is None:
            if os.path.splitext(args.inp)[1] == ".inp": # assume FLUKA
                    args.comment = "*"
            else: # assume MCNP
                    args.comment = "c"

    tallies = args.tally.split(',')

    # fix x title
    if args.xtitle=="par [cm]": args.xtitle = args.var + " [cm]"
    if args.title == "": args.title = args.tally

    hs = ROOT.TMultiGraph("hs", "%s;%s;%s" % (args.title, args.xtitle, args.ytitle))
    legymin = 1-0.1*len(tallies)
    if legymin<0.1:
        legymin=0.1
    leg = ROOT.TLegend(0.91, legymin, 0.99, 0.9)
    colors = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen+3, ROOT.kViolet, ROOT.kOrange-3]
    for i in range(100):
        colors.append(ROOT.kYellow+i)
    for i,tally in enumerate(tallies):
        gr = getGraph(args, tally, colors[i])
        hs.Add(gr)
        leg.AddEntry(gr, gr.GetTitle(), "p")
        if args.dump:
                printGraph(gr)
        if args.save != "":
            saveGraph(gr, args.save)

    # draw fit if only one graph is requested
    if hs.GetListOfGraphs().GetSize()==1 and len(args.fit):
            gr.Fit(args.fit)
#        gr.GetFunction(args.fit).SetLineColor(gr.GetMarkerColor())


    grav = getAverage(args, hs)
    if args.title != args.tally:
        grav.SetTitle("%s;%s;%s" % (args.title, args.xtitle, args.ytitle))

    if args.average:
        grav.Draw("ap")
        if args.fit != "":
            grav.Fit(args.fit)
    else:
        hs.Draw("ap")
        if hs.GetListOfGraphs().GetSize()>1:
            grav.Draw("same,p,e")
            if args.fit:
                grav.Fit(args.fit)
                grav.GetFunction(args.fit).SetLineColor(grav.GetMarkerColor())
                leg.AddEntry(grav, "Average", "l")
            else:
                leg.AddEntry(grav, "Average", "p")
#        leg.Draw()

#    ROOT.gPad.SetLogx()

    ROOT.gPad.Update()
#    if args.fit:
#        st = gr.FindObject("stats")
#        st.SetX2NDC(0.9)
    ROOT.gPad.SetGrid()

#    hs.SetMinimum(4E+13)
#    hs.SetMaximum(6E+13)

    if not args.nofooter:
        footer = ROOT.TLatex()
        footer.SetTextSize(0.01)
        footer.SetTextColor(ROOT.kGray)
        footer.SetNDC(ROOT.kTRUE)
        vardict = vars(args)
        vardict.pop('xtitle', None)
        vardict.pop('ytitle', None)
        vardict.pop('title', None)
        # vardict.pop('average', None)
        vardict.pop('nofooter', None)
        if not args.fit:
            vardict.pop('fit', None)
        if args.xscale == "*1":
            vardict.pop('xscale', None)
        if args.yscale == "/1.0":
            vardict.pop('yscale', None)
        footer.DrawLatex(0.0, 0.005, "%s %s %s" % (datetime.now().strftime("%Y-%m-%d"), str(vardict), os.getcwd() )) #.replace('/home/kbat', '~')))

#    gr.SaveAs("fom.root")

    # perform analysis on request
    analysis_fname = "getfom-analysis.py"
    if os.path.isfile(analysis_fname):
        fan = open(analysis_fname)
        for l in fan.readlines():
            # "The Python 3 syntax without the global and local dictionaries
            # will work in Python 2 as well:" (from `Supporting Python 3' by L. Regebro et al.)
            exec(l)
        fan.close()

    if args.pdf == "do not save":
        input()
    else:
        ROOT.gPad.Print(args.pdf)




if __name__=="__main__":
    exit(main())
