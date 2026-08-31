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
REPOSITORY = Path(__file__).resolve().parents[2]
CONVERTER = REPOSITORY / "mctools/phits/angel2root.py"
FIXTURES = Path(__file__).with_name("fixtures")


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


def is_gshow_only(source):
    """Return whether the output contains gshow drawing but no tally data."""
    try:
        text = source.read_text(errors="replace")
        has_gshow = re.search(
            r"^\s*\[\s*T\s*-\s*Gshow\s*\]|"
            r"^\s*gshow\s*=\s*[1-9]|^\s*#\s*gshow\s*$",
            text, re.MULTILINE | re.IGNORECASE)
        has_data = re.search(r"^\s*h(?:2|c2?|d):", text,
                             re.MULTILINE | re.IGNORECASE)
        # Geometry overlays use ANGEL drawing declarations such as
        # ``h: x ny1,0 ...``.  Ordinary 1D tally sections use ``h:`` too and
        # may contain legitimate plot directives such as ``ny21``.
        has_data = has_data or re.search(
            r"^[ \t]*h:(?![ \t]*x[ \t]+ny\d+[ \t]*,)[ \t]*.+$", text,
            re.MULTILINE | re.IGNORECASE)
        return bool(has_gshow and not has_data)
    except OSError:
        return False


def test_simple_1d_fixture_preserves_values_errors_and_subtitle(tmp_path):
    result, root_path = run_converter(FIXTURES / "simple_1d.angel", tmp_path)

    assert result.returncode == 0, result.stderr
    root_file = ROOT.TFile.Open(str(root_path))
    histogram = root_file.Get("spectrum")
    assert histogram.ClassName() == "TH1F"
    assert histogram.GetNbinsX() == 2
    assert histogram.GetBinContent(1) == pytest.approx(2.0)
    assert histogram.GetBinError(1) == pytest.approx(0.2)
    assert "proton" in histogram.GetTitle()
    root_file.Close()


def test_simple_2d_fixture_has_expected_dimensions(tmp_path):
    result, root_path = run_converter(FIXTURES / "simple_2d.angel", tmp_path)

    assert result.returncode == 0, result.stderr
    objects = root_objects(root_path)
    assert len(objects) == 1
    assert objects[0]["class"] == "TH2F"
    assert objects[0]["nbins"] == (2, 2)


def test_page_series_is_combined_into_2d_histogram(tmp_path):
    result, root_path = run_converter(FIXTURES / "page_series.angel", tmp_path)

    assert result.returncode == 0, result.stderr
    root_file = ROOT.TFile.Open(str(root_path))
    histogram = root_file.Get("angular_proton")
    assert histogram.ClassName() == "TH2F"
    assert (histogram.GetNbinsX(), histogram.GetNbinsY()) == (1, 2)
    assert histogram.GetBinContent(1, 1) == pytest.approx(2.0)
    assert histogram.GetBinContent(1, 2) == pytest.approx(3.0)
    root_file.Close()


