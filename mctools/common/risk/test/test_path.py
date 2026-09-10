import unittest

import numpy as np
import ROOT

from mctools.common.risk.limits import PathLimit3D, OrthogonalPathLimit3D


class TestPath(unittest.TestCase):
    def test_path_limit_3d_initialization(self):
        # Error: Path must have at least 2 points.
        with self.assertRaisesRegex(ValueError, "A path must have at least two"):
            PathLimit3D(x=np.array([0.0]), y=np.array([0.0]), z=np.array([0.0]))
        # Error: Inconsistent input.
        with self.assertRaisesRegex(ValueError, "All input arrays must have the "):
            PathLimit3D(
                x=np.array([0.0, 1.0]),
                y=np.array([0.0, 1.0]),
                z=np.array([0.0, 1.0, 2.0]),
            )
        # Error: Only 1D lists as input.
        with self.assertRaisesRegex(ValueError, "All input arrays must be one-"):
            PathLimit3D(
                x=np.array([[0.0, 1.0], [0.0, 1.0]]),
                y=np.array([0.0, 1.0]),
                z=np.array([0.0, 1.0]),
            )
        # Error: More than one variable passed as a single float
        with self.assertRaisesRegex(ValueError, "Only one of x, y, or z"):
            PathLimit3D(
                x=np.array([0.0, 1.0]),
                y=0.0,
                z=0.0,
            )
        with self.assertRaisesRegex(ValueError, "Only one of x, y, or z"):
            PathLimit3D(
                x=0.0,
                y=np.array([0.0, 1.0]),
                z=0.0,
            )
        with self.assertRaisesRegex(ValueError, "Only one of x, y, or z"):
            PathLimit3D(
                x=0.0,
                y=0.0,
                z=np.array([0.0, 1.0]),
            )
        with self.assertRaisesRegex(ValueError, "Only one of x, y, or z"):
            PathLimit3D(
                x=0.0,
                y=0.0,
                z=0.0,
            )
        # Initialization with a single variable as float.
        pl = PathLimit3D(
            x=np.array([0.0, 1.0]),
            y=np.array([0.0, 1.0]),
            z=3.0,
        )
        self.assertEqual(pl.xyz[0][2], 3.0)
        self.assertEqual(pl.xyz[1][2], 3.0)

    def test_orthogonal_path_limit_3d_initialization(self):
        # Test whether the attributes are initialized correctly.
        # Since OrthogonalPathLimit3D calls the base-class constructor, this also tests
        # PathLimit3D.__init__().
        x = np.array([0.0, 1.0, 2.0, 2.0, 2.0])
        y = np.array([0.0, 0.0, 0.0, 1.0, 1.0])
        z = np.array([0.0, 0.0, 0.0, 0.0, 3.0])
        opl = OrthogonalPathLimit3D(x=x, y=y, z=z)
        self.assertEqual(opl.n_points, 5)
        self.assertEqual(opl.step_axis, [0, 0, 1, 2])
        xyz_max = [2.0, 1.0, 3.0]
        for i in range(3):
            self.assertEqual(opl.xyz_min[i], 0.0)
            self.assertEqual(opl.xyz_max[i], xyz_max[i])
        self.assertTrue(all(opl.xyz[:, 0] == x))
        self.assertTrue(all(opl.xyz[:, 1] == y))
        self.assertTrue(all(opl.xyz[:, 2] == z))

        # Test orthogonalization
        x = np.array([0.0, 1.0, 2.0, 1.7, 2.0])
        y = np.array([0.0, 0.1, -0.1, 1.1, 1.0])
        z = np.array([0.0, 0.2, 0.3, 0.4, -3.0])
        opl = OrthogonalPathLimit3D(x=x, y=y, z=z)
        self.assertEqual(opl.step_axis, [0, 0, 1, 2])
        self.assertTrue(all(opl.xyz[:, 0] == np.array([0.0, 1.0, 2.0, 2.0, 2.0])))
        self.assertTrue(all(opl.xyz[:, 1] == np.array([0.0, 0.0, 0.0, 1.1, 1.1])))
        self.assertTrue(all(opl.xyz[:, 2] == np.array([0.0, 0.0, 0.0, 0.0, -3.0])))

    def test_path_limit_3d(self):
        # Dimensions of the bin.
        bmin = [-1.0, -1.0, -1.0]
        bmax = [1.0, 1.0, 1.0]

        # Both points outside bin
        self.assertTrue(
            PathLimit3D.bin_on_connection(
                np.array([0.0, 0.0, -2.0]),
                np.array([0.0, 0.0, 2.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # Start point inside
        self.assertTrue(
            PathLimit3D.bin_on_connection(
                np.array([0.0, 0.0, 0.0]),
                np.array([0.0, 0.0, 2.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # End point inside
        self.assertTrue(
            PathLimit3D.bin_on_connection(
                np.array([0.0, 0.0, -2.0]),
                np.array([0.0, 0.0, 0.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # Start point = end point, inside
        self.assertTrue(
            PathLimit3D.bin_on_connection(
                np.array([0.0, 0.0, 0.0]),
                np.array([0.0, 0.0, 0.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # Start point = end point, outside
        self.assertFalse(
            PathLimit3D.bin_on_connection(
                np.array([0.0, 0.0, 3.0]),
                np.array([0.0, 0.0, 3.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # No intersection
        self.assertFalse(
            PathLimit3D.bin_on_connection(
                np.array([3.0, 0.0, 0.0]),
                np.array([0.0, 0.0, 3.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # Connecting line on edge
        self.assertTrue(
            PathLimit3D.bin_on_connection(
                np.array([1.0, 1.0, -2.0]),
                np.array([1.0, 1.0, 2.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # Connecting line slightly outside
        almost_on_edge = 1.0 + 1e-10
        self.assertFalse(
            PathLimit3D.bin_on_connection(
                np.array([almost_on_edge, almost_on_edge, -2.0]),
                np.array([almost_on_edge, almost_on_edge, 2.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # Start point on surface
        self.assertTrue(
            PathLimit3D.bin_on_connection(
                np.array([1.0, 0.0, 0.0]),
                np.array([3.0, 0.0, 0.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )
        # End point on surface
        self.assertTrue(
            PathLimit3D.bin_on_connection(
                np.array([3.0, 0.0, 0.0]),
                np.array([1.0, 0.0, 0.0]),
                bmin=bmin,
                bmax=bmax,
            )
        )

    def test_orthogonal_path_limit_3d(self):
        # 5 x 5 x 5 - bin sample histogram with regular binning, but different bin
        # sizes on each axis.
        hist = ROOT.TH3F("h", "h", 5, -0.25, 0.25, 5, -2.5, 2.5, 5, -25.0, 25.0)
        # Test path that runs first along the x = y line on the lowest z plane
        # (step along x, then step along y), then along
        # the z axis to the central bin, then along the x axis to the central bin, and
        # lastly along the y axis to the central bin.
        opl = OrthogonalPathLimit3D(
            x=np.array([-0.2, -0.1, -0.1, 0.0, 0.0, 0.1, 0.1, 0.2, 0.2, 0.2, 0.0, 0.0]),
            y=np.array(
                [-2.0, -2.0, -1.0, -1.0, 0.0, 0.0, 1.0, 1.0, 2.0, 2.0, 2.0, 0.0]
            ),
            z=np.array(
                [
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    0.0,
                    0.0,
                    0.0,
                ]
            ),
        )
        for n_x in range(1, 6):
            for n_y in range(1, 6):
                for n_z in range(1, 6):
                    if n_x in (n_y, n_y + 1) and n_z == 1:
                        self.assertTrue(
                            opl.bin_in_range(n_x=n_x, n_y=n_y, n_z=n_z, hist=hist)
                        )
                    elif n_x == n_y == 5 and n_z < 4:
                        self.assertTrue(
                            opl.bin_in_range(n_x=5, n_y=5, n_z=n_z, hist=hist)
                        )
                    elif n_z == 3 and n_y == 5 and n_x > 2:
                        self.assertTrue(
                            opl.bin_in_range(n_x=n_x, n_y=5, n_z=3, hist=hist)
                        )
                    elif n_z == 3 and n_x == 3 and n_y > 2:
                        self.assertTrue(
                            opl.bin_in_range(n_x=3, n_y=n_y, n_z=3, hist=hist)
                        )
                    else:
                        self.assertFalse(
                            opl.bin_in_range(n_x=n_x, n_y=n_y, n_z=n_z, hist=hist)
                        )

        pl = PathLimit3D(
            x=np.array([-0.2, -0.1, -0.1, 0.0, 0.0, 0.1, 0.1, 0.2, 0.2, 0.2, 0.0, 0.0]),
            y=np.array(
                [-2.0, -2.0, -1.0, -1.0, 0.0, 0.0, 1.0, 1.0, 2.0, 2.0, 2.0, 0.0]
            ),
            z=np.array(
                [
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    -20.0,
                    0.0,
                    0.0,
                    0.0,
                ]
            ),
        )
        for n_x in range(1, 6):
            for n_y in range(1, 6):
                for n_z in range(1, 6):
                    if n_x in (n_y, n_y + 1) and n_z == 1:
                        self.assertTrue(
                            pl.bin_in_range(n_x=n_x, n_y=n_y, n_z=n_z, hist=hist)
                        )
                    elif n_x == n_y == 5 and n_z < 4:
                        self.assertTrue(
                            pl.bin_in_range(n_x=5, n_y=5, n_z=n_z, hist=hist)
                        )
                    elif n_z == 3 and n_y == 5 and n_x > 2:
                        self.assertTrue(
                            pl.bin_in_range(n_x=n_x, n_y=5, n_z=3, hist=hist)
                        )
                    elif n_z == 3 and n_x == 3 and n_y > 2:
                        self.assertTrue(
                            pl.bin_in_range(n_x=3, n_y=n_y, n_z=3, hist=hist)
                        )
                    else:
                        self.assertFalse(
                            pl.bin_in_range(n_x=n_x, n_y=n_y, n_z=n_z, hist=hist)
                        )
