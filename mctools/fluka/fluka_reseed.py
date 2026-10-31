#!/usr/bin/env python3

import sys, re, os
import argparse

DEFAULT_SEED = 54217137 # FLUKA default for WHAT(2) of RANDOMIZ
MAX_SEED = 900000000    # WHAT(2) must be < 9.E8
SEPARATOR = re.compile(r"(\s*[,;%\\:]\s*|\s+)") # free-format separators

def keyword(l):
    """ Return the upper-case 8-character card keyword of the line l """
    w = l.split(None, 1)
    return w[0][:8].upper() if w else ""

def is_free(l):
    """ Return True if the GLOBAL card l requests free-format input """
    try:
        what4 = float(l[40:50]) if l[40:50].strip() else 0.0
    except ValueError: # GLOBAL itself written in free format
        tokens = SEPARATOR.split(l.strip())[::2]
        what4 = float(tokens[4] or 0.0) if len(tokens) > 4 else 0.0
    return what4 in (2.0, 3.0)

def find_randomiz(lines):
    """ Return the index of the RANDOMIZ card and whether it is in free format """
    free = False
    geo = False
    found = []
    for i, l in enumerate(lines):
        if l.startswith(("*", "!")) or not l.strip():
            continue
        card = keyword(l)
        if card == "GEOBEGIN":
            geo = True
        elif card == "GEOEND":
            geo = False
        elif geo:
            continue
        elif card == "GLOBAL":
            free = is_free(l)
        elif card == "FREE":
            free = True
        elif card == "FIXED":
            free = False
        elif card == "RANDOMIZ":
            found.append((i, free))
    return found

def fmt(seed, width):
    """ Format seed as a real number fitting in width characters,
    leaving a blank before it if possible """
    s = f"{seed}.0"
    return s if len(s) < width else f"{seed}."

def get_seed(l, free):
    """ Return the WHAT(2) seed of the RANDOMIZ card l """
    if free:
        tokens = SEPARATOR.split(l.split("!")[0].strip())[::2]
        val = tokens[2] if len(tokens) > 2 else ""
    else:
        val = l[20:30]
    seed = int(float(val)) if val.strip() else 0
    return seed if seed > 0 else DEFAULT_SEED

def set_seed(l, seed, free):
    """ Return the RANDOMIZ card l with WHAT(2) replaced by seed """
    eol = l[len(l.rstrip("\r\n")):]
    l = l.rstrip("\r\n")
    if free:
        body, sep, comment = l.partition("!")
        lead = body[:len(body)-len(body.lstrip())]
        trail = body[len(body.rstrip()):]
        parts = SEPARATOR.split(body.strip())
        if len(parts) < 3:
            parts += [" ", "1.0"]
        if len(parts) < 5:
            parts += [" ", ""]
        parts[4] = fmt(seed, 99)
        return lead + "".join(parts) + trail + sep + comment + eol
    return f"{l[:20]:20}{fmt(seed, 10):>10}{l[30:]}".rstrip() + eol

def main():
    """ Generate copies of a FLUKA input file which differ only in the
    initial random number seed (WHAT(2) of the RANDOMIZ card). The seeds
    start from that of the original file incremented by 1, and every
    next file gets the seed of the previous one incremented by 1.
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('inp', type=str, help='FLUKA input file name')
    parser.add_argument('n', type=int, help='number of input files to generate')
    parser.add_argument('-f', '--force', action='store_true', default=False, help='overwrite existing output files')

    args = parser.parse_args()

    if args.n < 1:
        parser.error(f"number of files must be >= 1, got {args.n}")

    with open(args.inp, newline='') as f:
        lines = f.readlines()

    found = find_randomiz(lines)
    if len(found) != 1:
        parser.error(f"{args.inp}: expected exactly one RANDOMIZ card, found {len(found)}")
    i, free = found[0]

    seed0 = get_seed(lines[i], free)
    if seed0 + args.n >= MAX_SEED:
        parser.error(f"seed {seed0 + args.n} exceeds the FLUKA limit of {MAX_SEED}")

    outdir = os.path.dirname(args.inp)
    stem = os.path.splitext(os.path.basename(args.inp))[0]
    outputs = [(os.path.join(outdir, f"{stem}-{seed0+j}.inp"), seed0+j)
               for j in range(1, args.n+1)]

    if not args.force:
        exist = [out for out, _ in outputs if os.path.exists(out)]
        if exist:
            parser.error(f"file(s) already exist, use -f to overwrite: {' '.join(exist)}")

    for out, seed in outputs:
        new = lines.copy()
        new[i] = set_seed(lines[i], seed, free)
        with open(out, 'w', newline='') as f:
            f.writelines(new)
        print(out)

if __name__ == "__main__":
    sys.exit(main())
