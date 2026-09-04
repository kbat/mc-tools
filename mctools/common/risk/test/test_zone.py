import unittest

from mctools.common.risk.zone import BoxLimits3D, Limits, Limits3D, Zone
from mctools.common.risk.test.input_histogram import create_test_histogram


def x_bin_in_range(n_bin: int, hist, xlim: Limits) -> bool:
    return BoxLimits3D(xlim=xlim).bin_in_range(n_x=n_bin, n_y=1, n_z=1, hist=hist)


class TestZone(unittest.TestCase):
    def test_limits_3d_is_abstract(self):
        with self.assertRaises(TypeError):
            Limits3D()

    def test_box_limits_3d_bin_in_range(self):
        hist = create_test_histogram(name="th3_0")
        with self.assertWarns(UserWarning):
            x_bin_in_range(n_bin=1, hist=hist, xlim=Limits(lower=-0.3, upper=-0.7))
        # Both limits inside bin
        self.assertTrue(
            x_bin_in_range(n_bin=1, hist=hist, xlim=Limits(lower=-0.7, upper=-0.3))
        )
        # Lower limit outside bin
        self.assertTrue(
            x_bin_in_range(n_bin=1, hist=hist, xlim=Limits(lower=-1.3, upper=-0.3))
        )
        # Upper limit outside bin
        self.assertTrue(
            x_bin_in_range(n_bin=1, hist=hist, xlim=Limits(lower=-0.7, upper=0.3))
        )
        # Equal limits inside bin
        self.assertTrue(
            x_bin_in_range(n_bin=1, hist=hist, xlim=Limits(lower=-0.1, upper=-0.1))
        )
        # Equal limits on edges
        self.assertTrue(
            x_bin_in_range(n_bin=1, hist=hist, xlim=Limits(lower=-1.0, upper=-1.0))
        )
        self.assertTrue(
            x_bin_in_range(n_bin=1, hist=hist, xlim=Limits(lower=0.0, upper=0.0))
        )
        # Both limits outside bin
        self.assertTrue(
            x_bin_in_range(n_bin=1, hist=hist, xlim=Limits(lower=-10.0, upper=10.0))
        )

        # Both limits below bin
        self.assertFalse(
            x_bin_in_range(n_bin=2, hist=hist, xlim=Limits(lower=-1.0, upper=-0.5))
        )
        self.assertFalse(
            x_bin_in_range(n_bin=2, hist=hist, xlim=Limits(lower=-0.1, upper=-0.1))
        )
        # Both limits above bin
        self.assertFalse(
            x_bin_in_range(n_bin=2, hist=hist, xlim=Limits(lower=1.5, upper=2.5))
        )
        # Upper limit on edge
        self.assertTrue(
            x_bin_in_range(n_bin=2, hist=hist, xlim=Limits(lower=-1.0, upper=0.0))
        )
        # Lower limit on edge
        self.assertTrue(
            x_bin_in_range(n_bin=2, hist=hist, xlim=Limits(lower=1.0, upper=2.0))
        )
        # Both limits outside bin
        self.assertTrue(
            x_bin_in_range(n_bin=2, hist=hist, xlim=Limits(lower=-10.0, upper=10.0))
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
        zone = Zone(hist=hist, lim=[BoxLimits3D(zlim=Limits(upper=-0.1))])
        zone.evaluate()
        self.assertEqual(zone.value.val, 6.0)
        self.assertAlmostEqual(zone.value.err, 0.6, places=15)
        self.assertEqual(zone.value.x, 0.5)
        self.assertEqual(zone.value.y, 0.5)
        self.assertEqual(zone.value.z, -0.5)

        # 3) Multiple conditions on the same BoxLimits3D
        zone = Zone(
            hist=hist,
            lim=[BoxLimits3D(xlim=Limits(upper=-0.1), zlim=Limits(lower=0.1))],
        )
        zone.evaluate()
        self.assertEqual(zone.value.val, 3.0)
        self.assertAlmostEqual(zone.value.err, 0.3, places=15)
        self.assertEqual(zone.value.x, -0.5)
        self.assertEqual(zone.value.y, 0.5)
        self.assertEqual(zone.value.z, 0.5)

        zone = Zone(
            hist=hist,
            lim=[
                BoxLimits3D(
                    xlim=Limits(upper=-0.1),
                    ylim=Limits(upper=-0.1),
                    zlim=Limits(lower=0.1),
                )
            ],
        )
        zone.evaluate()
        self.assertEqual(zone.value.val, 1.0)
        self.assertAlmostEqual(zone.value.err, 0.1, places=15)
        self.assertEqual(zone.value.x, -0.5)
        self.assertEqual(zone.value.y, -0.5)
        self.assertEqual(zone.value.z, 0.5)

    def test_box_limits_3d_inverted(self):
        hist = create_test_histogram(name="th3_4")

        box = BoxLimits3D(zlim=Limits(upper=-0.1))
        inverted_box = BoxLimits3D(zlim=Limits(upper=-0.1), inverted=True)
        for n_x in (1, 2):
            for n_y in (1, 2):
                for n_z in (1, 2):
                    self.assertEqual(
                        inverted_box.bin_in_range(n_x, n_y, n_z, hist),
                        not box.bin_in_range(n_x, n_y, n_z, hist),
                    )

        zone = Zone(hist=hist, lim=[inverted_box])
        zone.evaluate()
        self.assertEqual(zone.value.val, 7.0)
        self.assertEqual(zone.value.x, 0.5)
        self.assertEqual(zone.value.y, 0.5)
        self.assertEqual(zone.value.z, 0.5)

    def test_zone_accepts_single_limits3d(self):
        hist = create_test_histogram(name="th3_6")
        box = BoxLimits3D(zlim=Limits(upper=-0.1))

        zone = Zone(hist=hist, lim=box)

        self.assertEqual(zone.lim, [box])

    def test_zone_combined_limits(self):
        # Inner box, inverted: everywhere except the (0.5, 0.5, 0.5) corner bin.
        # Excludes the global maximum.
        # Outer box: only the z = 0.5 slice. Excludes the next-highest value.
        hist = create_test_histogram(name="th3_5")
        outer = BoxLimits3D(zlim=Limits(lower=0.1))
        inner_excluded = BoxLimits3D(
            xlim=Limits(lower=0.1),
            ylim=Limits(lower=0.1),
            zlim=Limits(lower=0.1),
            inverted=True,
        )
        zone = Zone(hist=hist, lim=[outer, inner_excluded])
        zone.evaluate()
        self.assertEqual(zone.value.val, 5.0)
        self.assertEqual(zone.value.x, 0.5)
        self.assertEqual(zone.value.y, -0.5)
        self.assertEqual(zone.value.z, 0.5)

    def test_zone_default_limits_are_not_shared(self):
        zone_0 = Zone(hist=create_test_histogram(name="th3_2"))
        zone_1 = Zone(hist=create_test_histogram(name="th3_3"))

        zone_0.lim[0].xlim.lower = 0.0

        self.assertEqual(zone_1.lim[0].xlim.lower, float("-inf"))

    def test_limits_str(self):
        self.assertEqual(str(Limits()), "")
        self.assertEqual(str(Limits(variable_name="y")), "")

        self.assertEqual(str(Limits(lower=0.0)), "0.0 <= x")
        self.assertEqual(str(Limits(lower=0.0, variable_name="y")), "0.0 <= y")

        self.assertEqual(str(Limits(upper=0.0)), "x <= 0.0")
        self.assertEqual(str(Limits(upper=0.0, variable_name="y")), "y <= 0.0")

        self.assertEqual(str(Limits(lower=0.0, upper=0.0)), "x = 0.0")
        self.assertEqual(
            str(Limits(lower=0.0, upper=0.0, variable_name="y")), "y = 0.0"
        )

        self.assertEqual(str(Limits(lower=0.0, upper=1.0)), "0.0 <= x <= 1.0")
        self.assertEqual(
            str(Limits(lower=0.0, upper=1.0, variable_name="y")), "0.0 <= y <= 1.0"
        )

        self.assertEqual(str(BoxLimits3D()), "")

        self.assertEqual(
            str(BoxLimits3D(xlim=Limits(lower=0.0, upper=1.0))), "0.0 <= x <= 1.0"
        )
        self.assertEqual(
            str(BoxLimits3D(ylim=Limits(lower=0.0, upper=1.0))), "0.0 <= y <= 1.0"
        )
        self.assertEqual(
            str(BoxLimits3D(zlim=Limits(lower=0.0, upper=1.0))), "0.0 <= z <= 1.0"
        )

        self.assertEqual(
            str(
                BoxLimits3D(
                    xlim=Limits(lower=0.0, upper=1.0), ylim=Limits(lower=0.0, upper=1.0)
                )
            ),
            "0.0 <= x <= 1.0 && 0.0 <= y <= 1.0",
        )
        self.assertEqual(
            str(
                BoxLimits3D(
                    xlim=Limits(lower=0.0, upper=1.0), zlim=Limits(lower=0.0, upper=1.0)
                )
            ),
            "0.0 <= x <= 1.0 && 0.0 <= z <= 1.0",
        )
        self.assertEqual(
            str(
                BoxLimits3D(
                    ylim=Limits(lower=0.0, upper=1.0), zlim=Limits(lower=0.0, upper=1.0)
                )
            ),
            "0.0 <= y <= 1.0 && 0.0 <= z <= 1.0",
        )

        self.assertEqual(
            str(
                BoxLimits3D(
                    xlim=Limits(lower=0.0, upper=1.0),
                    ylim=Limits(lower=0.0, upper=1.0),
                    zlim=Limits(lower=0.0, upper=1.0),
                )
            ),
            "0.0 <= x <= 1.0 && 0.0 <= y <= 1.0 && 0.0 <= z <= 1.0",
        )
        self.assertEqual(
            str(
                BoxLimits3D(
                    xlim=Limits(lower=0.0, upper=0.0),
                    ylim=Limits(upper=1.0),
                    zlim=Limits(lower=0.0),
                )
            ),
            "x = 0.0 && y <= 1.0 && 0.0 <= z",
        )
