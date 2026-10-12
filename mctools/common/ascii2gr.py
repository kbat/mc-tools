#!/usr/bin/env python3
"""Convert whitespace-separated ASCII data to ROOT graphs."""

import argparse
import sys

import ROOT

ROOT.PyConfig.IgnoreCommandLineOptions = True


def _read_blocks(fname, l1=None, l2=None):
    """Yield data blocks and their optional EXFOR-style metadata."""
    start = 1 if l1 is None else l1
    with open(fname) as source:
        lines = source.readlines()

    end = len(lines) if l2 is None else min(l2, len(lines))
    print("--->reading between lines", start, end)

    rows = []
    metadata = {"title": "", "xtitle": "", "ytitle": ""}
    for line_number, line in enumerate(lines, 1):
        if line_number < start:
            continue
        if line_number > end:
            break

        words = line.split()
        if not words:
            if rows:
                yield rows, metadata
            rows = []
            metadata = {"title": "", "xtitle": "", "ytitle": ""}
            continue

        if words[0].startswith("#"):
            if words[0] == "#name:":
                metadata["title"] = " ".join(words[1:])
            elif words[0] == "#X.axis:":
                metadata["xtitle"] = " ".join(words[1:])
            elif words[0] == "#Y.axis:":
                metadata["ytitle"] = " ".join(words[1:])
            continue

        if len(words) < 2:
            print("Skipping line", line.strip())
            continue
        rows.append(words)

    if rows:
        yield rows, metadata


def _column(words, column):
    if column is None or column < 1:
        raise ValueError("column numbers must start at one")
    return float(words[column - 1])


def _new_graph_array():
    graphs = ROOT.TObjArray()
    graphs.SetOwner(True)
    return graphs


def _graph_name(name, index):
    return name if index == 0 else "%s%d" % (name, index)


def _add_graph(graphs, graph, name, index):
    ROOT.SetOwnership(graph, False)
    graph.SetName(_graph_name(name, index))
    graphs.Add(graph)


def _make_graph(rows, colx, colex, coly, coley, title, metadata, relerr,
                name, name_index, graphs):
    graph_class = ROOT.TGraph if colex is None and coley is None else ROOT.TGraphErrors
    graph = graph_class(len(rows))
    graph_title = metadata["title"] or title
    graph.SetTitle(graph_title)
    if metadata["xtitle"] or metadata["ytitle"]:
        graph.GetXaxis().SetTitle(metadata["xtitle"])
        graph.GetYaxis().SetTitle(metadata["ytitle"])

    for point, words in enumerate(rows):
        x = _column(words, colx)
        y = _column(words, coly)
        graph.SetPoint(point, x, y)
        if graph_class is ROOT.TGraphErrors:
            x_error = 0.0 if colex is None else _column(words, colex)
            y_error = 0.0 if coley is None else _column(words, coley)
            if relerr:
                x_error *= x
                y_error *= y
            graph.SetPointError(point, x_error, y_error)

    _add_graph(graphs, graph, name, name_index)


def _make_asymm_graph(rows, colx, exlow, exhigh, coly, eylow, eyhigh,
                      name, name_index, graphs):
    graph = ROOT.TGraphAsymmErrors(len(rows))
    for point, words in enumerate(rows):
        graph.SetPoint(point, _column(words, colx), _column(words, coly))
        graph.SetPointError(
            point,
            _column(words, exlow),
            _column(words, exhigh),
            _column(words, eylow),
            _column(words, eyhigh),
        )
    _add_graph(graphs, graph, name, name_index)


def GetGraphs(colx, colex, coly, coley, fname, l1, l2, name, title, relerr):
    graphs = _new_graph_array()
    for name_index, (rows, metadata) in enumerate(_read_blocks(fname, l1, l2)):
        _make_graph(rows, colx, colex, coly, coley, title, metadata, relerr,
                    name, name_index, graphs)
    return graphs


