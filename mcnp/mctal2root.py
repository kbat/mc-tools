#! /usr/bin/python -W all
#
# $URL$
# $Id$
#

import sys, re, string
from array import array
from ROOT import ROOT, TFile, TH1F, TObjArray, THnSparseF
from mctal import Tally, Axis

def main():
    """
    mctal2root - MCTAL to ROOT converter
    Usage: mctal2root.py mctal [output.root]
    ... many features are not yet supported!

    Homepage: http://code.google.com/p/mc-tools
    """

    # ROOT.PyConfig.IgnoreCommandLineOptions = True # does not work...

#    parser = ap.ArgumentParser(description=main.__doc__, epilog="Homepage: http://code.google.com/p/mc-tools", formatter_class=ap.ArgumentDefaultsHelpFormatter)
#    parser.add_argument('mctal', type=str, help='mctal file name')
#    parser.add_argument('root', type=str, help='output ROOT file name')
#    arguments = parser.parse_args()


    good_tallies = [5] # list of 'good' tally types - to be saved in the ROOT file
    fname_in = sys.argv[1]
    if len(sys.argv) == 3:
        fname_out = sys.argv[2]
    else:
        fname_out = re.sub("\....$", ".root", fname_in)
    if fname_in == fname_out:
        fname_out = fname_in + ".root"
    print fname_out

    file_in = open(fname_in)
    
    verbose = True          # verbosity switch
    kod = None               # name of the code, MCNPX
    ver = None               # code version
    probid = []              # date and time when the problem was run
    probid_date = None       # date from probid
    probid_time = None       # time from probid
    knod = None              # the dump number
    nps = None               # number of histories that were run
    rnr = None               # number of pseudorandom numbers that were used
    problem_title = None     # problem identification line
    ntal = None              # total number of tallies
    ntals = []               # array of tally numbers
    tally = None             # current tally

    is_vals = False          # True in the data/errors section

    histos = TObjArray()     # array of histograms
    f_boundary_number = 0    # index needed to count ordinal numbers in the boundaries of f-axis -> used in case the boundaries are written on several lines

    for line in file_in.readlines():
        if kod is None:
            kod, ver, probid_date, probid_time, knod, nps, rnr = line.split()
            probid.append(probid_date)
            probid.append(probid_time)
            if verbose:
                print ("code:\t\t%s" % kod)
                print ("version:\t%s" % ver)
                print ("date and time:\t%s" % probid)
                print ("dump number:\t%s" % knod)
                print ("number of histories:\t%s" % nps)
                print ("number of pseudorandom numbers used:\t%s" % rnr)
            continue
        else:
            if problem_title is None and line[0] == " ":
                problem_title = line.strip()
                if verbose:
                    print ("title:\t%s" % problem_title)
                continue


        words = line.split()

        if not ntal and words[0] == 'ntal':
            ntal = int(words[1])
#            if verbose: print("number of tallies in the problem: %d" % ntal)
            continue

        if ntal and not tally and words[0] != 'tally':
            for w in words:
                ntals.append(int(w))
            if verbose:
                if ntal>1: print ntal, 'tallies:', ntals
                else: print ntal, 'tally:', ntals

        if words[0] == 'tally':
            if tally: 
                tally.Fix()
                tally.Print()
        # add the latest boundary to the f-axis:  (MUST ALWAYS GO BEFORE tally.Histogram())
#                if tally.axes['f']: tally.axes['f'].boundaries.append(f_boundary_number)

                if tally.number % 10 in good_tallies:
                    histos.Add(tally.Histogram())
#                if tally.number % 10 == 4 or tally.number == 5 or tally.number == 6 or tally.number == 15:
#                    histos.Add(tally.Histogram())
#                elif tally.number == 125:
#                    tally.Print()
#                    histos.Add(tally.Histogram())
                del tally
# temporary
            tally = Tally(int(words[1]))
            tally.particle = int(words[2])
            tally.type = int(words[3])
            if verbose:
                print "tally number %d particle %d of type %d" % (tally.number, tally.particle, tally.type)
            if tally.number not in ntals:
                print 'tally %d is not in ntals' % tally.number
                print ntals
                return 1

            continue

        if not tally: continue

        if tally.axes['f'] and tally.axes['d'] is None and line[0] == ' ':
            for w in words:
                tally.axes['f'].binlabels.append(str(w))
                tally.axes['f'].boundaries.append(f_boundary_number) # in case of 'f'-axis the values written in mctal are not boundaries but just cell names => form the array of boundaries with ordinal numbers
                f_boundary_number += 1
#            tally.axes['f'].boundaries.append(f_boundary_number)

        if tally.axes['f'] is None and words[0] not in ['1', 'f']:
            tally.title = line.strip()
            print "tally.title:", tally.title
            return 0

            
        if tally.axes['t'] and is_vals == False and len(tally.data) == 0 and line[0] == ' ':
            for w in words: tally.axes['t'].boundaries.append(float(w))

        if tally.axes['e'] and tally.axes['t']is None and line[0] == ' ':
            for w in words: tally.axes['e'].boundaries.append(float(w))

        if tally.axes['u'] and tally.axes['s']is None and line[0] == ' ':
            for w in words: tally.axes['u'].boundaries.append(float(w))

        if   not tally.axes['f'] and re.search('^f', line[0]):        tally.axes['f'] = Axis(words[0], int(words[1]))
        elif not tally.axes['d'] and re.search('^d', line[0]):        tally.axes['d'] = Axis(words[0], int(words[1]))
        elif not tally.axes['u'] and re.search ("u[tc]?", line[0:1]): tally.axes['u'] = Axis(words[0], int(words[1]))
        elif not tally.axes['s'] and re.search('^s[tc]?', line[0:1]): tally.axes['s'] = Axis(words[0], int(words[1]))
        elif not tally.axes['m'] and re.search('^m[tc]?', line[0:1]): tally.axes['m'] = Axis(words[0], int(words[1]))
        elif not tally.axes['c'] and re.search('^c[tc]?', line[0:1]): tally.axes['c'] = Axis(words[0], int(words[1]))
        elif not tally.axes['e'] and re.search("^e[tc]?",  line[0:1]):tally.axes['e'] = Axis(words[0], int(words[1]))
        elif not tally.axes['t'] and re.search("^t[tc]?", line[0:1]): tally.axes['t'] = Axis(words[0], int(words[1]))
        elif line[0:2] == 'tfc':
            tally.tfc_n = words[1]
            tally.tfc_jtf = words[2:]

        if tally.tfc_n and line[0] == ' ':
            tally.tfc_data = words

        if words[0] == 'vals':
            is_vals = True
            continue

        if is_vals:
            if line[0] == ' ':
                for iw, w in enumerate(words):
                    if not iw % 2: tally.data.append(float(w))
                    else: tally.errors.append(float(w))
            else:
                is_vals = False

    tally.Print()
    
#    if tally.number == 15:
#        print "histogramming tally", tally.name

# add the latest boundary to the f-axis: (MUST ALWAYS GO BEFORE tally.Histogram())
#    if tally.axes['f']:  tally.axes['f'].boundaries.append(f_boundary_number)
    if tally.number % 10 in good_tallies:
        histos.Add(tally.Histogram())

    histos.Print()

    file_in.close()

    fout = TFile(fname_out, 'recreate')
    histos.Write()
    fout.Close()


if __name__ == '__main__':
    sys.exit(main())
