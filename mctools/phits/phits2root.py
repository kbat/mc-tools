#!/usr/bin/env python3
#
#  A script to convert all ANGEL (PHITS) tally outputs of one or several
#  PHITS runs into a single ROOT file
#  https://github.com/kbat/mc-tools
#
#  Usage: phits2root case*/phits.inp
#

import argparse
import logging
import math
import os
import re
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

LOGGER = logging.getLogger("phits2root")

#: tallies whose output is not in the ANGEL format
NON_ANGEL_TALLIES = ("dchain", "wwg", "wwbg", "volume", "userdefined",
                     "4dtrack", "3dshow")

#: maximum nesting level of infl: includes (PHITS limit)
MAX_INFL_DEPTH = 8

sectionRE = re.compile(r"^\s*\[\s*([^\]]+?)\s*\]\s*(\S*)", re.IGNORECASE)
inflRE = re.compile(r"infl:\s*\{([^}]*)\}\s*(?:\[\s*(\d*)\s*-?\s*(\d*)\s*\])?",
                    re.IGNORECASE)
fileRE = re.compile(r"^\s*file\s*=\s*(.*)$", re.IGNORECASE)
dumpRE = re.compile(r"^\s*dump\s*=", re.IGNORECASE)
resc2RE = re.compile(r"^#\s*resc2\s*=\s*(\S+)", re.MULTILINE)


class Tally:
    """A tally section of a PHITS input file."""

    def __init__(self, name, source):
        self.name = name      # tally type, e.g. "track"
        self.source = source  # file the section was read from
        self.files = []       # output file names as given in the input
        self.dump = False

    def __repr__(self):
        return "T-%s %s" % (self.name, self.files)


def strip_comment(line, section):
    """Remove PHITS comments from a line of the input file."""
    if re.match(r"^\s{0,4}c\s", line, re.IGNORECASE):
        return ""
    line = line.split("$", 1)[0]
    if section not in ("surface", "cell"):
        line = re.split(r"[#!]", line, maxsplit=1)[0]
    return line.rstrip()


def read_lines(path, first=None, last=None, depth=0):
    """Return the lines of *path* with infl: includes expanded.

    Each item is a (line, source path) tuple.  Includes written in
    disabled sections are skipped as PHITS does.
    """
    if depth > MAX_INFL_DEPTH:
        raise ValueError("%s: infl: nested more than %d times" % (path, MAX_INFL_DEPTH))
    path = Path(path)
    lines = path.read_text(errors="replace").splitlines()
    first = int(first) if first else 1
    last = int(last) if last else len(lines)
    result = []
    disabled = False
    for line in lines[first - 1:last]:
        mo = sectionRE.match(line)
        if mo:
            disabled = mo.group(2).lower() == "off"
        infl = inflRE.search(line.split("$", 1)[0])
        if infl and not disabled:
            include = path.parent / infl.group(1).strip()
            result += read_lines(include, infl.group(2), infl.group(3), depth + 1)
        else:
            result.append((line, path))
    return result


def parse_input(path):
    """Return the list of enabled tallies defined in the PHITS input *path*."""
    tallies = []
    tally = None
    section = None
    disabled = False
    for raw, source in read_lines(path):
        mo = sectionRE.match(raw)
        if mo:
            section = re.sub(r"\s+", "", mo.group(1)).lower()
            disabled = mo.group(2).lower() == "off"
            if section == "end":
                break
            tally = None
            if section.startswith("t-") and not disabled:
                tally = Tally(section[2:], source)
                tallies.append(tally)
            continue
        if re.match(r"^\s*q:", raw, re.IGNORECASE):
            break
        if tally is None:
            continue
        line = strip_comment(raw, section)
        if dumpRE.match(line):
            tally.dump = True
        mo = fileRE.match(line)
        if mo:
            tally.files += mo.group(1).split()
    return tallies


def tally_outputs(inp):
    """Return the ANGEL output files expected from the PHITS input *inp*."""
    outputs = []
    for tally in parse_input(inp):
        if tally.name in NON_ANGEL_TALLIES or tally.dump:
            LOGGER.info("%s: skipping T-%s %s (not ANGEL output)", inp,
                        tally.name, ' '.join(tally.files))
            continue
        if not tally.files:
            LOGGER.warning("%s: T-%s has no 'file =' parameter", inp, tally.name)
            continue
        for f in tally.files:
            if Path(f).stem.lower().endswith("_err"):
                continue
            outputs.append(f)
    return outputs


