#!/usr/bin/env bash

tmpfile=$(mktemp /tmp/compare.XXX)

rm -fv exe[01]_z*.root exe[01]_z*.root *.log

./cl-diff.py /home/kbat/misc/soft/comblayer/master/maxiv \
	     /home/kbat/misc/soft/comblayer/TDC/maxiv \
	     "-defaultConfig Linac All" \
	     -xrange -2000.1 750.2  -nx 2750 \
	     -yrange 0 13400.13    -ny 13400 \
	     -zrange -50.1 50.23 -nz 100 \
	     > $tmpfile

#parallel --halt now,fail=1 < $tmpfile > cl-diff.log
parallel < $tmpfile > cl-diff.log

head cl-diff.log

#rm -f $tmpfile

#	     -xrange -2000 750 -yrange 0 13400 -zrange -1 1 \

#	     -zrange -50.01 50.007 -zstep 1 \


# OK 1 cm
# -xrange -2000 750  -nx 2750 \
    # -yrange 0 13400    -ny 13400 \
    # -zrange -50.1 50.2 -nz 100 \


# OK walls
	     # -xrange -2622.04 1787.56  -nx 440 \
	     # -yrange -99.3 13345.69   -ny 1340 \
	     # -zrange -679.67 722.6 -nz 20 \
