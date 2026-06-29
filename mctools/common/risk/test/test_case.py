import tempfile
import unittest

import ROOT

from mctools.common.risk.case import Case
from mctools.common.risk.data import Data, SourceCombination
from mctools.common.risk.level import Level
from mctools.common.risk.scenario import Scenario
from mctools.common.risk.test.input_histogram import create_test_histogram
from mctools.common.risk.zone import Zone


class TestCaseClass(unittest.TestCase):
    def test_case(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale,
            tempfile.NamedTemporaryFile(suffix=".tex") as command_output_file,
            tempfile.NamedTemporaryFile(suffix=".tex") as variable_output_file,
        ):
            tfile = ROOT.TFile(tmp_root.name, "RECREATE")

            histograms = [
                create_test_histogram(name="Zone0", scale=1.0),
                create_test_histogram(name="Zone1", scale=2.0),
                create_test_histogram(name="Zone2", scale=3.0),
                create_test_histogram(name="Zone3", scale=4.0),
            ]

            for hist in histograms:
                hist.Write()
            tfile.Close()

            with open(tmp_scale.name, "w") as scale_file:
                scale_file.write("1.0")

            case = Case(
                scenarios={
                    "Scenario0": Scenario(
                        name="Scenario0",
                        data=Data(
                            sources={
                                "Region0": Level(
                                    sub_levels={
                                        "Area0": Level(
                                            sub_levels={
                                                "Zone0": Zone(hist="Zone0"),
                                                "Zone1": Zone(hist="Zone1"),
                                            }
                                        ),
                                        "Area1": Level(
                                            sub_levels={
                                                "Zone0": Zone(hist="Zone0"),
                                                "Zone1": Zone(hist="Zone1"),
                                            }
                                        ),
                                    }
                                ),
                                "Region1": Level(
                                    sub_levels={
                                        "Area0": Level(
                                            sub_levels={
                                                "Zone0": Zone(hist="Zone0"),
                                                "Zone1": Zone(hist="Zone1"),
                                            }
                                        ),
                                        "Area1": Level(
                                            sub_levels={
                                                "Zone0": Zone(hist="Zone0"),
                                                "Zone1": Zone(hist="Zone1"),
                                            }
                                        ),
                                    }
                                ),
                            },
                            arbitrary_level_combos={
                                "Region0.Max": SourceCombination(
                                    combination=[["Region0"]], path=("Region0.Max")
                                )
                            },
                        ),
                        root_file_name=tmp_root.name,
                        scale_file_name=tmp_scale.name,
                    )
                }
            )
            case.evaluate()
            case.toLaTeX(
                command_output_file_name=command_output_file.name,
                variable_output_file_name=variable_output_file.name,
            )