def get_weight(path):
    """Return the total source weight (resc2) written in an ANGEL output."""
    mo = resc2RE.search(Path(path).read_text(errors="replace"))
    if mo:
        try:
            return float(mo.group(1).replace("D", "E").replace("d", "e"))
        except ValueError:
            pass
    return None


def convert(job):
    """Convert one ANGEL file into a ROOT file (runs in a worker process)."""
    out, root = job
    # import here so that workers do not inherit ROOT state from the parent
    try:
        from mctools.phits.angel2root import Angel, AngelParseError
    except ImportError:
        from angel2root import Angel, AngelParseError
    if not Path(out).is_file():
        return {"error": "%s does not exist" % out}
    try:
        angel = Angel(out, root)
    except (AngelParseError, OSError, RuntimeError, ValueError) as error:
        return {"error": str(error)}
    return {"ignored": angel.ignored, "weight": get_weight(out)}


class Converter:
    def __init__(self, args):
        self.inp = args.inp
        self.overwrite = args.overwrite
        self.keep = args.keep
        self.njobs = args.njobs if args.njobs > 0 else os.cpu_count()
        self.root = args.output or self.getROOTFileName()

        if not self.overwrite and os.path.isfile(self.root):
            sys.exit("Can't overwrite %s. Remove it or use the '-f' argument." % self.root)
        for f in self.inp:
            if not os.path.isfile(f):
                sys.exit("Error: %s does not exist" % f)

        self.outputs = self.assignOutputs()
        LOGGER.info("input files: %s", self.inp)
        LOGGER.info("tally output files: %s", self.outputs)
        LOGGER.info("output ROOT file: %s", self.root)

    def getROOTFileName(self):
        """ Generate the output ROOT file name based on the input files """
        root = os.path.splitext(self.inp[0])[0] + ".root"
        if len(self.inp) > 1:
            root = re.sub(r'[0-9]+\.root', '.root', root)
        if os.path.basename(root) == '.root':
            root = os.path.basename(self.inp[0])[0] + '.root'
        return os.path.basename(root)

    def assignOutputs(self):
        """Return the list of tally outputs common to all input files."""
        reference = tally_outputs(self.inp[0])
        for inp in self.inp[1:]:
            current = tally_outputs(inp)
            if current != reference:
                print("Error: tally output files differ between input files.", file=sys.stderr)
                print("%s: %s" % (self.inp[0], reference), file=sys.stderr)
                print("%s: %s" % (inp, current), file=sys.stderr)
                sys.exit(4)
        if not reference:
            sys.exit("phits2root: no ANGEL tally outputs defined in %s" % self.inp[0])
        return reference

    def Convert(self, tmpdir):
        """Convert all tally outputs of all runs into per-run ROOT files.

        Return {output: [(rootfile, weight), ...]} for the tallies
        successfully converted in all runs.
        """
        jobs = {}
        for irun, inp in enumerate(self.inp):
            for out in self.outputs:
                path = Path(inp).parent / out
                root = Path(tmpdir) / ("%d_%s.root" % (irun, Path(out).name))
                jobs[(out, irun)] = (str(path), str(root))

        with ProcessPoolExecutor(max_workers=self.njobs) as executor:
            results = dict(zip(jobs, executor.map(convert, jobs.values())))

        converted = {}
        for out in self.outputs:
            runs = [(results[(out, irun)], jobs[(out, irun)])
                    for irun in range(len(self.inp))]
            errors = [r["error"] for r, _ in runs if "error" in r]
            if errors:
                for error in errors:
                    LOGGER.warning("skipping %s: %s", out, error)
                continue
            if any(r["ignored"] for r, _ in runs):
                LOGGER.info("%s: no tally data (ignored by angel2root)", out)
                continue
            weights = [r["weight"] for r, _ in runs]
            if None in weights:
                if len(self.inp) > 1:
                    LOGGER.warning("%s: total source weight (resc2) not found in some "
                                   "runs - using equal weights", out)
                weights = [1.0] * len(weights)
            converted[out] = [(job[1], w) for (_, job), w in zip(runs, weights)]
        return converted

    def Average(self, converted):
        """Return the weighted averages of the objects of all runs."""
        import ROOT
        result = []
        for out, runs in converted.items():
            files = [ROOT.TFile(root) for root, _ in runs]
            weights = [w for _, w in runs]
            for key in files[0].GetListOfKeys():
                name = key.GetName()
                objs = [f.Get(name) for f in files]
                if any(not obj for obj in objs):
                    LOGGER.warning("%s: %s is missing in some runs - skipped", out, name)
                    continue
                avg = average(objs, weights)
                if avg is None:
                    LOGGER.warning("%s: %s is incompatible between runs - skipped", out, name)
                    continue
                result.append(avg)
            for f in files:
                f.Close()
        return result

    def Write(self, objects):
        import ROOT
        fout = ROOT.TFile(self.root, "RECREATE")
        if not fout or fout.IsZombie():
            sys.exit("Can't create %s" % self.root)
        for obj in objects:
            obj.Write()
        shortest = min(self.inp, key=lambda f: len(os.path.basename(f)))
        LOGGER.info("saving %s as TMacro", shortest)
        ROOT.TMacro(shortest).Write()
        fout.Close()

    def Run(self):
        if self.keep:
            tmpdir = tempfile.mkdtemp(prefix="phits2root-", dir=".")
            LOGGER.info("keeping intermediate files in %s", tmpdir)
            converted = self.Convert(tmpdir)
            objects = self.Average(converted)
        else:
            with tempfile.TemporaryDirectory(prefix="phits2root-") as tmpdir:
                converted = self.Convert(tmpdir)
                objects = self.Average(converted)
        if not objects:
            print("phits2root: no tallies converted -> exit", file=sys.stderr)
            return 3
        self.Write(objects)
        return 0