def GetAsymmGraphs(colx, exlow, exhigh, coly, eylow, eyhigh, fname, l1, l2,
                   name):
    graphs = _new_graph_array()
    for name_index, (rows, _metadata) in enumerate(_read_blocks(fname, l1, l2)):
        _make_asymm_graph(rows, colx, exlow, exhigh, coly, eylow, eyhigh,
                          name, name_index, graphs)
    return graphs


# Keep the historical helper names available to callers importing this module.
def GetGraph(colx, colex, coly, coley, fname, l1, l2, name, title, graphs,
             name_index=0, relerr=False):
    for block_index, (rows, metadata) in enumerate(_read_blocks(fname, l1, l2)):
        _make_graph(rows, colx, colex, coly, coley, title, metadata, relerr,
                    name, name_index + block_index, graphs)


def GetAsymmGraph(colx, exlow, exhigh, coly, eylow, eyhigh, fname, l1, l2,
                  name, graphs, name_index):
    for block_index, (rows, _metadata) in enumerate(_read_blocks(fname, l1, l2)):
        _make_asymm_graph(rows, colx, exlow, exhigh, coly, eylow, eyhigh,
                          name, name_index + block_index, graphs)


def _parser():
    parser = argparse.ArgumentParser(
        description="Convert ASCII table data to TGraph or TGraphErrors.",
        epilog="Homepage: https://github.com/kbat/mc-tools",
    )
    parser.add_argument("-x", dest="colx", type=int, required=True,
                        help="x-column number (columns start from ONE)")
    parser.add_argument("-ex", dest="colex", type=int,
                        help="x-error column number")
    parser.add_argument("-y", dest="coly", type=int, required=True,
                        help="y-column number (columns start from ONE)")
    parser.add_argument("-ey", dest="coley", type=int,
                        help="y-error column number")
    parser.add_argument("inname", help="input file")
    parser.add_argument("-start", type=int, default=1, help="first line")
    parser.add_argument("-end", type=int,
                        help="last line; read to EOF if omitted")
    parser.add_argument("-o", dest="outname", help="output file name")
    parser.add_argument("-update", action="store_true",
                        help="update the output file instead of recreating it")
    parser.add_argument("-relerr", action="store_true",
                        help="treat symmetric errors as relative")
    parser.add_argument("-name", default="gr", help="graph name")
    parser.add_argument("-title", default="", help="graph title")
    parser.add_argument("-exlow", type=int,
                        help="low x-error column for TGraphAsymmErrors")
    parser.add_argument("-exhigh", type=int,
                        help="high x-error column for TGraphAsymmErrors")
    parser.add_argument("-eylow", type=int,
                        help="low y-error column for TGraphAsymmErrors")
    parser.add_argument("-eyhigh", type=int,
                        help="high y-error column for TGraphAsymmErrors")
    return parser


def _output_name(input_name, output_name):
    if output_name:
        return output_name
    output_name = input_name.replace(".dat", ".root").replace(".txt", ".root")
    return output_name if output_name != input_name else input_name + ".root"


def main():
    args = _parser().parse_args()
    asymm_columns = (args.exlow, args.exhigh, args.eylow, args.eyhigh)
    if any(column is not None for column in asymm_columns) and any(column is None for column in asymm_columns):
        raise SystemExit("all of -exlow, -exhigh, -eylow, and -eyhigh are required together")
    if args.start < 1 or (args.end is not None and args.end < args.start):
        raise SystemExit("invalid line range")

    fname_out = _output_name(args.inname, args.outname)
    print(args.inname, "=>", fname_out)
    fout = ROOT.TFile(fname_out, "update" if args.update else "recreate")
    if fout.IsZombie():
        raise OSError("failed to open output file %s" % fname_out)

    if args.eylow is None:
        graphs = GetGraphs(args.colx, args.colex, args.coly, args.coley,
                           args.inname, args.start, args.end, args.name,
                           args.title, args.relerr)
    else:
        graphs = GetAsymmGraphs(args.colx, args.exlow, args.exhigh,
                                args.coly, args.eylow, args.eyhigh,
                                args.inname, args.start, args.end, args.name)
    graphs.Write()
    fout.ls()
    fout.Close()


if __name__ == "__main__":
    sys.exit(main())
