#! /usr/bin/python -W all
# $Id$

import re, sys, string
from os import system, unlink

def main():
    """
    rotate3dshow - a script to rotate [t-3dshow] output.

Usage: rotate3dshow (e-the|e-phi|l-the|l-phi|w-ang) nsteps file.phits [output.gif]

    e-the, e-phi, l-the, l-phi or w-ang - the parameter to rotate.
    nsteps - number of images per full revolution (360 deg) of selected parameter.

    The PHITS input file must contain a [t-3dshow] section with description of the 1st shot of the animation.
    The script does nothing than generating 'nsteps' input files and running PHITS with each of them
    in order to make a full revolution of the selected parameter.
    
    As it is stated in the PHITS manual, e-the and e-phi rotate the view point angle,
    while l-the and l-phi correspond to the light source angle, and w-ang being the angle of frame.
    
    Individual .gif files produced by the program can be viewed with any image viewer.
    For instance: qiv -m -s -d 0.3 /tmp/rotate3dshow
    
    If the file 'output.gif' is specified and a program 'gifsicle' is installed in your system 
    then all the output files will be merged in a single 'output.gif'

    NOTE
    The parameter 'file' in the [t-3dshow] section should be called '3dshow.dat' and epsout should be enabled:
       file = 3dshow.dat
       epsout = 1


    DEPENDENCIES

    REQUIRED DEPENDENCIES
    python      - of course!
    ImageMagick - a standard Linux package to work with bitmap images [http://www.imagemagick.org].
                  This script uses the ImageMagick tool 'convert' to convert the EPS files produced by PHTIS to GIF.

    OPTIONAL DEPENDENCIES
    gifsicle    - a tool used to produced an animated gif out of the bunch of files produced by PHITS [http://www.lcdf.org/gifsicle].

    EXAMPLE
    Below is an example of a 3dshow tally to be used with rotate3dshow:
[t-3dshow]
  output = 3
      x0 =   0
      y0 =   0
      z0 =   100
    e-the = 178.0
   e-phi =  20
   e-dst =  200
   l-the =  20
   l-phi =   0
   l-dst = 100
   w-wdt =  350
   w-hgt =  350
   w-dst =  100
   w-mnw = 100
   w-mnh = 100
   w-ang = 30
  heaven = z
    file = 3dshow.dat
  epsout = 1
    """

    allowed_parameters = ('e-the', 'e-phi', 'l-the', 'l-phi', 'w-ang')

    if len(sys.argv) == 1:
        print main.__doc__
        return 1
    elif len(sys.argv) != 4 and len(sys.argv) != 5:
        print 'ERROR: wrong usage.'
        print main.__doc__
        return 1

    if sys.argv[1] not in allowed_parameters:
        print 'ERROR: Wrong parameter: ', sys.argv[1]
        print '       Allowed are', allowed_parameters
        return 2

    parameter = sys.argv[1] # parameter to rotate

    try:
        nsteps = int(sys.argv[2])
    except ValueError:
        print 'ERROR: Parameter "%s" must be an integer.' % sys.argv[2]
        return 3

    fname_in = sys.argv[3] # phits input file
    fname_out = None
    if len(sys.argv) == 5: fname_out = sys.argv[4]
    fname_tmp = "/tmp/panimate.phits"
    epsname = "3dshow.eps" # name of the eps file - parameter 'file' in the [t-3dshow] section must be 3dshow.dat

    file_in = open(fname_in)
    input_data = file_in.readlines()
    file_in.close()
    
    output_data = []

    angle0 = 0 # the value of the parameter set in the input file. we will start rotation from this position
    angleStep = 360/nsteps # [deg]
#    print "number of steps:", nsteps
    isFirst = True

    system('rm -fr /tmp/rotate3dshow')
    system('mkdir /tmp/rotate3dshow')

    for istep in range(nsteps):
        del output_data[:]
        for i, line in enumerate(input_data):
            words = line.split()
            if len(words)>=3:
                if words[0] == 'icntl':
                    words[2] = str(11) # 3dshow
                    line = string.join(words) + '\n'

                if isFirst:                                     # get the value of initial angle
                    if words[0] == parameter:
                        print "angle:", words[2]
                        angle0 = float(words[2])
                        isFirst = False
                else:                                           # rotate
                    if words[0] == parameter:
                        angle = angle0+istep*angleStep
                        words[2] = str(angle)
                        line = string.join(words) + '\n'
                        print "angle:", angle
                
            output_data.append(line)

        tmp_file = open(fname_tmp, 'w+')
        for line in output_data:
            tmp_file.write(line)
        tmp_file.close()
        system("phits < %s" % fname_tmp)
        system("grep -iH error $(ls -1rt |tail -1)") # check the output file for the errors
        system("convert -transparent-color white -background white -rotate 90 %s /tmp/rotate3dshow/%.3d.gif" % (epsname, istep))

    print 'The output files are in /tmp/rotate3dshow'

    if fname_out:
        if fname_out[-4:] == '.gif':
            print 'generating gif file', fname_out
            system('which gifsicle >/dev/null && gifsicle --loopcount=forever --disposal 2 /tmp/rotate3dshow/*.gif > %s' % fname_out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
