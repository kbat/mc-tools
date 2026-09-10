"""Limits for selecting subsets of all histogram bins

This module defines classes that determine whether a given histogram bin is inside or
outside a region.
A bin is defined as inside if any part of it is within the limits, i.e. it does not
need to be fully contained within the limits.

Note that getmax is assuming input from ROOT histograms that have bins aligned with
the canonical x-, y-, and z axes. Bins with arbitrary orientation are not in the scope
of this module.
"""

from abc import ABC, abstractmethod

from dataclasses import dataclass
from warnings import warn

import numpy as np
import ROOT


@dataclass
class Limits:
    """Limits for a 1D variable

    Attributes
    ----------
    lower: float
        Lower limit. Default: -inf, i.e. no lower limit.
    upper: float
        Upper limit. Default: inf, i.e. no upper limit.
    variable_name: str
        Name of the variable used in the string representation of Limits. Default: 'x'.
    """

    lower: float = float("-inf")
    upper: float = float("inf")
    variable_name: str = "x"

    def __post_init__(self):
        """Post Init"""
        if self.upper < self.lower:
            warn(
                "Given lower limit is larger than upper limit."
                "Assigning Limits.lower = upper and Limits.upper = lower."
            )
            self.lower, self.upper = self.upper, self.lower

    def __str__(self) -> str:
        """String representation"""
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

    Attributes
    ----------
    inverted: bool
        Determines whether the limits or their inverse will be applied.
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

    Attributes
    ----------
    lim: list[Limits3D]
        Set of limits.
    """

    def __init__(self, lim: Limits3D | list[Limits3D] | None = None):
        """Initialization

        Parameters
        ----------
        lim: Limits3D | list[Limits3D] | None
            Set of limits. A single Limits3D object will be turned into a list
            with the input as the only element. None as an input will result in
            a list that contains an unlimited BoxLimits3D object.
            Default: None.
        """
        if lim is None:
            self.lim: list[Limits3D] = [BoxLimits3D()]
        elif isinstance(lim, Limits3D):
            self.lim = [lim]
        else:
            self.lim = lim

    def __iter__(self):
        """Iteration"""
        return iter(self.lim)

    def __getitem__(self, index):
        """Item access"""
        return self.lim[index]

    def __eq__(self, other):
        """Test equality"""
        if not isinstance(other, CombinedLimits3D):
            return NotImplemented
        return self.lim == other.lim

    def __str__(self) -> str:
        """String representation

        Prints the set of limits connected by AND (&&) because this is the currently
        intended use.
        """
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

    Independent lower and upper limits for the x-, y-, and z coordinate.

    Attributes
    ----------
    xlim: Limits
        Lower and upper limit for the x coordinate.
    ylim: Limits
        Lower and upper limit for the y coordinate.
    zlim: Limits
        Lower and upper limit for the z coordinate.
    inverted: bool
        Determines whether the limits or their inverse will be applied.
    """

    def __init__(
        self,
        xlim: Limits | None = None,
        ylim: Limits | None = None,
        zlim: Limits | None = None,
        inverted: bool = False,
    ):
        """Initialization

        Parameters
        ----------
        xlim: Limits | None
            Lower and upper limit for the x coordinate. Default: None, i.e. no limits.
        ylim: Limits | None
            Lower and upper limit for the y coordinate. Default: None, i.e. no limits.
        zlim: Limits | None
            Lower and upper limit for the z coordinate. Default: None, i.e. no limits.
        inverted: bool
            Determines whether the limits or their inverse will be applied.
            Default: False, i.e. do not invert the limits.
        """
        super().__init__(inverted=inverted)
        self.xlim = Limits() if xlim is None else xlim
        self.xlim.variable_name = "x"
        self.ylim = Limits() if ylim is None else ylim
        self.ylim.variable_name = "y"
        self.zlim = Limits() if zlim is None else zlim
        self.zlim.variable_name = "z"

    def __str__(self) -> str:
        """String representation"""
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
        """Test whether a bin lies within the given limits.

        Calls the bin-in-range functions for each axis.

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
        return (
            self.bin_in_x_range(n_x, hist)
            and self.bin_in_y_range(n_y, hist)
            and self.bin_in_z_range(n_z, hist)
        )

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

        Returns
        -------
            True, if bin n_x lies within the given limits. False otherwise.
        """
        x_axis = hist.GetXaxis()
        return self.xlim.upper >= x_axis.GetBinLowEdge(
            n_x
        ) and self.xlim.lower <= x_axis.GetBinUpEdge(n_x)

    def bin_in_y_range(self, n_y: int, hist) -> bool:
        """Test whether a bin lies within the given limits imposed on the y axis

        This function is intended for cases where the independence of y can be
        exploited.

        Parameters
        ----------
        n_y: int
            Number of the bin on the y axis between 1 and hist.GetYaxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Returns
        -------
            True, if bin n_y lies within the given limits. False otherwise.
        """
        y_axis = hist.GetYaxis()
        return self.ylim.upper >= y_axis.GetBinLowEdge(
            n_y
        ) and self.ylim.lower <= y_axis.GetBinUpEdge(n_y)

    def bin_in_z_range(self, n_z: int, hist) -> bool:
        """Test whether a bin lies within the given limits imposed on the z axis

        This function is intended for cases where the independence of z can be
        exploited.

        Parameters
        ----------
        n_z: int
            Number of the bin on the z axis between 1 and hist.GetZaxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Returns
        -------
            True, if bin n_z lies within the given limits. False otherwise.
        """
        z_axis = hist.GetZaxis()
        return self.zlim.upper >= z_axis.GetBinLowEdge(
            n_z
        ) and self.zlim.lower <= z_axis.GetBinUpEdge(n_z)


