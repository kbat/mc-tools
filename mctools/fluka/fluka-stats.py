#!/usr/bin/env python

import argparse
from sys import exit
from pathlib import Path
import os
from tqdm import tqdm
from math import sqrt, log10, floor
import numpy as np
from uncertainties  import ufloat
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

STAT_PREFIXES = {
    "average": "Average CPU time used to follow a primary particle:",
    "maximum": "Maximum CPU time used to follow a primary particle:",
    "total": "Total CPU time used to follow all primary particles:",
    "nps": "Total number of primaries run",
}

def Print(vals, ttype, nps):
    data = np.array(vals)
    n = len(data)
    scale = n/nps
    val = np.average(data)*scale
    err = np.std(data)/sqrt(n)*scale
#    print("%s: %.5g ± %.1e sec" % (ttype, val, err))
    x = ufloat(val, err)*1000
    print(f"{ttype}: {x} msec")
    return (val, err)

def reversed_lines(fname, block_size=64 * 1024):
    """Yield text lines from the end of a file without loading it all."""
    with open(fname, "rb") as f:
        f.seek(0, os.SEEK_END)
        pos = f.tell()
        buffer = b""

        while pos > 0:
            read_size = min(block_size, pos)
            pos -= read_size
            f.seek(pos)

            lines = (f.read(read_size) + buffer).split(b"\n")
            buffer = lines[0]

            for line in reversed(lines[1:]):
                yield line.rstrip(b"\r").decode("utf-8", errors="replace")

        if buffer:
            yield buffer.rstrip(b"\r").decode("utf-8", errors="replace")

def parse_value(line, ttype):
    w = line.split()
    if ttype == "nps":
        val = w[5]
    else:
        val = w[-3]
    try:
        return float(val)
    except ValueError:
        print(f"Can't convert \"{val}\" to float")
        raise

def get_stats(fname, ttypes=("average", "maximum", "nps")):
    unknown = set(ttypes) - set(STAT_PREFIXES)
    if unknown:
        raise NameError(f"Unknown ttype argument: {unknown.pop()}")

    pending = set(ttypes)
    values = {ttype: None for ttype in ttypes}

    for line in reversed_lines(fname):
        l = line.strip()
        for ttype in tuple(pending):
            if l.startswith(STAT_PREFIXES[ttype]):
                values[ttype] = parse_value(l, ttype)
                pending.remove(ttype)
                break
        if not pending:
            break

    return values

def get(fname, ttype):
    return get_stats(fname, (ttype,))[ttype]

def getFiles(out):
    """ Return list of output files.
    If out is a directory, return result of recursive search  of "*.out" files inside that directory.
    Otherwise just return out.
    """
    if os.path.isdir(out[0]):
        directory = Path(out[0])
        return list(directory.rglob("*.out"))
    else:
        return out

def main():
    """ Print/draw the CPU time statistics based on the FLUKA output files"""

    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('out', type=str, nargs="+", help='List of FLUKA output file(s) or just path to the folder where all *.out files will be recursively analysed')
    parser.add_argument('-o', dest="pdf", type=str, default=None, help='optional output PDF file name where average and maximum histograms will be saved', required=False)
    parser.add_argument('-n', dest="N", type=int, default=10, help='number of histogram bins (make sense with the -o option only)', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='explain what is being done')

    args = parser.parse_args()

    args.out = getFiles(args.out)
    nout = len(args.out)

    if nout == 0:
        print("ERRPR: No output files found")
        exit(1)

    if args.verbose:
        print(nout, " output files found")


    if args.pdf and not args.pdf.endswith(".pdf"):
        print(f"Error: PDF file name is expected: {args.pdf}")
        return 1

    avals = []
    mvals = []
    avals1 = [] #  not normalised by nps (for PDF)
    mvals1 = [] #  not normalised by nps (for PDF)
    nps = 0
    for i in tqdm(range(nout)):
        fname = args.out[i]
        stats = get_stats(fname)
        aval = stats["average"]
        if aval is not None:
            mval = stats["maximum"]
            n = stats["nps"]
            if mval is not None and n is not None:
                avals.append(aval*n)
                mvals.append(mval*n)
                avals1.append(aval)
                mvals1.append(mval)
                nps += n

    val, err = Print(avals, "Average", nps)
    Print(mvals, "Maximum", nps)
    print(f"nps:     {nps:g}")

    val *= nps
    err *= nps
    print(f"Total time to run all particles on a single core:", end=" ")
    x = ufloat(val, err)
    if val<100:
        print(f"{x} sec")
    elif val < 3600:
        x /= 60
        print(f"{x} min")
    elif val < 24*3600:
        x /= 3600.0
        print(f"{x} h")
    else:
        x /= 24*3600.0
        print(f"{x} d")

    if args.pdf:

        ha = ROOT.TH1F("ha", "Average;Time [s];Number of runs", args.N, min(avals1)*0.99, max(avals1)*1.01)
        hm = ROOT.TH1F("hm", "Maximum;Time [s];Number of runs", args.N, min(mvals1)*0.99, max(mvals1)*1.01)

        for v in avals1:
            ha.Fill(v)

        for v in mvals1:
            hm.Fill(v)

        ha.Draw("hist e")
        ROOT.gPad.Print("%s(" % args.pdf)

        hm.Draw("hist e")
        ROOT.gPad.Print("%s)" % args.pdf)

if __name__ == "__main__":
    exit(main())