def run_text_converter(tmp_path, text, *extra_args):
    source = tmp_path / "input.out"
    source.write_text(text)
    result = subprocess.run(
        [sys.executable, str(CONVERTER), *extra_args, str(source)],
        cwd=tmp_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    return result, source.with_suffix(".root")


def test_missing_page_separator_is_reported_without_traceback(tmp_path):
    result, root_path = run_text_converter(tmp_path, "title = Broken\n")

    assert result.returncode == 1
    assert "no ANGEL 'newpage:' separator found" in result.stderr
    assert "Traceback" not in result.stderr
    assert not root_path.exists()


@pytest.mark.parametrize("value_count", [3, 5])
def test_wrong_2d_data_count_is_reported(tmp_path, value_count):
    text = (FIXTURES / "simple_2d.angel").read_text()
    text = re.sub(r"1\.0 2\.0\n3\.0 4\.0", " ".join(["1.0"] * value_count), text)
    result, root_path = run_text_converter(tmp_path, text)

    assert result.returncode == 1
    assert "2D histogram expected 4 values" in result.stderr
    assert not root_path.exists()


@pytest.mark.parametrize(
    ("replacement", "message"),
    [
        ("", "1D histogram contains no data"),
        ("0.0 1.0 nan 0.1", "non-finite data"),
        ("0.0 1.0 2.0", "expected at least 4 columns"),
    ],
)
def test_invalid_1d_data_is_reported_with_page_context(
        tmp_path, replacement, message):
    text = (FIXTURES / "simple_1d.angel").read_text()
    text = re.sub(r"0\.0 1\.0 2\.0 0\.1\n1\.0 2\.0 4\.0 0\.2",
                  replacement, text)
    result, root_path = run_text_converter(tmp_path, text)

    assert result.returncode == 1
    assert message in result.stderr
    assert "page 1" in result.stderr
    assert not root_path.exists()


def test_truncated_region_mesh_is_reported(tmp_path):
    text = """title = Broken region mesh
mesh = reg
newpage:
"""
    result, root_path = run_text_converter(tmp_path, text)

    assert result.returncode == 1
    assert "missing its 'reg =' declaration" in result.stderr
    assert not root_path.exists()


def test_truncated_multiplier_block_is_reported(tmp_path):
    text = """title = Broken multiplier
multiplier = all
part = proton
newpage:
"""
    result, root_path = run_text_converter(tmp_path, text)

    assert result.returncode == 1
    assert "truncated multiplier block" in result.stderr
    assert not root_path.exists()


def test_multiple_particle_page_series_are_combined_separately(tmp_path):
    text = (FIXTURES / "page_series.angel").read_text() + """
newpage:
ia = 1 part = neutron
x: Energy [MeV]
y: Fluence
h: n x y
0.0 1.0 4.0 0.1

newpage:
ia = 2 part = neutron
x: Energy [MeV]
y: Fluence
h: n x y
0.0 1.0 5.0 0.1
"""
    result, root_path = run_text_converter(tmp_path, text)

    assert result.returncode == 0, result.stderr
    root_file = ROOT.TFile.Open(str(root_path))
    assert root_file.Get("angular_proton").ClassName() == "TH2F"
    assert root_file.Get("angular_neutron").ClassName() == "TH2F"
    root_file.Close()


def test_geometry_only_output_removes_existing_destination(tmp_path):
    output = tmp_path / "custom.root"
    output.write_text("stale")
    text = """title = [ T-Gshow ]
file = geometry.out
newpage:
"""
    result, _ = run_text_converter(tmp_path, text, "--output", str(output))

    assert result.returncode == 0, result.stderr
    assert not output.exists()


def test_custom_output_and_verbose_logging(tmp_path):
    source = FIXTURES / "simple_1d.angel"
    output = tmp_path / "chosen.root"
    result = subprocess.run(
        [sys.executable, str(CONVERTER), "--verbose", "--output", str(output),
         str(source)],
        cwd=tmp_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert "converting" in result.stderr
    assert output.exists()


def test_output_creation_failure_is_reported(tmp_path):
    result = subprocess.run(
        [sys.executable, str(CONVERTER), "--output", str(tmp_path),
         str(FIXTURES / "simple_1d.angel")],
        cwd=tmp_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )

    assert result.returncode == 1
    assert "cannot create ROOT output file" in result.stderr

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
        if is_gshow_only(source):
            if root_path.exists():
                failures.append(f"{source}: gshow-only output created a ROOT file")
            continue
        try:
            if not root_path.exists():
                failures.append(f"{source}: converter did not create a ROOT file")
                continue
            objects = root_objects(root_path)
            if not objects:
                failures.append(f"{source}: no ROOT objects")
        except Exception as error:  # report all bad files in one test run
            failures.append(f"{source}: {error}")

    assert not failures, "\n\n".join(failures)
