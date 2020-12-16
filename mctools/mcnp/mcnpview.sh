#! /bin/bash
# mcnpview - a wrapper around "mcnp6 ip"
# This script has to be used with mc-tools/bin/zoom
# It allows to plot geometry with the same view
# as it was done during one of the previous calls of mcnpview.
# This is convenient for building geometry.
# Example:
# 1. Plot a geometry for the fist time:
#    mcnpview inp
#    Play with geometry: set a specific orientation, colour by material or temperature etc.
# 2. Save the view:
#    zoom
# 3. Plot the same view again:
#    mcnpview inp zoom
# 4. ... and even add any MCNP plot commands:
#    mcnpview inp zoom orig 100 200 300 bas 0 1 0 -1 0 0
#
# https://github.com/kbat/mc-tools

prog=$(basename $0)

if [ $# -eq 0 ]; then
    echo "Usage: $prog inp [zoom] [MCNP plot requests]"
    exit 1
fi

# 'mcnpview' calls 'mcnp6', wile 'mcnpxview' calls 'mcnpx':
mcnp=$(echo $(basename $0) | sed -e "s/pview/p6/" -e "s/view//")

if ! command -v $mcnp &> /dev/null ; then
    echo "${prog}: $mcnp executable does not exist"
    exit 1
fi

i=inp
test -z $1 || i=$1

if [ ! -f $i ]; then
    echo $prog": can't open MCNP input file " $i
    exit 1
fi

if [ -e ~/.xbindkeysrc-$mcnp ]; then
    ln -sf ~/.xbindkeysrc-$mcnp ~/.xbindkeysrc
    killall xbindkeys; xbindkeys
fi

tmpdir=`mktemp -d`

com=""
test -z $2 || com=$2

/bin/cp -f $i $tmpdir
i=$tmpdir/$(basename $i)
sed -i -e "s/[mM][tT]/c mt/g" $i

if [ ! -z $com -a -f $com ]; then
    cp -f $com $tmpdir
    com=$tmpdir/$(basename $com)
    echo $com
    # execute commands after $com in MCNP plot:
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

if command -v ps2pdf &> /dev/null; then
    f=$(ls -1rt|tail -1)
    if [[ $f =~ \.ps$  ]]; then ps2pdf $f && rm -f $f; fi
else
    echo $prog": install ps2pdf to automatically convert saved PostScript files into PDF format"
fi
