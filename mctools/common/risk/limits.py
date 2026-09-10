"""Limits for selecting subsets of all histogram bins"""

from abc import ABC, abstractmethod

from dataclasses import dataclass
from warnings import warn

import numpy as np
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
        """Initialization

        Parameters
        ----------
        inverted: bool
            Determines whether the limits or their inverse will be applied.
            Default: False, i.e. do not invert the limits.
        """
        self.inverted = inverted

    @abstractmethod
    def _bin_in_range(
        self, n_x: int, n_y: int, n_z: int, hist: "ROOT.TH3F | ROOT.TH3D"
    ) -> bool:
        """Test whether a bin lies within the given limits.

        This function ignores the inverted parameter of Limits3D.

        Parameters
        ----------
        n_x: int
            Number of the bin on the x axis between 1 and hist.GetXaxis().GetNbins().
        n_y: int
            Number of the bin on the y axis between 1 and hist.GetYaxis().GetNbins().
        n_z: int
            Number of the bin on the z axis between 1 and hist.GetZaxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Returns
        -------
        bool
            True, if bin (n_x, n_y, n_z) lies within the given limits. False otherwise.
        """

    def bin_in_range(
        self, n_x: int, n_y: int, n_z: int, hist: "ROOT.TH3F | ROOT.TH3D"
    ) -> bool:
        """Test whether a bin lies within the given limits.

        The limits can be inverted using a parameter of Limits3D.

        Parameters
        ----------
        n_x: int
            Number of the bin on the x axis between 1 and hist.GetXaxis().GetNbins().
        n_y: int
            Number of the bin on the y axis between 1 and hist.GetYaxis().GetNbins().
        n_z: int
            Number of the bin on the z axis between 1 and hist.GetZaxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Returns
        -------
        bool
            If not inverted: True, if bin (n_x, n_y, n_z) lies within the given limits.
            False otherwise.
            If inverted: False, if bin (n_x, n_y, n_z) lies within the given limits.
            True otherwise.
        """
        return self._bin_in_range(n_x, n_y, n_z, hist) != self.inverted

    def bin_in_x_range(self, n_x: int, hist) -> bool:
        """Test whether a bin lies within the given limits imposed on the x axis

        This function is intended for cases where the independence of x can be
        exploited.

        Parameters
        ----------
        n_x: int
            Number of the bin on the x axis between 1 and hist.GetXaxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Raises
        ------
        NotImplementedError
        """
        raise NotImplementedError()

    def bin_in_y_range(self, n_y: int, hist) -> bool:
        """Test whether a bin lies within the given limits imposed on the y axis

        This function is intended for cases where the independence of y can be
        exploited.

        Parameters
        ----------
        n_y: int
            Number of the bin on the y axis between 1 and hist.GetYAxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Raises
        ------
        NotImplemtedError
        """
        raise NotImplementedError()

    def bin_in_z_range(self, n_z: int, hist) -> bool:
        """Test whether a bin lies within the given limits imposed on the z axis

        This function is intended for cases where the independence of z can be
        exploited.

        Parameters
        ----------
        n_z: int
            Number of the bin on the z axis between 1 and hist.GetZAxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Raises
        ------
        NotImplemtedError
        """
        raise NotImplementedError()


class CombinedLimits3D:
    """Container class for multiple limits

    Supports iteration, access with square brackets, and comparison.
    """

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


