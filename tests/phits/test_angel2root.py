"""Regression tests for the PHITS ANGEL-output converter.

The PHITS installation is treated as a read-only test-data directory.  Each
input is copied into pytest's temporary directory because ``angel2root``
writes its output beside the input file.
"""

import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

ROOT = pytest.importorskip("ROOT")


PHITS_ROOT = Path(os.environ.get("PHITSPATH", ""))
CONVERTER = Path(os.environ.get("MCTOOLS", "")) / "mctools/phits/angel2root.py"


def phits_tally_outputs():
    """Return ANGEL tally outputs from the PHITS installation.

    The command supplied with PHITS also finds non-tally ``.out`` files and
    Git-LFS pointer files.  ANGEL tally files have both a tally header and an
    ANGEL page containing ``newpage:`` and a histogram section.
    """
    if not PHITS_ROOT.is_dir():
        return []

    outputs = []
    for path in sorted(PHITS_ROOT.rglob("*.out")):
        if path.name in {"batch.out", "phits.out"}:
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        if "version https://git-lfs.github.com/spec/v1" in text[:200]:
            continue
        if not re.search(r"^\s*\[\s*T[- ]", text, re.MULTILINE | re.IGNORECASE):
            continue
        if not re.search(r"newpage:", text, re.IGNORECASE):
            continue
        if not re.search(r"^\s*h(?:[2dc]|c2?)?:", text, re.MULTILINE | re.IGNORECASE):
            continue
        outputs.append(path)
    return outputs


def run_converter(source, workdir):
    """Copy *source* into *workdir* and convert the copy."""
    input_path = workdir / source.name
    shutil.copyfile(source, input_path)
    try:
        result = subprocess.run(
            [sys.executable, str(CONVERTER), str(input_path)],
            cwd=workdir,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess(
            args=error.cmd,
            returncode=None,
            stdout=error.stdout or "",
            stderr="converter timed out after 120 seconds",
        )
    return result, input_path.with_suffix(".root")


def root_objects(root_path):
    root_file = ROOT.TFile.Open(str(root_path))
    assert root_file and not root_file.IsZombie(), root_path
    objects = [key.ReadObj() for key in root_file.GetListOfKeys()]
    # Return stable metadata rather than PyROOT proxies owned by the file.
    metadata = [
        {
            "class": obj.ClassName(),
            "is_histogram": bool(obj.InheritsFrom("TH1")),
            "is_th2": bool(obj.InheritsFrom("TH2")),
            "nbins": tuple(
                getattr(obj, method)() for method in ("GetNbinsX", "GetNbinsY")
                if hasattr(obj, method)
            ),
        }
        for obj in objects
    ]
    root_file.Close()
    return metadata


def is_ignored_gshow_tally(source):
    """Return whether an ANGEL output contains a geometry-only gshow page."""
    try:
        return bool(re.search(r"^\s*#?\s*gshow\s*$|^\s*gshow\s*=\s*[1-9]",
                              source.read_text(errors="replace"),
                              re.MULTILINE | re.IGNORECASE))
    except OSError:
        return False


def test_bench_transmission_is_one_two_dimensional_histogram(tmp_path):
    source = Path(__file__).with_name("bench_phits_trans.out")
    result, root_path = run_converter(source, tmp_path)

    assert result.returncode == 0, result.stderr
    objects = root_objects(root_path)
    assert len(objects) == 1
    histogram = objects[0]
    assert histogram["is_th2"]
    assert histogram["nbins"] == (200, 45)


def test_phits_tally_outputs_convert_to_root(tmp_path):
    """Smoke-test every available PHITS ANGEL tally output.

    This checks that each output is a valid ROOT file containing at least one
    ROOT object.  ANGEL output can contain histograms, graphs, or other ROOT
    objects; histogram-only output is asserted by the focused tests above.
    """
    sources = phits_tally_outputs()
    if not sources:
        pytest.skip("PHITS tally outputs are not available")

    failures = []
    limit = os.environ.get("PHITS_TEST_LIMIT")
    if limit:
        sources = sources[: int(limit)]

    case_dirs = []
    for case_number, source in enumerate(sources):
        case_dir = tmp_path / str(case_number)
        case_dir.mkdir()
        case_dirs.append((source, case_dir))

    workers = int(os.environ.get("PHITS_TEST_WORKERS", str(os.cpu_count() or 1)))
    workers = max(1, min(workers, len(case_dirs)))
    # Conversion is performed in subprocesses, so parallel workers do not
    # share PyROOT state.  ROOT inspection remains serial below.
    with ThreadPoolExecutor(max_workers=workers) as executor:
        converted = list(
            executor.map(lambda case: run_converter(*case), case_dirs)
        )

    for (source, _), (result, root_path) in zip(case_dirs, converted):
        if result.returncode != 0:
            failures.append(f"{source}: exit {result.returncode}\n{result.stderr}")
            continue
        try:
            objects = root_objects(root_path)
            if not objects and not is_ignored_gshow_tally(source):
                failures.append(f"{source}: no ROOT objects")
        except Exception as error:  # report all bad files in one test run
            failures.append(f"{source}: {error}")

    assert not failures, "\n\n".join(failures)
