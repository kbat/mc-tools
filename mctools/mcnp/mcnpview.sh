#! /bin/bash
# mcnpview - a wrapper around "mcnp6 ip"
# This script has to be used with zoom.sh
# It allows to plot geometry with the same view
# as it was done during one of the previous calls of mcnpview.
# This is convenient while debugging geometry.
# Example:
# 1. Plot a geometry fist time:
#    mcnpview inp
#    Play with geometry: set a specific orientation, colour by material or temperature etc.
# 2. Save the view:
#    zoom
# 3. Plot the same view again:
#    mcnpview inp zoom
#
# https://github.com/kbat/mc-tools

mcnp=$(echo $(basename $0) | sed -e "s/pview/p6/" -e "s/view//")

tmpdir=`mktemp -d`

if [ $# -eq 0 ]; then
    echo "Usage: mcnpview inp [zoom] [mcplot command]"
    exit 1
fi

i=inp
test -z $1 || i=$1

com=""
test -z $2 || com=$2

if [ ! -f $i ]; then
    echo "mcnpview: can't open MCNP input file " $i
    exit 1
fi

/bin/cp -f $i $tmpdir
i=$tmpdir/$(basename $i)
sed -i -e "s/[mM][tT]/c mt/g" $i

if [ ! -z $com -a -f $com ]; then
    cp -f $com $tmpdir
    com=$tmpdir/$(basename $com)
    echo $com
    # execute commands after $com in mcplot:
    shift
    shift
    echo $@ >> $com
    $mcnp ip name=$tmpdir/foo. i=$i com=$com
else
    $mcnp ip name=$tmpdir/foo. i=$i
fi

# copy the command file to /tmp, so 'zoom' could find it:
# ($tmpdir is deleted below)
cp -f $tmpdir/foo.c /tmp/foo.c

#echo $tmpdir
rm -fr $tmpdir
# the lines below are called AFTER we exit from mcnp
#	xdotool mousemove 155 635 click 1
# update the plot
#	xdotool mousemove 100 100 click 1

f=$(ls -1rt|tail -1)	  	
if [[ $f =~ \.ps$  ]]; then ps2pdf $f && rm -f $f; fi


