#!/usr/bin/env python3
#
#  A script to convert ANGEL (PHITS) output into the ROOT format
#  Authors: Konstantin Batkov and Kazuyoshi Furutaka
#  Contact: batkov@gmail.com
#  https://github.com/kbat/mc-tools
#
#  Usage: angel2root.py file.dat
#

import argparse
import logging
import math
import os
import re
import sys
from array import array
from pathlib import Path

import ROOT
# The line below is needed to prevent command-line arguments from
# stolen by PyROOT and handed to TApplication
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import (TH1F, TH2F, TH3F, TFile, TGraph, TGraphErrors,
                  TMultiGraph, TObjArray)

SUBT = re.compile(r"""
\(
(?P<subtitle>.*)\s*?
\)
""", re.VERBOSE)

#: a regular expression which describes the page-separating line.
pageSepRE = re.compile(r"^\s*#?\s*newpage:\s*$", re.IGNORECASE)

#: a regular expression to search for continuation lines of "reg = "
regMeshRE = re.compile(r"^ *([,0-9{}<\(\)\[\]\-\+]|all|u *=).*")

#: a regular expression to separate the values in multiplier subsection
#  ex.1      mat                   mset1
#            all ( 1.79077E-13 2002 1 -4 )
#         => ['( 1.79077E-13 2002 1 -4 )']
#  ex.2      mat         mset1           mset2           mset3
#            all ( 1.0000 -250 ) ( 1.0000 -200 ) ( 1.0000 -201 )
#         => ['( 1.0000 -250 )','( 1.0000 -200 )','( 1.0000 -201 )]
mulDataRE = re.compile(r"(\(.*?\))+") # match non-greedily

LOGGER = logging.getLogger(__name__)


class AngelParseError(ValueError):
    """An ANGEL input error with optional page and line context."""

    def __init__(self, filename, message, *, line=None, page=None):
        location = str(filename)
        if page is not None:
            location += ": page %d" % page
        if line is not None:
            location += ": line %d" % line
        super().__init__("%s: %s" % (location, message))

