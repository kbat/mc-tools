#! /bin/bash
# Sets the FM card to the inverse value of the solid angle of the corresponding collimator

# in order to get rid of the problem .[?1034h
TERM=vt100

calc() { python -c "print $1"; }

inp=$1

if [ $# = 1 ]; then
    tallies=$(egrep '^f.*5:' $inp | sed "s/:.*//g" | sed "s/^f//")
    for t in $tallies; do
	setomega $inp F$t $t
    done
    exit 0
fi

if [ $# != 3 ]; then
    echo "Usage: setomega inp [tallyName tallyNumber]"
    echo "       If tallyName and tallyNumber are missed then loops through"
    echo "       all point detector tallies in inp and tries to set solid angle by executing"
    echo "       setomega F5 5"
    echo "       setomega F15 15"
    echo "       etc"
    exit 1
fi

tally=$2
n=$3
current=15603774361278814.0 # protons/sec at 2 mA


if [ ! -f $inp ]; then
    echo "File $inp does not exist"
    exit 2
fi

omega=$(getomega -inv $inp $tally)
# echo $omega
# echo $current
#omega=$(echo $omega*$current | bc)
omega=$(calc $omega*$current)

sed -i -e "s/\(^f$n:.*\)/\1\nfm$n $omega/" $inp
