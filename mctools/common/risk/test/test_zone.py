import unittest

from mctools.common.risk.zone import bin_in_range, Limits, Limits3D, Zone
from mctools.common.risk.test.input_histogram import create_test_histogram


class TestZone(unittest.TestCase):
    def test_bin_in_range(self):
        hist = create_test_histogram(name="th3_0")
        axis = hist.GetXaxis()
        with self.assertWarns(UserWarning):
            bin_in_range(n_bin=1, axis=axis, limits=Limits(lower=-0.3, upper=-0.7))
        # Both limits inside bin
        self.assertTrue(
            bin_in_range(n_bin=1, axis=axis, limits=Limits(lower=-0.7, upper=-0.3))
        )
        # Lower limit outside bin
        self.assertTrue(
            bin_in_range(n_bin=1, axis=axis, limits=Limits(lower=-1.3, upper=-0.3))
        )
        # Upper limit outside bin
        self.assertTrue(
            bin_in_range(n_bin=1, axis=axis, limits=Limits(lower=-0.7, upper=0.3))
        )
        # Equal limits inside bin
        self.assertTrue(
            bin_in_range(n_bin=1, axis=axis, limits=Limits(lower=-0.1, upper=-0.1))
        )
        # Equal limits on edges
        self.assertTrue(
            bin_in_range(n_bin=1, axis=axis, limits=Limits(lower=-1.0, upper=-1.0))
        )
        self.assertTrue(
            bin_in_range(n_bin=1, axis=axis, limits=Limits(lower=0.0, upper=0.0))
        )
        # Both limits outside bin
        self.assertTrue(
            bin_in_range(n_bin=1, axis=axis, limits=Limits(lower=-10.0, upper=10.0))
        )

        # Both limits below bin
        self.assertFalse(
            bin_in_range(n_bin=2, axis=axis, limits=Limits(lower=-1.0, upper=-0.5))
        )
        self.assertFalse(
            bin_in_range(n_bin=2, axis=axis, limits=Limits(lower=-0.1, upper=-0.1))
        )
        # Both limits above bin
        self.assertFalse(
            bin_in_range(n_bin=2, axis=axis, limits=Limits(lower=1.5, upper=2.5))
        )
        # Upper limit on edge
        self.assertTrue(
            bin_in_range(n_bin=2, axis=axis, limits=Limits(lower=-1.0, upper=0.0))
        )
        # Lower limit on edge
        self.assertTrue(
            bin_in_range(n_bin=2, axis=axis, limits=Limits(lower=1.0, upper=2.0))
        )
        # Both limits outside bin
        self.assertTrue(
            bin_in_range(n_bin=2, axis=axis, limits=Limits(lower=-10.0, upper=10.0))
        )

    def test_zone(self):
        # Create test histogram
        hist = create_test_histogram(name="th3_1")

        # 1) No Condition
        zone = Zone(hist=hist)
        zone.evaluate()
        self.assertEqual(zone.value.val, 7.0)
        self.assertAlmostEqual(zone.value.err, 0.7, places=15)
        self.assertEqual(zone.value.x, 0.5)
        self.assertEqual(zone.value.y, 0.5)
        self.assertEqual(zone.value.z, 0.5)

        # 2) Single Condition
        zone = Zone(hist=hist, lim=Limits3D(zlim=Limits(upper=-0.1)))
        zone.evaluate()
        self.assertEqual(zone.value.val, 6.0)
        self.assertAlmostEqual(zone.value.err, 0.6, places=15)
        self.assertEqual(zone.value.x, 0.5)
        self.assertEqual(zone.value.y, 0.5)
        self.assertEqual(zone.value.z, -0.5)

        # 3) Multiple conditions
        zone = Zone(
            hist=hist, lim=Limits3D(xlim=Limits(upper=-0.1), zlim=Limits(lower=0.1))
        )
        zone.evaluate()
        self.assertEqual(zone.value.val, 3.0)
        self.assertAlmostEqual(zone.value.err, 0.3, places=15)
        self.assertEqual(zone.value.x, -0.5)
        self.assertEqual(zone.value.y, 0.5)
        self.assertEqual(zone.value.z, 0.5)

        zone = Zone(
            hist=hist,
            lim=Limits3D(
                xlim=Limits(upper=-0.1), ylim=Limits(upper=-0.1), zlim=Limits(lower=0.1)
            ),
        )
        zone.evaluate()
        self.assertEqual(zone.value.val, 1.0)
        self.assertAlmostEqual(zone.value.err, 0.1, places=15)
        self.assertEqual(zone.value.x, -0.5)
        self.assertEqual(zone.value.y, -0.5)
        self.assertEqual(zone.value.z, 0.5)
