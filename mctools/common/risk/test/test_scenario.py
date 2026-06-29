import tempfile
import unittest

import ROOT

from mctools.common.risk.data import Data, SourceCombination
from mctools.common.risk.level import Level
from mctools.common.risk.scenario import Scenario
from mctools.common.risk.test.input_histogram import create_test_histogram
from mctools.common.risk.zone import Zone


class TestScenario(unittest.TestCase):
    def test_scenario(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale,
        ):
            tfile = ROOT.TFile(tmp_root.name, "RECREATE")

            histograms = [
                create_test_histogram(name="l10l00", scale=1.0),
                create_test_histogram(name="l10l01", scale=2.0),
                create_test_histogram(name="l11l00", scale=3.0),
                create_test_histogram(name="l11l01", scale=4.0),
            ]

            for hist in histograms:
                hist.Write()
            tfile.Close()

            with open(tmp_scale.name, "w") as scale_file:
                scale_file.write("1.0")

            scenario = Scenario(
                name="test",
                data=Data(
                    sources={
                        "L1_0": Level(
                            sub_levels={
                                "L0_0": Zone(hist="l10l00"),
                                "L0_1": Zone(hist="l10l01"),
                            }
                        ),
                        "L1_1": Level(
                            sub_levels={
                                "L0_0": Zone(hist="l11l00"),
                                "L0_1": Zone(hist="l11l01"),
                            }
                        ),
                    },
                    arbitrary_level_combos={
                        "compare_l00": SourceCombination(
                            combination=[["L1_0", "L0_0"], ["L1_1", "L0_0"]]
                        )
                    },
                ),
                root_file_name=tmp_root.name,
                scale_file_name=tmp_scale.name,
            )
            scenario.evaluate()
            self.assertEqual(scenario["L1_0"].value.val, 14.0)
            self.assertEqual(scenario["L1_1"].value.val, 28.0)
            self.assertEqual(scenario["compare_l00"].value.val, 21.0)

            self.assertEqual(scenario["L1_0"]["L0_0"].path, "test.L1_0.L0_0")
            self.assertEqual(scenario["compare_l00"].path, "test.compare_l00")
