# /bin/bash
# This script has to be used with mcnpview.sh
# It creates the zoom file based on the command file produced by mcnpview
# https://github.com/kbat/mc-tools
#

grep label /tmp/foo.c | tail -1 > zoom
grep basis /tmp/foo.c | tail -1 >> zoom
grep orig /tmp/foo.c | tail -1 >> zoom
grep ^px /tmp/foo.c | tail -1 >> zoom
grep ^py /tmp/foo.c | tail -1 >> zoom
grep ^pz /tmp/foo.c | tail -1 >> zoom
grep ^scal /tmp/foo.c | tail -1 >> zoom
grep ^ex /tmp/foo.c | tail -1 >> zoom
grep ^mesh /tmp/foo.c | tail -1 >> zoom
