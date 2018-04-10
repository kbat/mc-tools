#! /usr/bin/python -W all




import sys, re
import argparse

def main():
    """
    This script should be used with mcnpview.sh.
    It creates the COMOUT file based on the command file produced by mcnpview.
    """

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('com', type=str, help='plot requests file name', nargs='?', default="/tmp/foo.c")
    parser.add_argument('comout', type=str, help='COMOUT file name', nargs='?', default="zoom")

    args = parser.parse_args()

    cmd = {} # dictionary of commands

    bas = False
    plane = False
    
    with open(args.com) as f:
        for line in f.readlines():
            words = line.strip().split()
            if len(words) is 0:
                continue

            for i,w in enumerate(words):
                if re.search("^bas", w):
                    cmd['bas'] = map(float, words[i+1:i+7])
                    if plane is False: bas = True # basis was before plane cuts
                elif re.search("^or", w):
                    cmd['or'] = map(float, words[i+1:i+4])
                elif re.search("^ex", w):
                    try: # both x and y scales are given
                        cmd['ex'] = map(float, words[i+1:i+3])
                        continue
                    except ValueError: # just 1 scale is given
                        cmd['ex'] = map(float, words[i+1:i+2])
                elif re.search("^lab", w):
                    cmd['label'] = map(int, map(float, words[i+1:i+3])) #+ [words[i+3]]
                elif re.search("^p[xyz]", w):
                    cmd[w] = [float(words[i+1])]
                    if bas is False: plane = True # plane cuts were before basis
                elif re.search("^legend", w):
                    cmd[w] = [words[i+1]]
                elif w == "scale":
                    print w
                    if int(words[i+1]): # no need to put 'scale 0'
                        cmd[w] = [words[i+1]]
                elif w in ("mesh"):
                    if int(words[i+1])==1: # no need to put 'mesh 1'
                        cmd[w] = [words[i+1]]

    print bas, plane

    if plane: # bas was first
        keys = ('bas', 'or', 'ex', 'px', 'py', 'pz', 'label', 'mesh', 'legend', 'scale')
    elif bas:
        keys = ('or', 'ex', 'px', 'py', 'pz', 'bas', 'label', 'mesh', 'legend', 'scale')
    else:
        keys = {'or', 'ex', 'label', 'mesh', 'legend', 'scale'}
        
    with open(args.comout, 'w') as f:
        for key in keys:
            if key in cmd:
                # newline required by mcplot:
                if key in ('mesh', 'legend', 'scale', 'label'):
                    f.write("\n")
                f.write("%s %s " % (key," ".join(str(e) for e in cmd[key]),))
        f.write("\n")



if __name__ == "__main__":
    sys.exit(main())

# grep label /tmp/foo.c | tail -1 > zoom
# grep basis /tmp/foo.c | tail -1 >> zoom
# grep orig /tmp/foo.c | tail -1 >> zoom
# grep ^px /tmp/foo.c | tail -1 >> zoom
# grep ^py /tmp/foo.c | tail -1 >> zoom
# grep ^pz /tmp/foo.c | tail -1 >> zoom
# grep ^scal /tmp/foo.c | tail -1 >> zoom
# grep ^ex /tmp/foo.c | tail -1 >> zoom
# grep ^mesh /tmp/foo.c | tail -1 >> zoom
