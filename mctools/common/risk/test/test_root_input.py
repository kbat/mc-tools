import tempfile
import unittest

import ROOT

from mctools.common.risk.level import Level
from mctools.common.risk.test.input_histogram import create_test_histogram
from mctools.common.risk.zone import ROOTFileInput, Zone


class TestRootInput(unittest.TestCase):
    def test_root_input(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale_0,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale_1,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale_2,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale_3,
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

            with open(tmp_scale_0.name, "w") as scale_file:
                scale_file.write("1.0")
            with open(tmp_scale_1.name, "w") as scale_file:
                scale_file.write("2.0")
            with open(tmp_scale_2.name, "w") as scale_file:
                scale_file.write("3.0")
            with open(tmp_scale_3.name, "w") as scale_file:
                scale_file.write("4.0")

            lvl = Level(
                name="L2",
                sub_levels={
                    "L1_0": Level(
                        sub_levels={
                            "L0_0": Zone(
                                hist=ROOTFileInput(
                                    root_file_name=tmp_root.name,
                                    histogram_name="l10l00",
                                    scale_file_name=tmp_scale_0.name,
                                )
                            ),
                            "L0_1": Zone(
                                hist=ROOTFileInput(
                                    root_file_name=tmp_root.name,
                                    histogram_name="l10l01",
                                    scale_file_name=tmp_scale_1.name,
                                )
                            ),
                        }
                    ),
                    "L1_1": Level(
                        sub_levels={
                            "L0_0": Zone(
                                hist=ROOTFileInput(
                                    root_file_name=tmp_root.name,
                                    histogram_name="l11l00",
                                    scale_file_name=tmp_scale_2.name,
                                )
                            ),
                            "L0_1": Zone(
                                hist=ROOTFileInput(
                                    root_file_name=tmp_root.name,
                                    histogram_name="l11l01",
                                    scale_file_name=tmp_scale_3.name,
                                )
                            ),
                        }
                    ),
                },
            )
            self.assertEqual(lvl.get_max_value().val, 112.0)