def is_float(s):
    """
    Return True if s is float. Otherwise return False
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def splitHline(inLine):
    """split an "h:" line into words w/ "(...)" taking into account
    """
    line = inLine.strip() # remove leading/trailing whitespaces
    staPos = [0] # start position of a word (the first should be 0)
    endPos = []
    inParen = False # True if between '(' and ')'
    for idx in range(1,len(line)):
        if line[idx] == '(': inParen = True
        elif line[idx] == ')': inParen = False
        elif line[idx] == ' ' and line[idx-1] != ' ' and not inParen:
            endPos.append(idx)
        elif line[idx] != ' ' and line[idx-1] == ' ' and not inParen:
            staPos.append(idx)
    endPos.append(len(line))
    words = []
    for idx in range(len(staPos)):
        words.append(line[staPos[idx]:endPos[idx]])
    return words


class Angel:
    """Parse an ANGEL file and convert its plots to ROOT objects."""

    def __init__(self, fname_in, fname_out=None, *, avBitSet=False):
        self.dict_nbins = {}
        self.last_nbins_read = None
        self.dict_edges_array = {}
        self.axis = []
        self.ihist = 0
        self.title = ""
        self.xtitle = ""
        self.ytitle = ""
        self.ztitle = ""
        self.mesh = None
        self.output = None
        self.output_title = None
        self.unit = None
        self.unit_title = None
        self.file = None
        self.part = []
        self.return_value = 0
        self.numPlotPages = 0
        self.ignored = False
        self.has_gshow = False
        self.gshow = 0
        self.tally = None
        self.geometry_only = False
        self.histogram_records = []
        self._objects = []
        self.page_info = {}
        self.fname = str(fname_in)
        self.fname_out = str(fname_out) if fname_out is not None else None
        self.histos = TObjArray()
        self.avBitSet = avBitSet
        self.sangel = False # existence of additional angel instruction w/ "sangel = "
        self.lines = tuple(Path(self.fname).read_text(errors="replace").splitlines(True))
        self.pageSepLineLST = []
        self.pageLST = []

        self.parse()
        self.build_objects()
        if self.fname_out is not None:
            self.write(self.fname_out)

    def fail(self, message, *, line=None, page=None):
        raise AngelParseError(self.fname, message, line=line, page=page)

    def parse(self):
        """Split the input into pages and parse tally-wide header fields."""
        self.pageSepLineLST = [
            idx for idx, line in enumerate(self.lines) if pageSepRE.match(line.rstrip())
        ]
        if not self.pageSepLineLST:
            self.fail("no ANGEL 'newpage:' separator found")

        starts = [-1] + self.pageSepLineLST
        ends = self.pageSepLineLST + [len(self.lines)]
        self.pageLST = [tuple(self.lines[start + 1:end])
                        for start, end in zip(starts, ends)]
        self.numPlotPages = len(self.pageLST) - 1
        LOGGER.debug("found %d ANGEL plot pages", self.numPlotPages)
        self.parse_header(self.pageLST[0])

    def parse_header(self, header):
        """Extract tally-wide configuration from the ANGEL header page."""
        compact_header = re.sub(r"\s+", "", ''.join(header))
        tally = re.search(r"\[T-([^\]]+)\]", compact_header, re.IGNORECASE)
        if tally:
            self.tally = tally.group(1).lower()

        iline = 0
        while iline < len(header):
            line = header[iline].strip()
            if re.match(r"^title\s*=", line):
                words = line.split()
                if len(words) < 3:
                    self.fail("malformed title declaration", line=iline + 1)
                self.title = ' '.join(words[2:])
                iline += 1
            elif re.match(r"^mesh\s*=", line):
                words = line.split()
                if len(words) < 3:
                    self.fail("malformed mesh declaration", line=iline + 1)
                self.mesh = words[2]
                iline += 1
                if self.mesh in ("reg", "tet"):
                    if iline >= len(header) or "=" not in header[iline]:
                        self.fail("region mesh is missing its 'reg =' declaration",
                                  line=iline + 1)
                    self.reg = [header[iline].split("=", 1)[1].split("#", 1)[0].strip()]
                    iline += 1
                    while iline < len(header) and regMeshRE.match(header[iline]):
                        self.reg.append(header[iline].strip())
                        iline += 1
            elif re.match(r"^axis\s*=", line):
                for a in line.split()[2:]:
                    if a == '#': break
                    self.axis.append(a)
                iline += 1
            elif re.search(r"^n[eartxyzl]\s*=", line):
                words = line.split()
                try:
                    self.dict_nbins[words[0]] = int(words[2])
                except (IndexError, ValueError):
                    self.fail("malformed bin-count declaration", line=iline + 1)
                self.last_nbins_read = words[0]
                iline += 1
            elif re.search(r"^[#$]\s*data\s*=", line):
                if self.last_nbins_read is None:
                    self.fail("bin-edge data has no preceding bin count", line=iline + 1)
                self.dict_edges_array[self.last_nbins_read] = self.GetBinEdges(iline)
                iline += 1
            elif re.match(r"^part\s*=", line):
                words = line.split()
                # Multiplier blocks can contain another ``part =`` line.
                # Keep the tally's first particle list for naming columns.
                if not self.part:
                    self.part = words[2:]
                iline += 1
            elif re.match(r"^output\s*=", line):
                words = line.split()
                if len(words) < 3:
                    self.fail("malformed output declaration", line=iline + 1)
                self.output = words[2]
                self.output_title = ' '.join(words[4:])
                if self.unit_title is not None:
                    self.ztitle = (self.output_title + " " + self.unit_title).strip()
                iline += 1
            elif re.match(r"^unit\s*=", line):
                words = line.split()
                if len(words) < 3:
                    self.fail("malformed unit declaration", line=iline + 1)
                self.unit = words[2]
                self.unit_title = ' '.join(words[6:])
                if self.output_title is not None:
                    self.ztitle = (self.output_title + " " + self.unit_title).strip()
                iline += 1
            elif re.match(r"^file\s*=", line):
                words = line.split()
                if len(words) < 3:
                    self.fail("malformed file declaration", line=iline + 1)
                self.file = os.path.splitext(words[2])[0]
                iline += 1
            elif re.match(r"^multiplier\s*=", line):
                block = header[iline + 1:iline + 6]
                if len(block) != 5:
                    self.fail("truncated multiplier block", line=iline + 1)
                fields = [entry.strip().split() for entry in block]
                if len(fields[0]) < 3 or len(fields[2]) < 3 or len(fields[3]) < 2:
                    self.fail("malformed multiplier block", line=iline + 1)
                self.mult_part = fields[0][2]
                self.mult_emax = fields[2][2]
                self.mult_mat = fields[3][1:]
                self.mult_mul = mulDataRE.findall(block[4].strip())
                if not self.mult_mul:
                    self.fail("multiplier block has no multiplier data", line=iline + 6)
                iline += 6
            elif re.match(r"^sangel\s*=", line):
                self.sangel = True
                iline += 1
            elif re.match(r"^gshow\s*=", line):
                words = line.split()
                try:
                    self.gshow = int(words[2])
                except (IndexError, ValueError):
                    self.fail("malformed gshow declaration", line=iline + 1)
                iline += 1
            else:
                iline += 1

        if not self.file:
            self.file = Path(self.fname).stem
        has_gshow = self.gshow > 0
        has_gshow = bool(has_gshow or any(
            re.search(r"^\s*#\s*gshow\s*$", '\n'.join(page), re.IGNORECASE | re.MULTILINE)
            for page in self.pageLST[1:]
        ))
        self.has_gshow = has_gshow
        self.geometry_only = bool(re.search(r"t\s*-\s*gshow", self.title or '', re.IGNORECASE))
        if self.geometry_only:
            LOGGER.info("ignoring tally %s (T-Gshow)", self.file)
            self.ignored = True

    def build_objects(self):
        """Decode all plot pages into in-memory ROOT objects."""
        if self.ignored:
            return
        self.page_info = {
            npage: self.GetPageInfo(self.pageLST[npage])
            for npage in range(1, len(self.pageLST))
        }
        for npage in range(1, len(self.pageLST)):
            page = self.pageLST[npage]
            hLST = []
            page_subtitle = ""
            for iline, line in enumerate(page):
                if re.search("^x:", line):
                    words = line.split()
                    self.xtitle = ' '.join(words[1:])
                    continue
                elif re.search("^y:", line):
                    words = line.split()
                    self.ytitle = ' '.join(words[1:])
                    continue
                elif re.search("^z:", line):
                    if not re.search("xorg", line):
                        LOGGER.warning("page %d contains an unsupported z graph", npage)
                    continue
                elif re.search("'no. =", line):
                    page_subtitle = (' '.join(line[line.find(',') + 1:].split())
                                     .replace("'", '').strip())
                elif re.search("^h", line):
                    hLST.append((iline, line.split()[0]))
            if self.sangel and not hLST:
                self.fail("sangel page contains no histogram section", page=npage)

            in_gshow = False
            for iline, line in enumerate(page):
                if self.sangel and iline < hLST[-1][0]:
                    continue
                igline = iline + self.pageSepLineLST[npage - 1] + 1
                if re.search(r"^\s*#\s*gshow\s*$", line, re.IGNORECASE):
                    in_gshow = True
                    continue
                if in_gshow and not re.search(r"^h2:", line):
                    continue
                if re.search(r"^h2:", line):
                    in_gshow = False
                if re.search("^h", line):
                    if re.search("^h: [nx]", line):
                        self.Read1DHist(igline, npage, page_subtitle)
                        continue
                    elif re.search("h:              x", line):
                        self.Read1DGraphErrors(igline, npage, page_subtitle=page_subtitle)
                        continue
                    elif re.search("h:   x      n     n", line) and \
                            iline + 1 < len(page) and re.search(
                                "#    num    tetra   volume", page[iline + 1].strip()):
                        self.Read1DGraphErrors(igline, npage, tet=True,
                                               page_subtitle=page_subtitle)
                        continue
                    elif re.search("^h([2d]|c2?):", line):
                        self.Read2DHist(igline, npage, page_subtitle)
                        break
                    elif 'reg' in self.axis:
                        self.Read1DHist(igline, npage, page_subtitle)
                        continue
        self.CombinePageHistograms()
        if not self.histos.GetEntries():
            if self.has_gshow:
                LOGGER.info("ignoring tally with gshow output: %s", self.file)
                self.ignored = True
                return
            self.fail("no supported histograms or graphs found")
        self.BuildGeometry()

    def write(self, filename):
        """Write converted objects to *filename* after successful parsing."""
        output = Path(filename)
        if output.is_dir():
            raise OSError("cannot create ROOT output file: %s is a directory" % output)
        if self.ignored:
            output.unlink(missing_ok=True)
            return
        fout = TFile(str(output), "RECREATE")
        if not fout or fout.IsZombie():
            if fout:
                fout.Close()
            raise OSError("cannot create ROOT output file: %s" % output)
        complete = False
        try:
            fout.cd()
            written = sum(self.histos[index].Write()
                          for index in range(self.histos.GetEntries()))
            if written <= 0:
                raise OSError("ROOT did not write any objects to %s" % output)
            complete = True
        finally:
            fout.Close()
            if not complete:
                output.unlink(missing_ok=True)

    def GetPageInfo(self, page):
        """Extract mesh coordinates and particle name from an ANGEL page."""
        info = {}
        text = '\n'.join(page)
        for key, value in re.findall(
                r"\b(ia|ie|ix|iy|iz|it|il)\s*=\s*([+-]?\d+)", text):
            info[key] = int(value)
        particle = re.search(r"\bpart\.?\s*=\s*([^\s]+)", text)
        if particle:
            info['part'] = particle.group(1)
        return info

    def AddHistogram(self, histogram, page_num, slot=0, label=''):
        """Add a ROOT object and retain the page information used for merging."""
        if histogram.InheritsFrom('TH1'):
            histogram.SetDirectory(0)
        self._objects.append(histogram)
        self.histos.Add(histogram)
        self.histogram_records.append({
            'histogram': histogram,
            'page': page_num,
            'slot': slot,
            'label': label,
            'page_info': self.page_info.get(page_num, {}),
        })

    def PageAxis(self):
        """Return the ANGEL page index and its PHITS bin edges, if present."""
        edge_names = {
            'ia': 'na', 'ie': 'ne', 'ix': 'nx', 'iy': 'ny', 'iz': 'nz',
            'it': 'nt', 'il': 'nl',
        }
        for page_key in ('ia', 'ie', 'ix', 'iy', 'iz', 'it', 'il'):
            edge_key = edge_names[page_key]
            if edge_key not in self.dict_edges_array:
                continue
            edges = self.dict_edges_array[edge_key]
            if len(edges) <= 2 or not self.histogram_records:
                continue
            values = [r['page_info'].get(page_key) for r in self.histogram_records]
            if None not in values and len(set(values)) == len(edges) - 1:
                return page_key, edge_key, edges
        return None

    def CombinePageHistograms(self):
        """Combine ANGEL pages into the lowest-dimensional ROOT histogram.

        ANGEL represents an N-dimensional PHITS tally as one lower-dimensional
        plot per value of an additional mesh coordinate.  A 1D page therefore
        becomes a TH2F and a 2D page becomes a TH3F.  Objects that cannot be
        grouped unambiguously are kept as emitted by ANGEL.
        """
        page_axis = self.PageAxis()
        if not page_axis or not self.histogram_records:
            return

        page_key, edge_key, page_edges = page_axis
        page_bins = len(page_edges) - 1
        records = self.histogram_records
        if any(r['histogram'].InheritsFrom('TGraph') for r in records):
            return

        # Group by the histogram column (slot) and particle.  Some tallies
        # identify the particle on each page, while others (such as
        # T-Product DDX output) put one particle in each histogram column.
        groups = {}
        for record in records:
            value = record['page_info'].get(page_key)
            if value is None:
                return
            particle = record['page_info'].get('part', '')
            if not particle and record['slot'] < len(self.part):
                particle = self.part[record['slot']]
            if not particle:
                particle = record['label']
            key = (record['slot'], particle)
            groups.setdefault(key, []).append(record)

        if not groups or any(len(group) != page_bins for group in groups.values()):
            return

        combined = []
        for (slot, particle), group in groups.items():
            group.sort(key=lambda r: r['page_info'][page_key])
            if [r['page_info'][page_key] for r in group] != list(range(1, page_bins + 1)):
                return

            first = group[0]['histogram']
            if any(r['histogram'].ClassName() != first.ClassName() for r in group):
                return
            if first.InheritsFrom('TH1') and not first.InheritsFrom('TH2'):
                result = self.Combine1DGroup(first, group, page_edges, page_key, particle, slot)
            elif first.InheritsFrom('TH2') and not first.InheritsFrom('TH3'):
                result = self.Combine2DGroup(first, group, page_edges, page_key, particle, slot)
            else:
                return
            if result is None:
                return
            combined.append(result)

        # Replace the page objects so callers and the output file see the
        # actual tally histogram(s), not the intermediate ANGEL projections.
        self.histos = TObjArray()
        for histogram in combined:
            histogram.SetDirectory(0)
            self._objects.append(histogram)
            self.histos.Add(histogram)

    def PageAxisTitle(self, page_key):
        return {
            'ia': 'Angle', 'ie': 'Energy', 'ix': 'x', 'iy': 'y',
            'iz': 'z', 'it': 'Time', 'il': 'LET',
        }.get(page_key, page_key)

    def CombinedName(self, base, slot, particle):
        name = base
        if particle:
            name += '_%s' % particle
        elif slot:
            name += '_%d' % slot
        return name

    def PageHistogramName(self, page_num):
        """Name an unmerged page histogram using its particle identifier."""
        if self.numPlotPages == 1:
            return self.file

        particle = self.page_info.get(page_num, {}).get('part', '')
        if not particle:
            return "%s_%d" % (self.file, page_num)

        matching_pages = sum(
            info.get('part') == particle for info in self.page_info.values())
        if matching_pages == 1:
            return "%s_%s" % (self.file, particle)
        return "%s_%s_%d" % (self.file, particle, page_num)

    def GshowPolylines(self, page):
        """Extract ANGEL ``clip:`` polylines from a page's gshow section."""
        marker = next((index for index, line in enumerate(page)
                       if re.match(r"^\s*#\s*gshow\s*$", line,
                                   re.IGNORECASE)), None)
        if marker is None:
            return []

        polylines = []
        index = marker + 1
        while index < len(page):
            if page[index].strip().lower() != 'clip:':
                index += 1
                continue

            points = []
            index += 1
            while index < len(page):
                words = page[index].split()
                if len(words) != 2:
                    break
                try:
                    point = tuple(float(word.replace('D', 'E').replace('d', 'e'))
                                  for word in words)
                except ValueError:
                    break
                if not all(math.isfinite(value) for value in point):
                    break
                points.append(point)
                index += 1
            if len(points) >= 2:
                polylines.append(points)
        return polylines

    def BuildGeometry(self):
        """Create TMultiGraph geometry overlays for T-Track xyz tallies."""
        if self.tally != 'track' or self.mesh != 'xyz' or self.gshow != 1:
            return

        # Geometry depends on the selected spatial slice, not on particle or
        # energy.  PHITS repeats the same gshow section for those pages, so
        # parse it only once per spatial index combination.
        geometries = {}
        for page_num in range(1, len(self.pageLST)):
            info = self.page_info.get(page_num, {})
            slice_key = tuple((key, info[key]) for key in ('ix', 'iy', 'iz')
                              if key in info)
            if slice_key in geometries:
                continue
            polylines = self.GshowPolylines(self.pageLST[page_num])
            if polylines:
                geometries[slice_key] = polylines

        multiple = len(geometries) > 1
        for slice_key, polylines in geometries.items():
            name = "%s_geometry" % self.file
            if multiple:
                name += ''.join("_%s%d" % item for item in slice_key)
            multigraph = TMultiGraph(
                name, "%s geometry;%s;%s" %
                (self.title, self.xtitle, self.ytitle))
            for graph_num, points in enumerate(polylines, 1):
                graph = TGraph(
                    len(points), array('d', (point[0] for point in points)),
                    array('d', (point[1] for point in points)))
                graph.SetName("%s_%d" % (name, graph_num))
                graph.SetLineColor(ROOT.kBlack)
                multigraph.Add(graph, 'L')
                ROOT.SetOwnership(graph, False)
            self._objects.append(multigraph)
            self.histos.Add(multigraph)

    def CompatibleAxes(self, first, group, axes):
        """Check that every page in a group has identical binning."""
        reference = [self.getAxisEdges(getattr(first, 'Get%saxis' % axis)())
                     for axis in axes]
        for record in group[1:]:
            current = [self.getAxisEdges(getattr(record['histogram'],
                                                  'Get%saxis' % axis)())
                       for axis in axes]
            if current != reference:
                return False
        return True

    def Combine1DGroup(self, first, group, page_edges, page_key, particle, slot):
        if not self.CompatibleAxes(first, group, ('X',)):
            return None
        xedges = self.getXarray(first)
        yedges = array('f', [float(edge) for edge in page_edges])
        name = self.CombinedName(self.file or first.GetName(), slot, particle)
        title = '%s;%s;%s' % (self.title, first.GetXaxis().GetTitle(),
                              self.PageAxisTitle(page_key))
        histogram = TH2F(name, title, first.GetNbinsX(), array('f', xedges),
                         len(page_edges) - 1, yedges)
        for iy, record in enumerate(group, 1):
            source = record['histogram']
            for ix in range(1, source.GetNbinsX() + 1):
                histogram.SetBinContent(ix, iy, source.GetBinContent(ix))
                histogram.SetBinError(ix, iy, source.GetBinError(ix))
        return histogram

    def Combine2DGroup(self, first, group, page_edges, page_key, particle, slot):
        if not self.CompatibleAxes(first, group, ('X', 'Y')):
            return None
        xedges = self.getXarray(first)
        yedges = self.getYarray(first)
        zedges = array('f', [float(edge) for edge in page_edges])
        name = self.CombinedName(self.file or first.GetName(), slot, particle)
        title = '%s;%s;%s;%s' % (self.title, first.GetXaxis().GetTitle(),
                                 first.GetYaxis().GetTitle(),
                                 self.PageAxisTitle(page_key))
        histogram = TH3F(name, title, first.GetNbinsX(), array('f', xedges),
                         first.GetNbinsY(), array('f', yedges),
                         len(page_edges) - 1, zedges)
        for iz, record in enumerate(group, 1):
            source = record['histogram']
            for iy in range(1, source.GetNbinsY() + 1):
                for ix in range(1, source.GetNbinsX() + 1):
                    histogram.SetBinContent(ix, iy, iz, source.GetBinContent(ix, iy))
                    histogram.SetBinError(ix, iy, iz, source.GetBinError(ix, iy))
        return histogram

    def GetBinEdges(self, iline):
        edges = []
        for line_no, line in enumerate(self.lines[iline + 1:], iline + 2):
            words = line.split()
            if not words:
                break
            if line.lstrip().startswith(('#', '$')):
                candidates = words[1:]
            elif is_float(words[0]):
                candidates = words
            else:
                break
            for word in candidates:
                try:
                    value = float(word)
                except ValueError:
                    self.fail("invalid bin edge %r" % word, line=line_no)
                if not math.isfinite(value):
                    self.fail("non-finite bin edge %r" % word, line=line_no)
                edges.append(value)

        expected = self.dict_nbins[self.last_nbins_read]
        if len(edges) != expected + 1:
            self.fail("expected %d bin edges, found %d" % (expected + 1, len(edges)),
                      line=iline + 1)
        if any(right <= left for left, right in zip(edges, edges[1:])):
            self.fail("bin edges must be strictly increasing", line=iline + 1)
        return tuple(edges)

    def GetNhist(self, line):
        """
        Analyzes the section header and return the number of histograms in the section data
        (but not in the entire file!)
        """
