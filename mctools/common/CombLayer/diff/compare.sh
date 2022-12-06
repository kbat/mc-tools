#!/usr/bin/env bash

tmpfile=$(mktemp /tmp/compare.XXX)

rm -fv exe[01]_z*.root hist_diff_z*.root *.log *.vtk

cldiff=$MCTOOLS/mctools/common/CombLayer/diff/cl-diff.py

$cldiff ~/misc/soft/comblayer/master/maxiv \
	~/misc/soft/comblayer/SoftiMAX-wall/maxiv \
	"-offset object SoftiMAXFrontBeamUPipe 0 -defaultConfig Single SOFTIMAX" \
	-xrange  -250 3415 -nx 3665 \
	-yrange  -460 225  -ny 685 \
	-zrange  -4 4  -nz 7 \
	> $tmpfile


#	-zrange  -130 260  -nz 390 \

#parallel --halt now,fail=1 < $tmpfile > cl-diff.log
parallel < $tmpfile > cl-diff.log
