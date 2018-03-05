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

    with open(args.com) as f:
        for line in f.readlines():
            words = line.strip().split()
            if len(words) is 0:
                continue

            for i,w in enumerate(words):
                if re.search("^bas", w):
                    cmd['bas'] = map(float, words[i+1:i+7])
                elif re.search("^or", w):
                    cmd['or'] = map(float, words[i+1:i+4])
                elif re.search("^ex", w):
                    try: # both x and y scales are given
                        cmd['ex'] = map(float, words[i+1:i+3])
                        break
                    except ValueError: # just 1 scale is given
                        cmd['ex'] = map(float, words[i+1:i+2])
                elif re.search("^lab", w):
                    cmd['label'] = map(int, map(float, words[i+1:i+3])) + [words[i+3]]
                elif re.search("^p[xyz]", w):
                    cmd[w] = [float(words[i+1])]

#    print cmd
    with open(args.comout, 'w') as f:
        for key,value in cmd.iteritems():
            f.write("%s %s " % (key," ".join(str(e) for e in value),))
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