def average(objs, weights):
    """Return the weighted average of compatible ROOT objects.

    mean = sum(w*x)/sum(w), error = sqrt(sum((w*e)^2))/sum(w)
    Return None if the objects are incompatible.
    """
    import ROOT
    first = objs[0]
    if any(obj.ClassName() != first.ClassName() for obj in objs):
        return None
    wsum = sum(weights)

    if first.InheritsFrom("TH1"):
        h = first.Clone()
        h.SetDirectory(0)
        h.Reset()
        for obj, w in zip(objs, weights):
            if obj.GetNcells() != h.GetNcells():
                return None
            if not h.Add(obj, w):
                return None
        h.Scale(1.0 / wsum)
        return h

    if first.InheritsFrom("TGraphErrors"):
        n = first.GetN()
        if any(obj.GetN() != n for obj in objs):
            return None
        g = first.Clone()
        for i in range(n):
            x = first.GetPointX(i)
            if any(not math.isclose(obj.GetPointX(i), x, rel_tol=1e-9, abs_tol=1e-12)
                   for obj in objs):
                return None
            y = sum(w * obj.GetPointY(i) for obj, w in zip(objs, weights)) / wsum
            ey = math.sqrt(sum((w * obj.GetErrorY(i))**2
                               for obj, w in zip(objs, weights))) / wsum
            g.SetPoint(i, x, y)
            g.SetPointError(i, first.GetErrorX(i), ey)
        return g

    if first.InheritsFrom("TMultiGraph"):
        return first.Clone()  # geometry overlay is the same in all runs

    return None


def main():
    """phits2root - convert the ANGEL output of all PHITS tallies defined in the input file(s) into a single ROOT file.
    """
    parser = argparse.ArgumentParser(description=main.__doc__,
                                     epilog="Homepage: https://github.com/kbat/mc-tools")
    parser.add_argument('inp', type=str, nargs="+", help='PHITS input file(s). Tally output files are searched for in the directory of each input file. If multiple files are given, the script will assume the input files differ only in the random seed and average the corresponding tallies weighted by the total source weight.')
    parser.add_argument('-o', '--output', type=str, default=None, help='output ROOT file name (default: derived from the input file name)')
    parser.add_argument('-f', '--force', action='store_true', default=False, dest='overwrite', help='overwrite the output ROOT file')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='print what is being done')
    parser.add_argument('-keep', '--keep-files', action='store_true', default=False, dest='keep', help='do not delete the intermediate per-run ROOT files')
    parser.add_argument('-j', default=0, dest='njobs', type=int, help='number of parallel conversion jobs (default: number of CPUs)')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format="phits2root: %(levelname)s: %(message)s")

    c = Converter(args)
    return c.Run()


if __name__ == "__main__":
    sys.exit(main())
