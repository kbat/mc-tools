import unittest

from mctools.common.risk.data import Data, SourceCombination
from mctools.common.risk.level import Level
from mctools.common.risk.test.input_histogram import create_test_histogram
from mctools.common.risk.zone import Zone


class TestData(unittest.TestCase):
    def test_data(self):
        data = Data(
            sources={
                "L2_0": Level(
                    title="Level 2, Sublevel 0",
                    sub_levels={
                        "L1_0": Zone(hist=create_test_histogram("L1_0", 1.0)),
                        "L1_1": Zone(hist=create_test_histogram("L1_1", 2.0)),
                    },
                ),
                "L2_1": Level(
                    sub_levels={
                        "L1_0": Level(
                            sub_levels={
                                "L0_0": Zone(hist=create_test_histogram("L0_0", 3.0)),
                                "L0_1": Zone(hist=create_test_histogram("L0_1", 4.0)),
                            }
                        ),
                        "L1_1": Level(
                            sub_levels={
                                "L0_0": Zone(hist=create_test_histogram("L0_0p", 5.0)),
                                "L0_1": Zone(hist=create_test_histogram("L0_1p", 6.0)),
                            }
                        ),
                    }
                ),
            },
            arbitrary_level_combos={
                "custom0": SourceCombination(
                    combination=[["L2_0"], ["L2_1", "L1_0", "L0_1"]]
                ),
                "custom1": SourceCombination(
                    combination=[["L2_0"], ["L2_1", "L1_0", "L0_1"], ["L2_1", "L1_1"]]
                ),
            },
        )
        data.set_sub_level_paths()

        # Verify that the paths are set correctly
        self.assertEqual(data.sources["L2_0"].path, "L2_0")
        self.assertEqual(data.sources["L2_0"]["L1_0"].path, "L2_0.L1_0")
        self.assertEqual(data.sources["L2_0"]["L1_1"].path, "L2_0.L1_1")
        self.assertEqual(data.sources["L2_1"].path, "L2_1")
        self.assertEqual(data.sources["L2_1"]["L1_0"].path, "L2_1.L1_0")
        self.assertEqual(data.sources["L2_1"]["L1_0"]["L0_0"].path, "L2_1.L1_0.L0_0")
        self.assertEqual(data.sources["L2_1"]["L1_0"]["L0_1"].path, "L2_1.L1_0.L0_1")
        self.assertEqual(data.sources["L2_1"]["L1_1"].path, "L2_1.L1_1")
        self.assertEqual(data.sources["L2_1"]["L1_1"]["L0_0"].path, "L2_1.L1_1.L0_0")
        self.assertEqual(data.sources["L2_1"]["L1_1"]["L0_1"].path, "L2_1.L1_1.L0_1")

        data.evaluate()
        # Level 2
        self.assertEqual(data.sources["L2_0"].value.val, 14.0)
        self.assertEqual(data.sources["L2_1"].value.val, 42.0)
        # Level 1
        self.assertEqual(data.sources["L2_0"]["L1_0"].value.val, 7.0)
        self.assertEqual(data.sources["L2_0"]["L1_1"].value.val, 14.0)
        self.assertEqual(data.sources["L2_1"]["L1_0"].value.val, 28.0)
        self.assertEqual(data.sources["L2_1"]["L1_1"].value.val, 42.0)
        # Level 0 (only for L2_1 branch)
        self.assertEqual(data.sources["L2_1"]["L1_0"]["L0_0"].value.val, 21.0)
        self.assertEqual(data.sources["L2_1"]["L1_0"]["L0_1"].value.val, 28.0)
        self.assertEqual(data.sources["L2_1"]["L1_1"]["L0_0"].value.val, 35.0)
        self.assertEqual(data.sources["L2_1"]["L1_1"]["L0_1"].value.val, 42.0)
        # Combinations
        self.assertEqual(data.arbitrary_level_combos["custom0"].value.val, 28.0)
        self.assertEqual(data.arbitrary_level_combos["custom1"].value.val, 42.0)

        print(data.__str__())
        # Test string representation
        self.assertEqual(
            data.__str__(),
            "Level 2, Sublevel 0: 14 ± 1   10.0 % at 0.5000 0.5000 0.5000\tL2_0\n"
            "L2_0.L1_0: 7 ± 0.7   10.0 % at 0.5000 0.5000 0.5000\tL2_0.L1_0\n"
            "L2_0.L1_1: 14 ± 1   10.0 % at 0.5000 0.5000 0.5000\tL2_0.L1_1\n"
            "L2_1: 42 ± 4   10.0 % at 0.5000 0.5000 0.5000\tL2_1\n"
            "L2_1.L1_0.L0_0: 21 ± 2   10.0 % at 0.5000 0.5000 0.5000\tL2_1.L1_0.L0_0\n"
            "L2_1.L1_0.L0_1: 28 ± 3   10.0 % at 0.5000 0.5000 0.5000\tL2_1.L1_0.L0_1\n"
            "L2_1.L1_1.L0_0: 35 ± 4   10.0 % at 0.5000 0.5000 0.5000\tL2_1.L1_1.L0_0\n"
            "L2_1.L1_1.L0_1: 42 ± 4   10.0 % at 0.5000 0.5000 0.5000\tL2_1.L1_1.L0_1\n"
            "custom0: 28 ± 3   10.0 % at 0.5000 0.5000 0.5000\tcustom0\n"
            "custom1: 42 ± 4   10.0 % at 0.5000 0.5000 0.5000\tcustom1\n",
        )

        self.assertEqual(
            data.__str__(threshold=40.0, unit="a.u."),
            "Level 2, Sublevel 0: 14 ± 1   10.0 % at 0.5000 0.5000 0.5000\tL2_0\n"
            "L2_0.L1_0: 7 ± 0.7   10.0 % at 0.5000 0.5000 0.5000\tL2_0.L1_0\n"
            "L2_0.L1_1: 14 ± 1   10.0 % at 0.5000 0.5000 0.5000\tL2_0.L1_1\n"
            "L2_1: 42 ± 4   10.0 % at 0.5000 0.5000 0.5000\tL2_1\n"
            "\033[31m Above 40.0 a.u.: \033[0m L2_1: 42 ± 4   10.0 %\n"
            "L2_1.L1_0.L0_0: 21 ± 2   10.0 % at 0.5000 0.5000 0.5000\tL2_1.L1_0.L0_0\n"
            "L2_1.L1_0.L0_1: 28 ± 3   10.0 % at 0.5000 0.5000 0.5000\tL2_1.L1_0.L0_1\n"
            "L2_1.L1_1.L0_0: 35 ± 4   10.0 % at 0.5000 0.5000 0.5000\tL2_1.L1_1.L0_0\n"
            "L2_1.L1_1.L0_1: 42 ± 4   10.0 % at 0.5000 0.5000 0.5000\tL2_1.L1_1.L0_1\n"
            "\033[31m Above 40.0 a.u.: \033[0m L2_1.L1_1.L0_1: 42 ± 4   10.0 %\n"
            "custom0: 28 ± 3   10.0 % at 0.5000 0.5000 0.5000\tcustom0\n"
            "custom1: 42 ± 4   10.0 % at 0.5000 0.5000 0.5000\tcustom1\n"
            "\033[31m Above 40.0 a.u.: \033[0m custom1: 42 ± 4   10.0 %\n",
        )
