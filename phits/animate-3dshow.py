#! /usr/bin/python -W all

import re, sys, string
from os import system, unlink

def getOut(fname_in):
    """
    Return the output file name based on the input file name
    """
    fname_out = re.sub("\.....?.?", ".avi", fname_in)
    if fname_out == fname_in:
        fname_out = fname_in + ".avi"
    return fname_out

def main():
    """
    animate-3dshow (theta|phi) nsteps file.phits
    """

    if len(sys.argv) != 4:
        print "wrong usage", len(sys.argv)
        return 1

    if sys.argv[1] == 'phi':
        rotatePhi = True
    elif sys.argv[1] == 'theta':
        rotatePhi = False
    else:
        print 'theta or phi?'
        print "usage"
        return 2

    nsteps = int(sys.argv[2])

    fname_in = sys.argv[3] # phits input file
    fname_out = getOut(fname_in)
    fname_tmp = "panimate.phits"
    epsname = "3dshow.eps" # name of the eps file - parameter 'file' in the [t-3dshow] section must be 3dshow.dat

    print fname_in, fname_out

    file_in = open(fname_in)
    input_data = file_in.readlines()
    file_in.close()
    
    output_data = []

    angle0 = 0 # the value of e-the or e-phi set in the input file. we will start rotation from this position
    angleStep = 360/nsteps # [deg]
    print "number of steps:", nsteps
    isFirst = True

    system('rm -fr /tmp/animate-3dshow')
    system('mkdir /tmp/animate-3dshow')

    for istep in range(nsteps):
#        print "step #", istep
        del output_data[:]
        for i, line in enumerate(input_data):
            words = line.split()
            if len(words)>=3:
                if words[0] == 'icntl':
                    words[2] = str(11) # 3dshow
                    line = string.join(words) + '\n'

                if isFirst: # get the value of initial angle
                    if rotatePhi and words[0] == 'e-phi':
                        angle0 = int(words[2])
                        isFirst = False
                    elif not rotatePhi and words[0] == 'e-the':
                        angle0 = int(words[2])
                        isFirst = False
                else:
                    if rotatePhi and words[0] == 'e-phi':
                        angle = angle0+istep*angleStep
                        words[2] = str(angle)
                        line = string.join(words) + '\n'
                        print "phi:", angle
                    elif not rotatePhi and words[0] == 'e-the':
                        angle = angle0+istep*angleStep
                        words[2] = str(angle)
                        line = string.join(words) + '\n'
                        print "theta:", angle
                
            output_data.append(line)

        tmp_file = open(fname_tmp, 'w+')
        for line in output_data:
            tmp_file.write(line)
        tmp_file.close()
        system("phits < %s" % fname_tmp)
        system("convert -transparent-color white -background white -rotate 90 %s /tmp/animate-3dshow/%.3d.png" % (epsname, istep))

#    system('mencoder')


    return 0


if __name__ == "__main__":
    sys.exit(main())
