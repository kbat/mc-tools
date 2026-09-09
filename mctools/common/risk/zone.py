"""BaseLevel associated with a ROOT TH3 histogram"""

from abc import ABC, abstractmethod
from collections.abc import Iterable
from itertools import product
from pathlib import Path
from dataclasses import dataclass
from uuid import uuid4
from warnings import warn

import ROOT

from mctools.common.risk.level import BaseLevel
from mctools.common.risk.limits import CombinedLimits3D, Limits3D, BoxLimits3D
from mctools.common.risk.value import Value


@dataclass
class ROOTFileInput:
    root_file_name: Path
    histogram_name: str
    scale_file_name: Path


class ROOTInputCache:
    def __init__(self) -> None:
        self.root_files: dict[str, ROOT.TFile] = {}
        self.scales: dict[str, float] = {}
        self.histograms: dict[tuple[str, str, str], ROOT.TH3F | ROOT.TH3D] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.histograms.clear()
        self.scales.clear()
        for root_file in self.root_files.values():
            root_file.Close()
        self.root_files.clear()

    def get_histogram(self, root_file_input: ROOTFileInput):
        root_file_name = str(root_file_input.root_file_name)
        histogram_name = root_file_input.histogram_name
        scale_file_name = str(root_file_input.scale_file_name)
        key = (root_file_name, histogram_name, scale_file_name)
        if key not in self.histograms:
            hist = self._get_root_file(root_file_name).Get(histogram_name)
            if hist is None or not hist:
                raise KeyError(
                    f"Histogram '{histogram_name}' missing in ROOT file "
                    f"'{root_file_name}'."
                )
            cached_hist = hist.Clone(f"{histogram_name}_{uuid4().hex}")
            cached_hist.SetDirectory(0)
            cached_hist.Scale(self._get_scale(scale_file_name))
            self.histograms[key] = cached_hist
        return self.histograms[key]

    def _get_root_file(self, root_file_name: str):
        if root_file_name not in self.root_files:
            self.root_files[root_file_name] = ROOT.TFile.Open(root_file_name)
        return self.root_files[root_file_name]

    def _get_scale(self, scale_file_name: str) -> float:
        if scale_file_name not in self.scales:
            with open(scale_file_name, encoding="utf-8") as scale_file:
                self.scales[scale_file_name] = float(scale_file.readline())
        return self.scales[scale_file_name]


class Zone(BaseLevel):
    """BaseLevel associated with a ROOT TH3 histogram

    A list of Limits3D instances can be given to restrict the bins that are searched
    for the maximum value to a certain region of the histogram. A bin is only
    included in the search if it is in range of every Limits3D in the list (i.e. the
    limits are combined with a logical AND). By default, a single BoxLimits3D with no
    constraints is used, i.e. the whole histogram is searched.
    """

    def __init__(
        self,
        hist: ROOT.TH3F | ROOT.TH3D | ROOTFileInput | str,
        lim: CombinedLimits3D | Limits3D | list[Limits3D] | None = None,
        name: str = "",
        title: str = "",
    ):
        super().__init__(name=name, title=title)
        self.hist = hist
        if lim is None:
            self.lim: CombinedLimits3D = CombinedLimits3D()
        elif isinstance(lim, Limits3D):
            self.lim = CombinedLimits3D(lim=[lim])
        elif isinstance(lim, list) and all(isinstance(l, Limits3D) for l in lim):
            self.lim = CombinedLimits3D(lim=lim)
        elif isinstance(lim, CombinedLimits3D):
            self.lim = lim
        else:
            raise ValueError("Invalid input for lim.")

    def evaluate(self, root_input_cache=None):
        """Find the maximum value in the (constrained) TH3"""

        if isinstance(self.hist, ROOTFileInput):
            if root_input_cache is None:
                with ROOTInputCache() as cache:
                    hist = cache.get_histogram(self.hist)
                    self._evaluate_histogram(hist)
                return
            hist = root_input_cache.get_histogram(self.hist)
        else:
            hist = self.hist

        if isinstance(self.hist, str):
            raise ValueError(
                "Unable to evaluate Zone because only the name of "
                "the histogram is known. Instead of passing the "
                "histogram as a name, pass the TH3 object or include "
                "the zone in a context like Scenario."
            )
        self._evaluate_histogram(hist)

    def _evaluate_histogram(self, hist: ROOT.TH3F | ROOT.TH3D):
        n_bins_x = hist.GetNbinsX()
        n_bins_y = hist.GetNbinsY()
        n_bins_z = hist.GetNbinsZ()

        # A box constraint that is not inverted restricts each axis independently,
        # so the per-axis bin masks can be precomputed once instead of re-evaluating
        # the full box condition for every (n_x, n_y, n_z) triple. An inverted box
        # constraint excludes bins if any axis is out of range, which is not
        # separable into independent per-axis masks, so it falls back to the
        # general case below.
        if all(isinstance(lim, BoxLimits3D) and not lim.inverted for lim in self.lim):
            bins_x = [
                n_x
                for n_x in range(1, n_bins_x + 1)
                if all(lim.bin_in_x_range(n_x, hist) for lim in self.lim)
            ]
            bins_y = [
                n_y
                for n_y in range(1, n_bins_y + 1)
                if all(lim.bin_in_y_range(n_y, hist) for lim in self.lim)
            ]
            bins_z = [
                n_z
                for n_z in range(1, n_bins_z + 1)
                if all(lim.bin_in_z_range(n_z, hist) for lim in self.lim)
            ]
            bin_indices: Iterable[tuple[int, int, int]] = product(
                bins_x, bins_y, bins_z
            )
        else:
            bin_indices = (
                (n_x, n_y, n_z)
                for n_x in range(1, n_bins_x + 1)
                for n_y in range(1, n_bins_y + 1)
                for n_z in range(1, n_bins_z + 1)
                if all(lim.bin_in_range(n_x, n_y, n_z, hist) for lim in self.lim)
            )

        max_val = float("-inf")
        max_err = max_x = max_y = max_z = 0.0
        for n_x, n_y, n_z in bin_indices:
            bin_content = hist.GetBinContent(n_x, n_y, n_z)
            if bin_content > max_val:
                max_val = bin_content
                max_err = hist.GetBinError(n_x, n_y, n_z)
                max_x = hist.GetXaxis().GetBinCenter(n_x)
                max_y = hist.GetYaxis().GetBinCenter(n_y)
                max_z = hist.GetZaxis().GetBinCenter(n_z)
        self.value = Value(
            val=max_val,
            err=max_err,
            x=max_x,
            y=max_y,
            z=max_z,
        )

    def set_sub_level_paths(self, separator="."):
        pass
