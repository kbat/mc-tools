#!/usr/bin/env bash

tmpfile=$(mktemp /tmp/compare.XXX)

rm -fv exe[01]_z*.root hist_diff_z*.root *.log *.vtk

cldiff=$MCTOOLS/mctools/common/CombLayer/diff/cl-diff.py

$cldiff ~/misc/soft/comblayer/TDC/maxiv \
	~/misc/soft/comblayer/TDC-merge-master/maxiv \
	"-defaultConfig Linac All" \
	-xrange  -1507 138 -nx 1645 \
	-yrange  9390 10075  -ny 685 \
	-zrange  -585 640  -nz 1225 \
	> $tmpfile


# first round (folder: 1)
#	-zrange  -130 100  -nz 230 \

# second round (folder: 2)
#	-zrange  -9 2.5  -nz 12 \

# third round (folder: 3): all OK
#	-xrange  -828 455 -nx 1283 \
#	-yrange  445 10297  -ny 9842 \
#	-zrange  -2.5 -1.85  -nz 8 \



#	-zrange  -130 260  -nz 390 \

#parallel --bar  --halt now,fail=1 < $tmpfile > cl-diff.log
# parallel can be resumed with --joblog: https://www.gnu.org/software/parallel/parallel_tutorial.html
parallel --bar --joblog /tmp/log < $tmpfile > cl-diff.log

#	"-offset object SoftiMAXFrontBeamUPipe 0 -defaultConfig Single SOFTIMAX" \
# -zrange -592 627 -nz  1219

	# -xrange  -2486 1681 -nx 4167 \
	# -yrange  0 13210  -ny 13210 \
	# -zrange  -609 647  -nz 1256 \
