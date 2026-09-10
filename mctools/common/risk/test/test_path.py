import unittest

import numpy as np
import ROOT

from mctools.common.risk.limits import PathLimit3D, OrthogonalPathLimit3D


class TestPath(unittest.TestCase):
    def test_orthogonal_path_3d_initialization(self):
        with self.assertRaisesRegex(ValueError, "A path must have at least two"):
            OrthogonalPathLimit3D(
                x=np.array([0.0]), y=np.array([0.0]), z=np.array([0.0])
            )
        with self.assertRaisesRegex(ValueError, "All input arrays must have the "):
            OrthogonalPathLimit3D(
                x=np.array([0.0, 1.0]),
                y=np.array([0.0, 1.0]),
                z=np.array([0.0, 1.0, 2.0]),
            )
        with self.assertRaisesRegex(ValueError, "All input arrays must be one-"):
            OrthogonalPathLimit3D(
                x=np.array([[0.0, 1.0], [0.0, 1.0]]),
                y=np.array([0.0, 1.0]),
                z=np.array([0.0, 1.0]),
            )

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

        x = np.array([0.0, 1.0, 2.0, 1.7, 2.0])
        y = np.array([0.0, 0.1, -0.1, 1.1, 1.0])
        z = np.array([0.0, 0.2, 0.3, 0.4, -3.0])
        opl = OrthogonalPathLimit3D(x=x, y=y, z=z)
        self.assertEqual(opl.step_axis, [0, 0, 1, 2])
        self.assertTrue(all(opl.xyz[:, 0] == np.array([0.0, 1.0, 2.0, 2.0, 2.0])))
        self.assertTrue(all(opl.xyz[:, 1] == np.array([0.0, 0.0, 0.0, 1.1, 1.1])))
        self.assertTrue(all(opl.xyz[:, 2] == np.array([0.0, 0.0, 0.0, 0.0, -3.0])))

    def test_orthogonal_path_3d(self):
        hist = ROOT.TH3F("h", "h", 5, -0.25, 0.25, 5, -2.5, 2.5, 5, -25.0, 25.0)
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
                    if (n_x == n_y or n_x == n_y + 1) and n_z == 1:
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
                    if (n_x == n_y or n_x == n_y + 1) and n_z == 1:
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
