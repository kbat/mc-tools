#! /usr/bin/env bash

if [ $# != 9 ]; then
    >&2 echo "getmesh - prints mesh definition in the CombLayer format"
    >&2 echo "          Vec3D(xmin,ymin,zmin) Vec3D(xmax,ymax,zmax) nx ny dz"
    >&2 echo ""
    >&2 echo "Usage: getmesh  xmin ymin zmin  xmax ymax zmax  dx dy dz"
    >&2 echo "       [xyz]min, [xyz]max  min/max coordinates of the mesh"
    >&2 echo "       d[xyz]              bin widths along each direction"
    exit 1
fi

xmin=$1
ymin=$2
zmin=$3

xmax=$4
ymax=$5
zmax=$6

dx=$7
dy=$8
dz=$9

for a in x y z; do
    width="d$a"
    if [ ${!width} -le 0 ]; then
	echo "Error: wrong value of d$a: ${!width}."
	exit 2
    fi
done

nx=$(echo "($xmax - $xmin)/$dx"|bc)
ny=$(echo "($ymax - $ymin)/$dy"|bc)
nz=$(echo "($zmax - $zmin)/$dz"|bc)

for a in x y z; do
    nbins="n$a";
    if [ ${!nbins} -le 0 ]; then
	>&2 echo "Error: wrong value of n$a: ${!nbins}. Check ${a}min, ${a}max and d${a}."
	exit 3
    fi
done

echo "Vec3D($xmin,$ymin,$zmin) Vec3D($xmax,$ymax,$zmax) $nx $ny $nz"
