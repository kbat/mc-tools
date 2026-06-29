import unittest

from mctools.common.risk.level import Level
from mctools.common.risk.test.input_histogram import create_test_histogram
from mctools.common.risk.zone import Limits, Limits3D, Zone


class TestLevels(unittest.TestCase):
    def test_levels(self):
        # 1) No Constraints
        lvl = Level(
            name="L2",
            sub_levels={
                "L1_0": Level(
                    sub_levels={
                        "L0_0": Zone(hist=create_test_histogram("l0_0", 1.0)),
                        "L0_1": Zone(hist=create_test_histogram("l0_1", 2.0)),
                    }
                ),
                "L1_1": Level(
                    sub_levels={
                        "L0_0": Zone(hist=create_test_histogram("l1_0", 3.0)),
                        "L0_1": Zone(hist=create_test_histogram("l1_1", 4.0)),
                    }
                ),
            },
        )
        # Maximum at Level 2
        self.assertEqual(lvl.get_max_value().val, 28.0)
        # Maxima at Level 1
        self.assertEqual(lvl["L1_0"].get_max_value().val, 14.0)
        self.assertEqual(lvl["L1_1"].get_max_value().val, 28.0)
        # Maxima at Level 0
        self.assertEqual(lvl["L1_0"]["L0_0"].get_max_value().val, 7.0)
        self.assertEqual(lvl["L1_0"]["L0_1"].get_max_value().val, 14.0)
        self.assertEqual(lvl["L1_1"]["L0_0"].get_max_value().val, 21.0)
        self.assertEqual(lvl["L1_1"]["L0_1"].get_max_value().val, 28.0)

        # 2) Constraints
        lvl = Level(
            name="L2",
            sub_levels={
                "L1_0": Level(
                    sub_levels={
                        "L0_0": Zone(hist=create_test_histogram("L0_0", 1.0)),
                        "L0_1": Zone(hist=create_test_histogram("L0_1", 2.0)),
                    }
                ),
                "L1_1": Level(
                    sub_levels={
                        "L0_0": Zone(
                            hist=create_test_histogram("L1_0", 3.0),
                            lim=Limits3D(
                                zlim=Limits(upper=-0.1),
                            ),
                        ),
                        "L0_1": Zone(
                            hist=create_test_histogram("L1_1", 4.0),
                            lim=Limits3D(
                                xlim=Limits(upper=-0.1),
                                ylim=Limits(lower=0.1),
                                zlim=Limits(upper=-0.1),
                            ),
                        ),
                    }
                ),
            },
        )
        # Maximum at Level 2
        max_value = lvl.get_max_value()
        self.assertEqual(max_value.val, 18.0)
        self.assertEqual(max_value.err, 1.8)
        self.assertEqual(max_value.x, 0.5)
        self.assertEqual(max_value.y, 0.5)
        self.assertEqual(max_value.z, -0.5)
        # Maxima at Level 1
        self.assertEqual(lvl["L1_0"].get_max_value().val, 14.0)
        self.assertEqual(lvl["L1_1"].get_max_value().val, 18.0)
        # Maxima at Level 0
        self.assertEqual(lvl["L1_0"]["L0_0"].get_max_value().val, 7.0)
        self.assertEqual(lvl["L1_0"]["L0_1"].get_max_value().val, 14.0)
        self.assertEqual(lvl["L1_1"]["L0_0"].get_max_value().val, 18.0)
        self.assertEqual(lvl["L1_1"]["L0_1"].get_max_value().val, 8.0)

    def test_paths(self):
        lvl = Level(
            name="L3",
            path="L3",
            sub_levels={
                "L2_0": Level(
                    sub_levels={
                        "L1_0": Level(
                            sub_levels={"L0_0": Zone(hist=""), "L0_1": Zone(hist="")},
                        ),
                        "L1_1": Zone(hist=""),
                    }
                ),
                "L2_1": Level(
                    sub_levels={
                        "L1_0": Zone(hist=""),
                        "L1_1": Zone(hist=""),
                    }
                ),
            },
        )
        lvl.set_sub_level_paths()
        self.assertEqual(lvl.path, "L3")
        self.assertEqual(lvl["L2_0"].path, "L3.L2_0")
        self.assertEqual(lvl["L2_0"]["L1_0"].path, "L3.L2_0.L1_0")
        self.assertEqual(lvl["L2_0"]["L1_0"]["L0_0"].path, "L3.L2_0.L1_0.L0_0")
        self.assertEqual(lvl["L2_0"]["L1_0"]["L0_1"].path, "L3.L2_0.L1_0.L0_1")
        self.assertEqual(lvl["L2_0"]["L1_1"].path, "L3.L2_0.L1_1")
        self.assertEqual(lvl["L2_1"].path, "L3.L2_1")
        self.assertEqual(lvl["L2_1"]["L1_0"].path, "L3.L2_1.L1_0")
        self.assertEqual(lvl["L2_1"]["L1_1"].path, "L3.L2_1.L1_1")
