"""BaseLevel associated with a ROOT TH3 histogram"""

from pathlib import Path
from dataclasses import dataclass
from uuid import uuid4
from warnings import warn

import ROOT

from mctools.common.risk.level import BaseLevel
from mctools.common.risk.value import Value


class Limits:
    """Limits for a 1D variable"""

    def __init__(self, lower: float = float("-inf"), upper: float = float("inf")):
        if upper < lower:
            warn(
                "Given lower limit is larger than upper limit."
                "Assigning Limits.lower = upper and Limits.upper = lower."
            )
            self.lower = upper
            self.upper = lower
        else:
            self.lower = lower
            self.upper = upper


class Limits3D:
    """Box limits for a 3D variable"""

    def __init__(
        self, xlim: Limits = Limits(), ylim: Limits = Limits(), zlim: Limits = Limits()
    ):
        self.xlim = xlim
        self.ylim = ylim
        self.zlim = zlim


@dataclass
class ROOTFileInput:
    root_file_name: Path
    histogram_name: str
    scale_file_name: Path


class ROOTInputCache:
    def __init__(self):
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
            if not Path(root_file_name).is_file():
                raise FileNotFoundError(f"Could not open ROOT file '{root_file_name}'.")
            try:
                root_file = ROOT.TFile.Open(root_file_name)
            except OSError as exc:
                raise FileNotFoundError(
                    f"Could not open ROOT file '{root_file_name}'."
                ) from exc
            if root_file is None or not root_file or root_file.IsZombie():
                if root_file:
                    root_file.Close()
                raise FileNotFoundError(f"Could not open ROOT file '{root_file_name}'.")
            self.root_files[root_file_name] = root_file
        return self.root_files[root_file_name]

    def _get_scale(self, scale_file_name: str) -> float:
        if scale_file_name not in self.scales:
            try:
                scale_file = open(scale_file_name, encoding="utf-8")
            except FileNotFoundError as exc:
                raise FileNotFoundError(
                    f"Could not open scale file '{scale_file_name}'."
                ) from exc
            except OSError as exc:
                raise OSError(f"Could not read scale file '{scale_file_name}'.") from exc

            with scale_file:
                try:
                    self.scales[scale_file_name] = float(scale_file.readline())
                except ValueError as exc:
                    raise ValueError(
                        f"Could not parse scale factor in '{scale_file_name}'."
                    ) from exc
        return self.scales[scale_file_name]


def bin_in_range(n_bin: int, axis: ROOT.TAxis, limits: Limits) -> bool:
    if limits.upper < axis.GetBinLowEdge(n_bin) or limits.lower > axis.GetBinUpEdge(
        n_bin
    ):
        return False
    return True


class Zone(BaseLevel):
    """BaseLevel associated with a ROOT TH3 histogram

    It is possible to use box constraints to limit the range of bins that are searched
    for the maximum value.
    For each axis individually, a minimum and maximum value can be given.
    If the minimum value is larger than the upper edge of a bin or the maximum value is
    smaller than the lower edge of a bin, the bin is not included in the search.
    """

    def __init__(
        self,
        hist: ROOT.TH3F | ROOT.TH3D | ROOTFileInput | str,
        lim: Limits3D = Limits3D(),
        name: str = "",
        title: str = "",
    ):
        super().__init__(name=name, title=title)
        self.hist = hist
        self.lim = lim

    def evaluate(self, root_input_cache=None):
        """Find the maximum value in the (constrained) TH3"""

        if self.hist is not None:
            if isinstance(self.hist, ROOTFileInput):
                if root_input_cache is None:
                    with ROOTInputCache() as root_input_cache:
                        hist = root_input_cache.get_histogram(self.hist)
                        self._evaluate_histogram(hist)
                    return
                hist = root_input_cache.get_histogram(self.hist)
            else:
                hist = self.hist

            self._evaluate_histogram(hist)
        else:
            raise ValueError(f"Input histogram for Zone '{self.name}' missing.")

    def _evaluate_histogram(self, hist):
        max_val = float("-inf")
        max_err = max_x = max_y = max_z = 0.0
        for n_x in range(hist.GetNbinsX()):
            if bin_in_range(n_bin=n_x + 1, axis=hist.GetXaxis(), limits=self.lim.xlim):
                for n_y in range(hist.GetNbinsY()):
                    if bin_in_range(
                        n_bin=n_y + 1, axis=hist.GetYaxis(), limits=self.lim.ylim
                    ):
                        for n_z in range(hist.GetNbinsZ()):
                            if bin_in_range(
                                n_bin=n_z + 1,
                                axis=hist.GetZaxis(),
                                limits=self.lim.zlim,
                            ):
                                if (
                                    hist.GetBinContent(n_x + 1, n_y + 1, n_z + 1)
                                    > max_val
                                ):
                                    max_val = hist.GetBinContent(
                                        n_x + 1, n_y + 1, n_z + 1
                                    )
                                    max_err = hist.GetBinError(
                                        n_x + 1, n_y + 1, n_z + 1
                                    )
                                    max_x = hist.GetXaxis().GetBinCenter(n_x + 1)
                                    max_y = hist.GetYaxis().GetBinCenter(n_y + 1)
                                    max_z = hist.GetZaxis().GetBinCenter(n_z + 1)
        self.value = Value(
            val=max_val,
            err=max_err,
            x=max_x,
            y=max_y,
            z=max_z,
        )

    def set_sub_level_paths(self, path_prefix="", separator="."):
        pass
