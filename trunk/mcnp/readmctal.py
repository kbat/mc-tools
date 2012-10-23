#! /usr/bin/python -W all
#
# $URL$
# $Id$
#

import sys, re, string
from array import array
from mctal import Header, Tally, Axis
from mcnp import GetParticleNames
    

def main():
    """
    readmctal - an example how to read the mctal file
    Usage: readmctal mctal
    ... many features are not yet supported!

    Homepage: http://code.google.com/p/mc-tools
    """

    good_tallies = [4] # list of 'good' tally types
    fname_in = sys.argv[1]

    verbose = True           # verbosity switch
    probid_date = None       # date from probid
    probid_time = None       # time from probid

    tally = None             # current tally
    tallies = []             # list of tallies read so far

    is_vals = False          # True in the data/errors section
#    is_bin_labels = False    # True in the line after the "^tally" line
    is_list_of_particles = False # True if the line with the list of particles follows the ^tally line

    h = Header()

    file_in = open(fname_in)
    
    for line in file_in.readlines():
        if h.kod == 0:
            h.kod, h.ver, probid_date, probid_time, h.knod, h.nps, h.rnr = line.split()
            h.probid.append(probid_date)
            h.probid.append(probid_time)
            continue
        else:
            if h.title is None and line[0] == " ":
                h.title = line.strip()
                continue

        words = line.split()

        if not h.ntal and words[0] == 'ntal':
            h.ntal = int(words[1])
            if len(words) == 4 and words[2] == 'npert':
                h.npert = int(words[3])
            continue

        if h.ntal and not tally and words[0] != 'tally':
            for w in words:
                h.ntals.append(int(w))

            if verbose: 
                h.Print()

        if words[0] == 'tally':
            if verbose: print("")
            if tally: 
                if tally.number and tally.number % 10 in good_tallies:
                    tallies.append(tally)
                del tally
# temporary
            tally = Tally(int(words[1]))
            tally.particle = int(words[2])
            if tally.particle < 0: # then tally.particle is number of particle types and the next line lists them
                is_list_of_particles = True
            tally.type = int(words[3])
            if verbose:
                print "tally number %d particle %d of type %d" % (tally.number, tally.particle, tally.type)
            if tally.number not in h.ntals:
                print 'tally %d is not in ntals' % tally.number
                print h.ntals
                return 1
#            is_bin_labels = True
            continue

        if is_list_of_particles:
            tally.particle = map(int, words)
            if verbose:
                print "list of particles: ", GetParticleNames(tally.particle)
            is_list_of_particles = False

        
        if not tally: continue

        if tally.axes['f'] and tally.axes['d'] is None and line[0] == ' ':
            for w in words:
                tally.axes['f'].arraycsn.append(str(w))
#            print "axis", tally.axes['f'].arraycsn

#        if tally.axes['f'] is None and words[0] not in ['1', 'f']:
#            tally.title = line.strip()
#            print "tally.title:", tally.title
#            return 0

        if tally.axes['t'] and is_vals == False and len(tally.data) == 0 and line[0] == ' ':
            for w in words: tally.axes['t'].arraycsn.append(float(w))

        if tally.axes['e'] and tally.axes['t'] is None and line[0] == ' ':
            for w in words: tally.axes['e'].arraycsn.append(float(w))

        if tally.axes['u'] and tally.axes['s']is None and line[0] == ' ':
            for w in words: tally.axes['u'].arraycsn.append(float(w))

        if   not tally.axes['f'] and re.search('^f', line[0]):        tally.axes['f'] = Axis(words[0], map(int, words[1:]))
        elif not tally.axes['d'] and re.search('^d', line[0]):        tally.axes['d'] = Axis(words[0], map(int, words[1:]))
        elif not tally.axes['u'] and re.search ("u[tc]?", line[0:1]): tally.axes['u'] = Axis(words[0], map(int, words[1:]))
        elif not tally.axes['s'] and re.search('^s[tc]?', line[0:1]): tally.axes['s'] = Axis(words[0], map(int, words[1:]))
        elif not tally.axes['m'] and re.search('^m[tc]?', line[0:1]): tally.axes['m'] = Axis(words[0], map(int, words[1:]))
        elif not tally.axes['c'] and re.search('^c[tc]?', line[0:1]): tally.axes['c'] = Axis(words[0], map(int, words[1:]))
        elif not tally.axes['e'] and re.search("^e[tc]?",  line[0:1]):tally.axes['e'] = Axis(words[0], map(int, words[1:]))
        elif not tally.axes['t'] and re.search("^t[tc]?", line[0:1]): tally.axes['t'] = Axis(words[0], map(int, words[1:]))
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

#    print "valsss", tally.data

    tally.Print() #  print only last tally
    
#    if tally.number == 15:
#        print "histogramming tally", tally.name

# add the latest boundary to the f-axis: (MUST ALWAYS GO BEFORE tally.Histogram())
#    if tally.axes['f']:  tally.axes['f'].arraycsn.append(f_boundary_number)
#    if tally.number % 10 in good_tallies:
#        histos.Add(tally.Histogram())

    file_in.close()



if __name__ == '__main__':
    sys.exit(main())
