#! /usr/bin/python -W all
# $Id: rotate3dshow.py 100 2012-06-27 10:19:30Z batkov $
# $URL$

import re, sys, string, argparse, shutil, os

def main():
    """
    rotate3dshow - a script to rotate [t-3dshow] output.

    USAGE
    rotate3dshow (e-the|e-phi|l-the|l-phi|w-ang) nimages file.phits [output.gif]

    e-the, e-phi, l-the, l-phi or w-ang - the parameter to rotate.
    nimages - number of images per full revolution (360 deg) of selected parameter.
    file.phits - PHITS input file (see an example of the [t-3dshow] tally setup below).
    output.gif - optional parameter - the name of the animated GIF file.
                 If not specified, the 'nimages' GIF files will be generated in /tmp/rotate3dshow

    The PHITS input file must contain a [t-3dshow] section with description of the 1st shot of the animation.
    The script does nothing than generating 'nimages' input files and running PHITS with each of them
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
    Python and PHITS - of course!
    ImageMagick - a standard Linux package to work with bitmap images [http://www.imagemagick.org].
                  This script uses the ImageMagick tool 'convert' to convert the EPS files produced by PHTIS to GIF.

    OPTIONAL DEPENDENCIES
    gifsicle    - a tool used to produced an animated gif out of the bunch of files produced by PHITS [http://www.lcdf.org/gifsicle].

    EXAMPLE
    Below is an example of a [t-3dshow] tally to be used with rotate3dshow:
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

    Produce an animation of e-phi rotation with 10 frames based on the PHITS input file 'inp' and save it in a GIF file '3dshow.gif':
        rotate3dshow e-phi 10 inp 3dshow.gif
    """

    allowed_parameters = ('e-the', 'e-phi', 'l-the', 'l-phi', 'w-ang')

    phits_default = 'phits'
    convert_default = 'convert'
    if os.name == 'nt': 
        phits_default = 'c:/phits/bin/phits_c.exe' # !!! should use just phits.exe here and set correct PATH
        convert_default = 'convert.exe'

    parser = argparse.ArgumentParser(description="main.__doc__", epilog='Homepage: http://code.google.com/p/mc-tools', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('parameter', type=str, help='Parameter to rotate', choices=allowed_parameters) #, metavar='(e-the|e-phi)')
    parser.add_argument('nimages', type=int, default='10', help='Number of images per full revolution (360 deg) of selected parameter')
    parser.add_argument('input', type=argparse.FileType('rt'), help='PHITS input file')
    parser.add_argument('-o', type=str, dest='outname', help='If specified, the produced images will be merged in the animated GIF file with this name.', required=False)
    parser.add_argument('-copt', type=str, dest='copt', help='Options passed to the convert tool used to convert from EPS to GIF. See the "Format conversion" section of the ImageMagick manual: http://www.imagemagick.org', required=False, default='-transparent-color white -background white -rotate 90 -density 100x100')
    parser.add_argument('-aopt', type=str, dest='aopt', help='Options passed to the convert tool used to produce the animated GIF file. See the "Format conversion" section of the ImageMagick manual for details: http://www.imagemagick.org', required=False, default='-delay 5 -dispose background')
    parser.add_argument('-epsname', type=str, dest='epsname', help='Name of the EPS file produced by the [t-3dshow] tally', required=False, default='3dshow.eps')
    parser.add_argument('-phits', type=str, dest='phits', help='PHITS executable', required=False, default=phits_default)
    parser.add_argument('-convert', type=str, dest='convert', help='ImageMagic\'s convert executable', required=False, default=convert_default)
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbosity', help='Explain what is being done')

    arguments = parser.parse_args()
    tmpdir = 'rotate3d-gifs' # should not be allowed as an argument since this folder is being purged by the script (a user can set an existing folder here)
    tmpinp = os.path.join(tmpdir, 'panimate.phits')

    input_data = arguments.input.readlines()# open(fname_in).readlines()
    
    output_data = []

    angle0 = 0
    angle = 0
    angleStep = 360/arguments.nimages # [deg]
    isFirst = True

    # remove .gif files from tmpdir
    if not os.path.exists(tmpdir): 
        os.mkdir(tmpdir, 0700)
    else:
        for the_file in os.listdir(tmpdir):
            file_path = os.path.join(tmpdir, the_file)
            try:
                if os.path.isfile(file_path) and file_path[-4:] == '.gif':
                    os.unlink(file_path)
            except Exception, e:
                print e



    for istep in range(arguments.nimages):
        del output_data[:]
        for i, line in enumerate(input_data):
            words = line.split()
            if len(words)>=3:
                if words[0] == 'icntl':
                    words[2] = str(11) # 3dshow
                    line = string.join(words) + '\n'

                if isFirst:                                     # get the value of initial angle
                    if words[0] == arguments.parameter:
#                        print words[2], 'deg'
                        angle = float(words[2])
                        angle0 = angle  # the value of the parameter set in the input file. we will start rotation from this position
                        isFirst = False
                else:                                           # rotate
                    if words[0] == arguments.parameter:
                        angle = angle0+istep*angleStep
                        words[2] = str(angle)
                        line = string.join(words) + '\n'
#                        print angle, 'deg'
                
            output_data.append(line)

        tmp_file = open(tmpinp, 'w+')
        for line in output_data:
            tmp_file.write(line)
        tmp_file.close()
        command = "%s < %s" % (arguments.phits, tmpinp)
        if arguments.verbosity: print "Producing the image at %.0f deg:\t%s" % (angle, command)
        os.system(command)
#        os.system("grep -iH error $(ls -1rt |tail -1)") # check the output file for the errors
        command = "%s %s %s %s" % (arguments.convert, arguments.copt, arguments.epsname, os.path.join(tmpdir, "%.3d.gif" % istep))
        if arguments.verbosity: print command
        os.system(command)

    if arguments.verbosity: print 'The output files are in %s' % tmpdir

    if arguments.outname:
        if arguments.outname[-4:] == '.gif':
            command = 'convert %s %s/*.gif %s' % (arguments.aopt, tmpdir, arguments.outname)
            if arguments.verbosity:
                print "Generating the gif-animation file '%s': %s" % (arguments.outname, command)
            os.system(command)

            #os.system('which gifsicle >/dev/null && gifsicle --loopcount=forever --disposal 2 /tmp/rotate3dshow/*.gif > %s' % arguments.outname)

    return 0


if __name__ == "__main__":
    sys.exit(main())
