"""BaseLevel associated with a ROOT TH3 histogram"""

from pathlib import Path
from dataclasses import dataclass
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

    def evaluate(self):
        """Find the maximum value in the (constrained) TH3"""

        if self.hist is not None:
            if isinstance(self.hist, ROOTFileInput):
                tfile = ROOT.TFile(str(self.hist.root_file_name))
                hist = tfile.Get(self.hist.histogram_name)
                with open(self.hist.scale_file_name, encoding="utf-8") as scale_file:
                    scale = float(scale_file.readline())
                hist.Scale(scale)
            else:
                hist = self.hist

            max_val = float("-inf")
            max_err = max_x = max_y = max_z = 0.0
            for n_x in range(hist.GetNbinsX()):
                if bin_in_range(
                    n_bin=n_x + 1, axis=hist.GetXaxis(), limits=self.lim.xlim
                ):
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
        else:
            raise (ValueError(f"Input histogram for Zone '{self.name}' missing."))

    def set_sub_level_paths(self, path_prefix="", separator="."):
        pass
