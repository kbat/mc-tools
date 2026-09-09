from abc import ABC, abstractmethod

from dataclasses import dataclass
from warnings import warn

import ROOT


@dataclass
class Limits:
    """Limits for a 1D variable"""

    lower: float = float("-inf")
    upper: float = float("inf")
    variable_name: str = "x"

    def __post_init__(self):
        if self.upper < self.lower:
            warn(
                "Given lower limit is larger than upper limit."
                "Assigning Limits.lower = upper and Limits.upper = lower."
            )
            self.lower, self.upper = self.upper, self.lower

    def __str__(self) -> str:
        if self.lower == float("-inf") and self.upper == float("inf"):
            return ""
        if self.lower == self.upper:
            return f"{self.variable_name} = {self.lower}"
        lower = "" if self.lower == float("-inf") else f"{self.lower} <= "
        upper = "" if self.upper == float("inf") else f" <= {self.upper}"
        return f"{lower}{self.variable_name}{upper}"


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


class CombinedLimits3D:
    def __init__(self, lim: Limits3D | list[Limits3D] | None = None):
        if lim is None:
            self.lim: list[Limits3D] = [BoxLimits3D()]
        elif isinstance(lim, Limits3D):
            self.lim = [lim]
        else:
            self.lim = lim

    def __iter__(self):
        return iter(self.lim)

    def __getitem__(self, index):
        return self.lim[index]

    def __eq__(self, other):
        if not isinstance(other, CombinedLimits3D):
            return NotImplemented
        return self.lim == other.lim

    def __str__(self) -> str:
        result = ""
        for l in self.lim:
            l_str = str(l)
            if l_str != "":
                if result != "":
                    if len(result) >= 4 and result[-4:] != "&&":
                        result += " && "
                result += l_str
        return result


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
        self.xlim.variable_name = "x"
        self.ylim = Limits() if ylim is None else ylim
        self.ylim.variable_name = "y"
        self.zlim = Limits() if zlim is None else zlim
        self.zlim.variable_name = "z"

    def __str__(self) -> str:
        xlim = str(self.xlim)
        ylim = str(self.ylim)
        zlim = str(self.zlim)
        result = xlim
        if xlim != "" and (ylim != "" or zlim != ""):
            result += " && "
        result += ylim
        if zlim != "" and result != "":
            if len(result) >= 4 and result[-4:] != " && ":
                result += " && "
        result += zlim
        if self.inverted:
            return f"!({result})"
        return result

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