# Let's remove all spaces between ')'. For some reason line.replace('\s*)', ')') does not work
# so we do it in this weird way:
        line1 = None
        while line1 != line:
            line1 = line
            line = line.replace(' )', ')')

        words = splitHline(line)
        subtitles = []
        for w in words:
            if re.search("^y", w):
                mo = SUBT.search(w)
                subtitles.append(mo.group('subtitle') if mo else '')
        if not subtitles:
            self.fail("histogram section declares no y columns")
        return len(subtitles), subtitles

    def Read1DHist(self, iline, pageNum, page_subtitle=""):
        """
        Read 1D histogram section
        """
        nhist, subtitles = self.GetNhist(self.lines[iline])
        isCharge = False
        if re.search("x-0.5", self.lines[iline].split()[1]):
            isCharge = True # the charge-mass-chart distribution, x-axis is defined by the 1st column only
            if nhist != 1:
                self.fail("charge histogram must contain exactly one y column",
                          line=iline + 1, page=pageNum)
        xarray = []
        xmax = None
        data = {}     # dictionary for all histograms in the current section
        errors = {}   # dictionary for all histograms in the current section
        bin_labels = [] # relevant for self.axis == 'reg' only

        for ihist in range(nhist):  # create the empty lists, so we could append later
            data[ihist] = []
            errors[ihist] = []

        for line_no, line in enumerate(self.lines[iline + 1:], iline + 2):
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            try:
                if isCharge:
                    if len(words) != 3:
                        raise ValueError("expected 3 columns")
                    xarray.append(float(words[0])-0.5)
                    xmax = float(words[0])+0.5
                    data[0].append(float(words[1]))
                    errors[0].append(float(words[2]))
                elif 'reg' in self.axis:
                    value_idx = len(words) - 2 * nhist
                    if value_idx < 1:
                        raise ValueError("not enough value/error columns")
                    xarray.append(float(words[0])-0.5)
                    xmax = float(words[0])+0.5
                    bin_labels.append(words[1] if value_idx > 2 else words[0])
                    for ihist in range(nhist):
                        data[ihist].append(float(words[value_idx + ihist * 2]))
                        errors[ihist].append(float(words[value_idx + ihist * 2 + 1]))
                else:
                    expected = 2 + 2 * nhist
                    if len(words) < expected:
                        raise ValueError("expected at least %d columns, found %d" %
                                         (expected, len(words)))
                    xarray.append(float(words[0]))
                    xmax = float(words[1])
                    for ihist in range(nhist):
                        data[ihist].append(float(words[(ihist+1)*2]))
                        errors[ihist].append(float(words[(ihist+1)*2+1]))
            except (ValueError, IndexError) as error:
                self.fail("invalid 1D histogram row (%s): %s" % (error, line),
                          line=line_no, page=pageNum)

        nbins = len(xarray)
        if not nbins or xmax is None:
            self.fail("1D histogram contains no data", line=iline + 1,
                      page=pageNum)
        xarray.append(xmax)
        if any(not math.isfinite(value) for value in xarray):
            self.fail("1D histogram has non-finite bin edges", page=pageNum)
        if any(right <= left for left, right in zip(xarray, xarray[1:])):
            self.fail("1D histogram bin edges must be strictly increasing",
                      page=pageNum)
        for values in list(data.values()) + list(errors.values()):
            if any(not math.isfinite(value) for value in values):
                self.fail("1D histogram contains non-finite data", page=pageNum)

        for ihist in range(nhist):
            section_subtitle = subtitles[ihist]
            title_subtitle = page_subtitle or section_subtitle
            subtitle = ' - ' + title_subtitle if title_subtitle else ''
            self.FixTitles()
            # self.ihist+1 - start from ONE as in Angel - easy to compare
            if self.numPlotPages == 1:
                if nhist == 1:
                    hname = "%s" % (self.file)
                else:
                    hname = "%s_%s" % (self.file, section_subtitle or ihist + 1)
            else:
                if nhist == 1:
                    hname = "%s_%d" % (self.file, pageNum)
                else:
                    hname = "%s_%d_%s" % (self.file, pageNum,
                                            section_subtitle or ihist + 1)
            h = TH1F(hname, "%s%s;%s;%s" % (self.title, subtitle, self.xtitle, self.ytitle), nbins, array('f', xarray))
            if self.avBitSet:
                h.SetBit(TH1F.kIsAverage)
            self.ihist += 1
            for i in range(nbins):
                val = data[ihist][i]
                err = abs(errors[ihist][i] * val)
                h.SetBinContent(i+1, val)
                h.SetBinError(i+1, err)

            if 'reg' in self.axis:
                for i in range(nbins):
                    h.GetXaxis().SetBinLabel(i+1, bin_labels[i])
                h.GetXaxis().SetTitle("Region number")

            self.AddHistogram(h, pageNum, ihist, section_subtitle)

    def Read1DGraphErrors(self, iline, pageNum, tet=False, page_subtitle=""):
        """
        Read 1D graph section
        """
        ngraphs, subtitles = self.GetNhist(self.lines[iline])
        xarray = []
        data = {}
        errors = {}
        tetShift = 2 if tet else 0 # column shift for tetra mesh

        for igraph in range(ngraphs):
            data[igraph] = []
            errors[igraph] = []

        for line_no, line in enumerate(self.lines[iline + 1:], iline + 2):
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            expected = 1 + tetShift + 2 * ngraphs
            if len(words) < expected:
                self.fail("invalid graph row: expected at least %d columns, found %d" %
                          (expected, len(words)), line=line_no, page=pageNum)
            try:
                xarray.append(float(words[0]))
                for igraph in range(ngraphs):
                    data[igraph].append(float(words[(igraph+1)*2-1+tetShift]))
                    errors[igraph].append(float(words[(igraph+1)*2+tetShift]))
            except ValueError as error:
                self.fail("invalid graph row (%s): %s" % (error, line),
                          line=line_no, page=pageNum)

        npoints = len(xarray)
        if not npoints:
            self.fail("graph contains no data", line=iline + 1, page=pageNum)
        for values in [xarray] + list(data.values()) + list(errors.values()):
            if any(not math.isfinite(value) for value in values):
                self.fail("graph contains non-finite data", page=pageNum)

        for igraph in range(ngraphs):
            section_subtitle = subtitles[igraph]
            title_subtitle = page_subtitle or section_subtitle
            subtitle = ' - ' + title_subtitle if title_subtitle else ''
            self.FixTitles()
            g = TGraphErrors(npoints)
            # self.ihist+1 - start from ONE as in Angel - easy to compare
            if self.numPlotPages == 1:
                if ngraphs == 1:
                    gname = self.file
                else:
                    gname = "%s_%s" % (self.file, section_subtitle or igraph + 1)
            else:
                if ngraphs == 1:
                    gname = "%s_%d" % (self.file, pageNum)
                else:
                    gname = "%s_%d_%s" % (self.file, pageNum,
                                            section_subtitle or igraph + 1)
            g.SetNameTitle(gname, "%s%s;%s;%s" % (self.title, subtitle, self.xtitle, self.ytitle))
            self.ihist += 1
            for i in range(npoints):
                x = xarray[i]
                y = data[igraph][i]
                ey = errors[igraph][i]
                g.SetPoint(i, x, y)
                g.SetPointError(i, 0, abs(ey * y))

            self.AddHistogram(g, pageNum, igraph, section_subtitle)


    def FixTitles(self):
        """
        Makes some ROOT fixes

        """
        self.ytitle = self.ytitle.replace("cm^2", "cm^{2}")
        self.ytitle = self.ytitle.replace("cm^3", "cm^{3}")
        self.title = self.title.replace("cm^2", "cm^{2}")
        self.title = self.title.replace("cm^3", "cm^{3}")

    def Read2DHist(self, iline, pageNum=None, page_subtitle=""):
        """
        Read 2D histogram section
        """
        line = self.lines[iline].replace(" =", "=") # sometimes Angel writes 'y=' and sometimes 'y ='
        words = line.split()
        if len(words) != 15:
            self.fail("invalid 2D header: expected 15 fields, found %d" % len(words),
                      line=iline + 1, page=pageNum)
        try:
            yfirst, ylast, dy = map(float, (words[2], words[4], words[6]))
            xfirst, xlast, dx = map(float, (words[9], words[11], words[13]))
        except ValueError as error:
            self.fail("invalid 2D header (%s)" % error, line=iline + 1,
                      page=pageNum)
        if not all(math.isfinite(value)
                   for value in (yfirst, ylast, dy, xfirst, xlast, dx)):
            self.fail("2D header contains non-finite coordinates", line=iline + 1,
                      page=pageNum)
        if dx == 0 or dy == 0:
            self.fail("2D histogram bin width cannot be zero", line=iline + 1,
                      page=pageNum)

        def bounds_and_bins(first, last, step, axis_name):
            width = abs(step)
            low = min(first, last) - width / 2.0
            high = max(first, last) + width / 2.0
            bins_float = (high - low) / width
            bins = int(round(bins_float))
            if bins <= 0 or not math.isclose(bins_float, bins, rel_tol=1e-6,
                                              abs_tol=1e-6):
                self.fail("%s range is not an integer number of bins" % axis_name,
                          line=iline + 1, page=pageNum)
            return low, high, bins

        ymin, ymax, ny = bounds_and_bins(yfirst, ylast, dy, "y")
        xmin, xmax, nx = bounds_and_bins(xfirst, xlast, dx, "x")

        data = []
        for line_no, line in enumerate(self.lines[iline + 1:], iline + 2):
            line = line.strip()
            if line == '': break
            elif re.search("^#", line): continue
            words = line.split()
            for w in words:
                if w == 'z:':
                    return # this was a color palette
                try:
                    value = float(w)
                except ValueError:
                    self.fail("invalid 2D data value %r" % w, line=line_no,
                              page=pageNum)
                if not math.isfinite(value):
                    self.fail("non-finite 2D data value %r" % w, line=line_no,
                              page=pageNum)
                data.append(value)
        expected = nx * ny
        if len(data) != expected:
            self.fail("2D histogram expected %d values, found %d" %
                      (expected, len(data)), line=iline + 1, page=pageNum)

        hname = self.PageHistogramName(pageNum)
        title = self.title + (" - " + page_subtitle if page_subtitle else "")
        h = TH2F(hname, "%s;%s;%s;%s" %
                 (title, self.xtitle, self.ytitle, self.ztitle),
                 nx, xmin, xmax, ny, ymin, ymax)
        self.ihist += 1

        for y in range(ny-1, -1, -1):
            for x in range(nx):
                d = data[x+(ny-1-y)*nx]
                h.SetBinContent(x+1, y+1, d)
        self.AddHistogram(h, pageNum, 0)

    def getXarray(self, h):
        """
        Return the tuple with x-low-edges of TH1 'h'
        """
        return self.getAxisEdges(h.GetXaxis())

    def getYarray(self, h):
        """Return the y-axis bin edges of a ROOT histogram."""
        return self.getAxisEdges(h.GetYaxis())

    def getAxisEdges(self, axis):
        """Return all low edges plus the upper edge of a ROOT axis."""
        return [float(axis.GetBinLowEdge(i)) for i in range(1, axis.GetNbins() + 2)]

    def Make2Dfrom1D(self):
        """Compatibility wrapper for callers of older versions."""
        return self.CombinePageHistograms()



def main():
    """
    angel2root - ANGEL to ROOT converter
    """
    parser = argparse.ArgumentParser(description=main.__doc__, epilog="Homepage: https://github.com/kbat/mc-tools")

    parser.add_argument("-a", "--average", action="store_true",
                        help="set the TH1.kIsAverage bit for averaging")
    parser.add_argument("infilename", type=Path,
                        help="input ANGEL filename")
    parser.add_argument("-o", "--output", type=Path,
                        help="output ROOT filename (default: input with .root suffix)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="enable detailed conversion logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format="%(levelname)s: %(message)s")
    fname_in = args.infilename
    fname_out = args.output or fname_in.with_suffix(".root")
    if fname_in == fname_out:
        fname_out = Path(str(fname_in) + ".root")
    LOGGER.info("converting %s -> %s", fname_in, fname_out)

    try:
        angel = Angel(fname_in, fname_out, avBitSet=args.average)
    except (AngelParseError, OSError, RuntimeError) as error:
        LOGGER.error("%s", error)
        return 1
    return angel.return_value

if __name__ == "__main__":
    sys.exit(main())
