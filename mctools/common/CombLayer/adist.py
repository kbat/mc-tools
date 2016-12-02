#! /usr/bin/python -W all

from sys import argv, exit
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os, argparse, re, math

def getFOM(mctal, tname, bins):
    """
    Return figure-of-merit
    """
    f = ROOT.TFile(mctal)
    f.Get(tname).GetAxis(2).SetRange(1,1)
    tally = f.Get(tname).Projection(6);

    ytmp = 0.0
    eytmp = 0.0
    for b in bins:
        thebin = int(b.strip())
        ytmp += tally.GetBinContent(thebin)
        eytmp += pow(tally.GetBinError(thebin), 2)
    eytmp = math.sqrt(eytmp)

    return ytmp,eytmp

def getTheta(tname, inp):
    """
    Return the polar angle of a point detector tally 'tname' in the input file 'inp'
    """
    theta = 0.0
    found = False
    f = open(inp)
    for line in f.readlines():
        if re.search("\A%s:" % tname, line, re.IGNORECASE):
            w = line.split()
            x,y = map(float, w[1:3])
            if math.atan2(x,y)>0:
                theta = math.atan2(x,y)
            else:
                theta = 2*math.pi + math.atan2(x,y)
            theta *= 180/math.pi
            if found == True:
                print "Error: theta has already been found in ", inp
            Found = True
            
#            print inp, tname, x,y, theta
    f.close()
    return theta
    


def main():
    """
    Draws angular distribution
    """
    ROOT.gStyle.SetOptFit(0)

    parser = argparse.ArgumentParser(description=main.__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter, epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('-draw', dest='draw', action='store_true', help='Draws the graph')
    parser.add_argument('-save', dest='save', type=str, default="", help='ROOT file name to save the graph')
    parser.add_argument('-bin', dest='bin', type=str, default="1", help='bin of the axis to use as the figure of merit. Comma-separated list of bins is allowed, then the result will be the sum over all bins')
    parser.add_argument('-tally', dest='tally', type=str, help='Comma- or dash- separated list of tallies. If separated by comma, the specified tallies will be used; if separated by dash, the range with increment=10 will be used (i.e. f5-f35 is equivalent to f5,f15,f25,f35')
    parser.add_argument('mctal', type=str, help='mctal.root file name')
    parser.add_argument('inp', type=str, help='MCNP(X) input file name')
    args = parser.parse_args()

    tallies = []
    if re.search("-", args.tally):
        tt = args.tally.split('-')
        n1 = int(tt[0][1:])
        n2 = int(tt[1][1:])
        for i in range(n1, n2+10, 10):
            tallies.append("f%d" % i)
    else:
        tallies = args.tally.split(',')

    bins = args.bin.split(',')
#    print "Tallies:", tallies

    nt = len(tallies)
    ge = ROOT.TGraphErrors(nt)
    ge.SetMarkerStyle(ROOT.kFullCircle)
    for i,f in enumerate(tallies):
        y,ey = getFOM(args.mctal, f, bins)
        x = getTheta(f, args.inp)
        ge.SetPoint(i, x, y)
        ge.SetPointError(i, 0, ey)

    ge.SetNameTitle("ge", ";#theta [deg];Figure-of-merit")

    if args.save != "":
        ge.SaveAs(args.save)
        
    ge.Fit("pol0", "q")
    average = ge.GetFunction("pol0").GetParameter(0)
    err = ge.GetFunction("pol0").GetParError(0)
    print "(", average/1E+13, " +- ", err/1E+13, ") x 1E+13"

    if args.draw:
        ge.Draw("ap")
        ROOT.gPad.SetGrid()
        input()


    return 0

    


if __name__=="__main__":
    exit(main())