class PathLimit3D(Limits3D):
    def __init__(
        self, x: np.ndarray, y: np.ndarray, z: np.ndarray, inverted: bool = False
    ):
        super().__init__(inverted=inverted)
        self.n_points = len(x)
        if self.n_points < 2:
            raise ValueError("A path must have at least two points.")
        if len(np.shape(x)) != 1 or len(np.shape(y)) != 1 or len(np.shape(z)) != 1:
            raise ValueError(
                "All input arrays must be one-dimensional (numpy.shape() == (N,).)"
            )
        if len(y) != self.n_points or len(z) != self.n_points:
            raise ValueError("All input arrays must have the same number of points.")
        self.xyz = np.transpose(np.array([x, y, z]))
        self.xyz_min = np.min(self.xyz, axis=0)
        self.xyz_max = np.max(self.xyz, axis=0)

    def _bin_in_range(
        self, n_x: int, n_y: int, n_z: int, hist: "ROOT.TH3F | ROOT.TH3D"
    ) -> bool:
        rmin = np.array(
            [
                hist.GetXaxis().GetBinLowEdge(n_x),
                hist.GetYaxis().GetBinLowEdge(n_y),
                hist.GetZaxis().GetBinLowEdge(n_z),
            ]
        )
        rmax = np.array(
            [
                hist.GetXaxis().GetBinUpEdge(n_x),
                hist.GetYaxis().GetBinUpEdge(n_y),
                hist.GetZaxis().GetBinUpEdge(n_z),
            ]
        )
        if all(rmin <= self.xyz_max) and all(rmax >= self.xyz_min):
            for n in range(self.n_points - 1):
                if self.bin_on_connection(
                    p0=self.xyz[n],
                    p1=self.xyz[n + 1],
                    rmin=rmin,
                    rmax=rmax,
                ):
                    return True
        return False

    @staticmethod
    def bin_on_connection(
        p0: np.ndarray,
        p1: np.ndarray,
        rmin: np.ndarray,
        rmax: np.ndarray,
    ) -> bool:
        tmin, tmax = 0.0, 1.0
        d = p1 - p0
        for i in range(3):
            if d[i] != 0.0:
                t1 = (rmin[i] - p0[i]) / d[i]
                t2 = (rmax[i] - p0[i]) / d[i]
                if t1 > t2:
                    t1, t2 = t2, t1
                tmin = max(tmin, t1)
                tmax = min(tmax, t2)
                if tmin > tmax:
                    return False
            else:
                if p0[i] < rmin[i] or p0[i] > rmax[i]:
                    return False

        return True


class OrthogonalPathLimit3D(PathLimit3D):
    def __init__(
        self, x: np.ndarray, y: np.ndarray, z: np.ndarray, inverted: bool = False
    ):
        super().__init__(x=x, y=y, z=z, inverted=inverted)
        self.step_axis = self.orthogonalize()

    def orthogonalize(self) -> list[int]:
        step_axis = [0] * (self.n_points - 1)
        for n in range(self.n_points - 1):
            d = np.abs(self.xyz[n + 1] - self.xyz[n])
            step_ax = np.argmax(d)
            step_axis[n] = step_ax
            for axis in range(3):
                if axis != step_ax:
                    self.xyz[n + 1][axis] = self.xyz[n][axis]

        return step_axis

    def _bin_in_range(self, n_x, n_y, n_z, hist):
        rmin = np.array(
            [
                hist.GetXaxis().GetBinLowEdge(n_x),
                hist.GetYaxis().GetBinLowEdge(n_y),
                hist.GetZaxis().GetBinLowEdge(n_z),
            ]
        )
        rmax = np.array(
            [
                hist.GetXaxis().GetBinUpEdge(n_x),
                hist.GetYaxis().GetBinUpEdge(n_y),
                hist.GetZaxis().GetBinUpEdge(n_z),
            ]
        )
        if all(rmin <= self.xyz_max) and all(rmax >= self.xyz_min):
            for n in range(self.n_points - 1):
                bin_on_connection = True
                for axis in range(3):
                    if axis == self.step_axis[n]:
                        pmin = min(self.xyz[n][axis], self.xyz[n + 1][axis])
                        pmax = max(self.xyz[n][axis], self.xyz[n + 1][axis])
                        if rmin[axis] > pmax or rmax[axis] < pmin:
                            bin_on_connection = False
                            break
                    elif not (rmin[axis] <= self.xyz[n][axis] <= rmax[axis]):
                        bin_on_connection = False
                        break
                if bin_on_connection:
                    return True
        return False