class PathLimit3D(Limits3D):
    """Path limit for a 3D variable

    Determines whether a bin lies on a path determined by a set of 3D points connected
    by straight lines.

    Attributes
    ----------
    n_points: int
        Number of points.
    xyz: (n_points,3) ndarray
        Coordinates of the points.
    xyz_min: (3,) ndarray
        Lower limits of the bounding box of the path.
    xyz_max: (3,) ndarray
        Upper limits of the bounding box of the path.
    """

    def __init__(
        self,
        x: np.ndarray | float,
        y: np.ndarray | float,
        z: np.ndarray | float,
        inverted: bool = False,
    ):
        """Initialization

        Parameters
        ----------
        x: (n_points,) ndarray | float
            x coordinates of the points. If a float is given, it will be assumed that
            the x coordinate is the same for all points on the path.
        y: (n_points,) ndarray | float
            y coordinates of the points. If a float is given, it will be assumed that
            the y coordinate is the same for all points on the path.
        z: (n_points,) ndarray | float
            z coordinates of the points. If a float is given, it will be assumed that
            the z coordinate is the same for all points on the path.
        inverted: bool
            Determines whether the limits or their inverse will be applied.
            Default: False, i.e. do not invert the limits.

        Raises
        ------
        ValueError
            If list input is inconsistent or does not constitute a path.
        """
        super().__init__(inverted=inverted)
        n_float_inputs = 0
        if isinstance(x, float):
            n_float_inputs += 1
            if isinstance(y, np.ndarray):
                x_input: np.ndarray = np.full(np.shape(y), x)
            else:
                raise ValueError(
                    "Only one of x, y, or z can be a float. Otherwise, the path would "
                    "be trivial."
                )
        else:
            x_input = x
        if isinstance(y, float):
            n_float_inputs += 1
            if isinstance(x, np.ndarray):
                y_input: np.ndarray = np.full(np.shape(x), y)
            else:
                raise ValueError(
                    "Only one of x, y, or z can be a float. Otherwise, the path would "
                    "be trivial."
                )
        else:
            y_input = y
        if isinstance(z, float):
            n_float_inputs += 1
            if isinstance(x, np.ndarray):
                z_input: np.ndarray = np.full(np.shape(x), z)
            else:
                raise ValueError(
                    "Only one of x, y, or z can be a float. Otherwise, the path would "
                    "be trivial."
                )
        else:
            z_input = z
        if n_float_inputs > 1:
            raise ValueError(
                "Only one of x, y, or z can be a float. Otherwise, the path would "
                "be trivial."
            )
        self.n_points = len(x_input)
        if self.n_points < 2:
            raise ValueError("A path must have at least two points.")
        if (
            len(np.shape(x_input)) != 1
            or len(np.shape(y_input)) != 1
            or len(np.shape(z_input)) != 1
        ):
            raise ValueError(
                "All input arrays must be one-dimensional (numpy.shape() == (N,).)"
            )
        if len(y_input) != self.n_points or len(z_input) != self.n_points:
            raise ValueError("All input arrays must have the same number of points.")
        self.xyz = np.transpose(np.array([x_input, y_input, z_input]))
        self.xyz_min = np.min(self.xyz, axis=0)
        self.xyz_max = np.max(self.xyz, axis=0)

    def _bin_in_range(
        self, n_x: int, n_y: int, n_z: int, hist: "ROOT.TH3F | ROOT.TH3D"
    ) -> bool:
        """Test whether a bin lies within the given limits.

        Checks first whether the bin is within the bounding box of the path.
        If the bin is within the bounding box, then checks whether any of the
        connecting lines of the path is contained in the bin.

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
        bmin = np.array(
            [
                hist.GetXaxis().GetBinLowEdge(n_x),
                hist.GetYaxis().GetBinLowEdge(n_y),
                hist.GetZaxis().GetBinLowEdge(n_z),
            ]
        )
        bmax = np.array(
            [
                hist.GetXaxis().GetBinUpEdge(n_x),
                hist.GetYaxis().GetBinUpEdge(n_y),
                hist.GetZaxis().GetBinUpEdge(n_z),
            ]
        )
        if all(bmin <= self.xyz_max) and all(bmax >= self.xyz_min):
            for n in range(self.n_points - 1):
                if self.bin_on_connection(
                    p0=self.xyz[n],
                    p1=self.xyz[n + 1],
                    bmin=bmin,
                    bmax=bmax,
                ):
                    return True
        return False

    def bin_in_x_range(self, n_x, hist):
        """Test whether a bin lies within the bounding-box range on the x axis

        This function is intended for preprocessing a histogram.

        Parameters
        ----------
        n_x: int
            Number of the bin on the x axis between 1 and hist.GetXaxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Returns
        -------
            True, if bin n_x lies within the bounding box. False otherwise.
        """
        x_axis = hist.GetXaxis()
        return self.xyz_max[0] >= x_axis.GetBinLowEdge(n_x) and self.xyz_min[
            0
        ] <= x_axis.GetBinUpEdge(n_x)

    def bin_in_y_range(self, n_y, hist):
        """Test whether a bin lies within the bounding-box range on the y axis

        This function is intended for preprocessing a histogram.

        Parameters
        ----------
        n_y: int
            Number of the bin on the y axis between 1 and hist.GetYaxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Returns
        -------
            True, if bin n_y lies within the bounding box. False otherwise.
        """
        y_axis = hist.GetYaxis()
        return self.xyz_max[1] >= y_axis.GetBinLowEdge(n_y) and self.xyz_min[
            1
        ] <= y_axis.GetBinUpEdge(n_y)

    def bin_in_z_range(self, n_z, hist):
        """Test whether a bin lies within the bounding-box range on the z axis

        This function is intended for preprocessing a histogram.

        Parameters
        ----------
        n_z: int
            Number of the bin on the z axis between 1 and hist.GetZaxis().GetNbins().
        hist: ROOT.TH3F or ROOT.TH3D
            ROOT histogram.

        Returns
        -------
            True, if bin n_z lies within the bounding box. False otherwise.
        """
        z_axis = hist.GetZaxis()
        return self.xyz_max[2] >= z_axis.GetBinLowEdge(n_z) and self.xyz_min[
            2
        ] <= z_axis.GetBinUpEdge(n_z)

    @staticmethod
    def bin_on_connection(
        p0: np.ndarray,
        p1: np.ndarray,
        bmin: np.ndarray,
        bmax: np.ndarray,
    ) -> bool:
        """Test whether a bin lies on a connecting line between two points

        Calculates the intersection points of the infinite line with the 6 surfaces of
        the bin and checks whether the intersection points are on the connection.

        Parameters
        ----------
        p0: (3,) ndarray
            Start point of the line.
        p1: (3,) ndarray
            End point of the line.
        bmin: (3,) ndarray
            Lower limits of the bin.
        bmax: (3,) ndarray
            Upper limits of the bin.

        Returns
        -------
        bool
            True, if bin (n_x, n_y, n_z) lies on the connecting line.
            False otherwise.
        """
        tmin, tmax = 0.0, 1.0
        d = p1 - p0
        for i in range(3):
            if d[i] != 0.0:
                t1 = (bmin[i] - p0[i]) / d[i]
                t2 = (bmax[i] - p0[i]) / d[i]
                if t1 > t2:
                    t1, t2 = t2, t1
                tmin = max(tmin, t1)
                tmax = min(tmax, t2)
                if tmin > tmax:
                    return False
            else:
                if p0[i] < bmin[i] or p0[i] > bmax[i]:
                    return False

        return True


class OrthogonalPathLimit3D(PathLimit3D):
    """Orthogonal path limit for a 3D variable

    An orthogonal path consists of connecting lines ('steps') that are parallel to the
    x-, y-, or z axis.

    Attributes
    ----------
    n_points: int
        Number of points.
    xyz: (n_points,3) ndarray
        Coordinates of the points.
    xyz_min: (3,) ndarray
        Lower limits of the bounding box of the path.
    xyz_max: (3,) ndarray
        Upper limits of the bounding box of the path.
    step_axis: list[int] with length n_points-1
        For each step, indicates along which axis the step occurs.
        0 = x, 1 = y, 2 = z.
    """

    def __init__(
        self,
        x: np.ndarray | float,
        y: np.ndarray | float,
        z: np.ndarray | float,
        inverted: bool = False,
    ):
        """Initialization

        The input path will be 'orthogonalized' to be in compliance with the
        assumptions of this class. The orthogonalization proceeds as follows:
        For each pair of points (p0, p1) along the path that define a connecting line,
        determine the step lengths dx, dy, dz along the axes:

            dx = abs(p1[0]-p0[0])
            dy = abs(p1[0]-p0[0])
            dz = abs(p1[0]-p0[0])

        The largest of the step lengths defines the step axis (see step_axis
        attribute). For the remaining two axes, the coordinates of the end point are
        set to the value of the start point:

            p1[i] = p0[i]       where i is not the step axis

        Possible problems with this algorithm are precision issues (a very small step
        may be obscured by rounding errors along another axis).

        Parameters
        ----------
        x: (n_points,) ndarray | float
            x coordinates of the points. If a float is given, it will be assumed that
            the x coordinate is the same for all points on the path.
        y: (n_points,) ndarray | float
            y coordinates of the points. If a float is given, it will be assumed that
            the y coordinate is the same for all points on the path.
        z: (n_points,) ndarray | float
            z coordinates of the points. If a float is given, it will be assumed that
            the z coordinate is the same for all points on the path.
        inverted: bool
            Determines whether the limits or their inverse will be applied.
            Default: False, i.e. do not invert the limits.

        Raises
        ------
        ValueError
            If list input is inconsistent or does not constitute a path.
        """
        super().__init__(x=x, y=y, z=z, inverted=inverted)
        self.step_axis = self.orthogonalize()

    def orthogonalize(self) -> list[int]:
        """Orthogonalize the steps between the points of the path

        Analyzes the step lengths along individual axes to find the step axis for each
        step.
        May shift all points except the first one such that all steps are exactly
        parallel to the step axis.

        Returns
        -------
        step_axis: list[int] with length n_points-1
            For each step, indicates along which axis the step occurs.
            0 = x, 1 = y, 2 = z.
        """
        step_axis = [0] * (self.n_points - 1)
        for n in range(self.n_points - 1):
            d = np.abs(self.xyz[n + 1] - self.xyz[n])
            step_ax = int(np.argmax(d))
            step_axis[n] = step_ax
            for axis in range(3):
                if axis != step_ax:
                    self.xyz[n + 1][axis] = self.xyz[n][axis]

        return step_axis

    def _bin_in_range(
        self, n_x: int, n_y: int, n_z: int, hist: "ROOT.TH3F | ROOT.TH3D"
    ) -> bool:
        """Test whether a bin lies within the given limits.

        Checks first whether the bin is within the bounding box of the path.
        If the bin is within the bounding box, check whether any of the connecting
        lines lies within the bin. For each connecting line, distinguish between
        the step axis and the remaining two axis.

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
                    elif not rmin[axis] <= self.xyz[n][axis] <= rmax[axis]:
                        bin_on_connection = False
                        break
                if bin_on_connection:
                    return True
        return False
