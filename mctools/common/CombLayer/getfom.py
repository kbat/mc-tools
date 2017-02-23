#! /usr/bin/python

from sys import argv, exit
from math import sqrt
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from comblayer import getPar as getParCL
import glob, os, argparse
from array import array
from datetime import datetime

def saveGraph(gr, fout):
    """
    Saves gr into fout
    """
    f = ROOT.TFile(fout, "update")
    gr.Write(gr.GetName(), ROOT.TObject.kOverwrite)
    f.Close()

def printGraph(gr):
    """ Prints TGraphErrors """
    print "# ", gr.GetTitle()
    print "# format: x ex y ey"
    N = gr.GetN()
    for i in range(N):
        print i, gr.GetX()[i], gr.GetEX()[i], gr.GetY()[i], gr.GetEY()[i]

def getGraph(args, tname, color):
    x = []
    ex = []
    y = []
    ey = []
    for mctal in glob.glob(args.mctal):
        dirname = os.path.split(mctal)[0]
#        print dirname
        inp = os.path.join(dirname, 'inp')
        f = ROOT.TFile(mctal)
        if args.axis>=0: # axis and bin are specified
            f.Get(tname).GetAxis(2).SetRange(1,1)
            print >> sys.stderr, "f.Get(tname).GetAxis(2).SetRange(1,1) called!"
            tally = f.Get(tname).Projection(args.axis);
        else: # args.bin is absolute bin number
            tally = f.Get(tname)
        x.append(eval("%g%s" % (getParCL(inp, args.var, int(args.varpos)), args.xscale)))
        ex.append(0.0)

        bins = args.bin.split(',')
#        print "args.bin: ", bins
        nbins = len(bins)
        ytmp = 0.0
        eytmp = 0.0
        for b in bins:
            thebin = int(b.strip())
            ytmp += tally.GetBinContent(thebin)
            eytmp += pow(tally.GetBinError(thebin), 2)
        eytmp = sqrt(eytmp)
        y.append(eval("%g%s" % (ytmp, args.yscale)))
        ey.append(eval("%g%s" % (eytmp, args.yscale)))
        f.Close()
#    print x
#    print y

# sort all arrays
    x,y,ex,ey = zip(*sorted(zip(x,y,ex,ey)))
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
        ey = map(sqrt, ey)

    gr = ROOT.TGraphErrors(len(x), array('f', x), array('f', y), array('f', ex), array('f', ey))
    gr.SetNameTitle("grAverage", "%s;%s;%s" % (title, args.xtitle, args.ytitle))
#    gr.SetNameTitle("grAverage", "%s;%s;%s" % ("", args.xtitle, args.ytitle))
    gr.SetMarkerStyle(ROOT.kOpenSquare)
    gr.SetLineStyle(ROOT.kSolid)
    gr.SetMarkerColor(ROOT.kBlack)
    return gr

def main():
    """
    If getfom-analysis.py file exists in the current folder, evaluates it line-by-line in the end of the script
    """
    ROOT.gStyle.SetOptFit(0)

    parser = argparse.ArgumentParser(description=main.__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-tally', dest='tally', type=str, default="f5", help='Tally name')
    parser.add_argument('-axis', dest='axis', type=int, default=6, help='axis to project THnSparse on. If <0, the absolute value of BIN must be specified (see next argument).')
    parser.add_argument('-bin', dest='bin', type=str, default="1", help='bin of the axis to use as the figure of merit. Comma-separated list of bins is allowed, then the result will be the sum over all bins')
    parser.add_argument('-title', dest='title', type=str, default="", help='graph title')
    parser.add_argument('-xtitle', dest='xtitle', type=str, default="par [cm]", help='x-axis title')
    parser.add_argument('-ytitle', dest='ytitle', type=str, default="Figure of Merit [a.u.]", help='y-axis title')
    parser.add_argument('-xscale', dest='xscale', type=str, help='x-scaling factor. It will be evaluated as eval(\"x XSCALE\").', default="*1")
    parser.add_argument('-yscale', dest='yscale', type=str, help='y-scaling factor. It will be evaluated as eval(\"y YSCALE\").', default="/1.0")
    parser.add_argument('-fit', dest='fit', type=str, default="", help='fitting function')
    parser.add_argument('-pdf', dest='pdf', type=str, default="do not save", help='PDF file name to save canvas to')
    parser.add_argument('-only-average', dest='average', action='store_true', help='Draws only average of all points')
    parser.add_argument('-no-footer', dest='footer', action='store_false', help='Do not draw footer')
    parser.add_argument('-dump', dest='dump', action='store_true', help='Dump the values in stdout')
    parser.add_argument('-save', dest='save', type=str, help='Saves resulting graph into a ROOT file', default="")
    parser.add_argument('-varpos', dest='varpos', default=2, help='position of the variable\'s value in the input file')
    parser.add_argument('-mctal', dest='mctal', default="case*/mctal.root", help='list of mctal files to use')
    parser.add_argument('var', type=str, help='CombLayer variable to plot (see also -varpos). It must be written as a commented string in the MCNP input deck.')
    args = parser.parse_args()


    tallies = args.tally.split(',')
    ntallies = len(tallies)

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
    if hs.GetListOfGraphs().GetSize()==1:
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

    if args.footer:
        footer = ROOT.TLatex()
        footer.SetTextSize(0.02)
        footer.SetTextColor(ROOT.kGray)
        footer.SetNDC(ROOT.kTRUE)
        vardict = vars(args)
        vardict.pop('xtitle', None)
        vardict.pop('ytitle', None)
        vardict.pop('title', None)
        vardict.pop('average', None)
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
            exec l


    if args.pdf == "do not save":
        input()
    else:
        ROOT.gPad.Print(args.pdf)
    
        


if __name__=="__main__":
    exit(main())
