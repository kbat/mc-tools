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
from mctools.common.risk.value import Value


@dataclass
class Limits:
    """Limits for a 1D variable"""

    lower: float = float("-inf")
    upper: float = float("inf")

    def __post_init__(self):
        if self.upper < self.lower:
            warn(
                "Given lower limit is larger than upper limit."
                "Assigning Limits.lower = upper and Limits.upper = lower."
            )
            self.lower, self.upper = self.upper, self.lower


class Limits3D(ABC):
    """Abstract base class for constraints that restrict which bins of a TH3
    histogram are searched for the maximum value

    If inverted is True, a bin is in range if it lies outside the limits instead of
    inside them.
    """

    def __init__(self, inverted: bool = False):
        self.inverted = inverted

    @abstractmethod
    def _bin_in_range(
        self, n_x: int, n_y: int, n_z: int, hist: "ROOT.TH3F | ROOT.TH3D"
    ) -> bool:
        """Return True if bin (n_x, n_y, n_z) of hist lies within these limits,
        ignoring the inverted option"""

    def bin_in_range(
        self, n_x: int, n_y: int, n_z: int, hist: "ROOT.TH3F | ROOT.TH3D"
    ) -> bool:
        """Return True if bin (n_x, n_y, n_z) of hist lies within these limits,
        applying the inverted option"""
        return self._bin_in_range(n_x, n_y, n_z, hist) != self.inverted

    def bin_in_x_range(self, n_x: int, hist) -> bool:
        raise NotImplementedError()

    def bin_in_y_range(self, n_y: int, hist) -> bool:
        raise NotImplementedError()

    def bin_in_z_range(self, n_z: int, hist) -> bool:
        raise NotImplementedError()


class BoxLimits3D(Limits3D):
    """Box limits for a 3D variable

    If inverted is True, a bin is in range if it lies outside the box instead of
    inside it.
    """

    def __init__(
        self,
        xlim: Limits | None = None,
        ylim: Limits | None = None,
        zlim: Limits | None = None,
        inverted: bool = False,
    ):
        super().__init__(inverted=inverted)
        self.xlim = Limits() if xlim is None else xlim
        self.ylim = Limits() if ylim is None else ylim
        self.zlim = Limits() if zlim is None else zlim

    def _bin_in_range(self, n_x: int, n_y: int, n_z: int, hist) -> bool:
        return (
            self.bin_in_x_range(n_x, hist)
            and self.bin_in_y_range(n_y, hist)
            and self.bin_in_z_range(n_z, hist)
        )

    def bin_in_x_range(self, n_x: int, hist) -> bool:
        """Return True if bin n_x lies within xlim, ignoring the inverted option"""
        x_axis = hist.GetXaxis()
        return self.xlim.upper >= x_axis.GetBinLowEdge(
            n_x
        ) and self.xlim.lower <= x_axis.GetBinUpEdge(n_x)

    def bin_in_y_range(self, n_y: int, hist) -> bool:
        """Return True if bin n_y lies within ylim, ignoring the inverted option"""
        y_axis = hist.GetYaxis()
        return self.ylim.upper >= y_axis.GetBinLowEdge(
            n_y
        ) and self.ylim.lower <= y_axis.GetBinUpEdge(n_y)

    def bin_in_z_range(self, n_z: int, hist) -> bool:
        """Return True if bin n_z lies within zlim, ignoring the inverted option"""
        z_axis = hist.GetZaxis()
        return self.zlim.upper >= z_axis.GetBinLowEdge(
            n_z
        ) and self.zlim.lower <= z_axis.GetBinUpEdge(n_z)


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
        lim: Limits3D | list[Limits3D] | None = None,
        name: str = "",
        title: str = "",
    ):
        super().__init__(name=name, title=title)
        self.hist = hist
        if lim is None:
            self.lim: list[Limits3D] = [BoxLimits3D()]
        elif isinstance(lim, Limits3D):
            self.lim = [lim]
        else:
            self.lim = lim

    def evaluate(self, root_input_cache=None):
        """Find the maximum value in the (constrained) TH3"""

        if isinstance(self.hist, ROOTFileInput):
            if root_input_cache is None:
                with ROOTInputCache() as root_input_cache:
                    hist = root_input_cache.get_histogram(self.hist)
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

    def set_sub_level_paths(self, path_prefix="", separator="."):
        pass
