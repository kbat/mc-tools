#! /bin/bash
#
# removes weight records from a CombLayer-generated input file

sed -i -e "/WEIGHT CARDS/,/END/{/.*/d}" $1
