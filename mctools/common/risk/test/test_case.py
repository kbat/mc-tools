import tempfile
import unittest
from pathlib import Path

import ROOT

from mctools.common.risk.case import Case
from mctools.common.risk.data import Data, SourceCombination
from mctools.common.risk.level import Level
from mctools.common.risk.scenario import Scenario
from mctools.common.risk.test.input_histogram import create_test_histogram
from mctools.common.risk.zone import Zone


def make_test_case(root_file_name, scale_file_name, scenario_names):
    scenarios = {}
    for scenario_name in scenario_names:
        scenarios[scenario_name] = Scenario(
            name=scenario_name,
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
                        }
                    ),
                    "Region1": Level(
                        sub_levels={
                            "Area0": Level(
                                sub_levels={
                                    "Zone2": Zone(hist="Zone2"),
                                    "Zone3": Zone(hist="Zone3"),
                                }
                            ),
                        }
                    ),
                },
                arbitrary_level_combos={
                    "Region0.Max": SourceCombination(combination=[["Region0"]])
                },
            ),
            root_file_name=root_file_name,
            scale_file_name=scale_file_name,
        )
    return Case(scenarios=scenarios)


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

    def test_parallel_evaluate_matches_sequential(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale,
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

            scenario_names = ["Scenario0", "Scenario1"]
            sequential_case = make_test_case(
                root_file_name=tmp_root.name,
                scale_file_name=tmp_scale.name,
                scenario_names=scenario_names,
            )
            parallel_case = make_test_case(
                root_file_name=tmp_root.name,
                scale_file_name=tmp_scale.name,
                scenario_names=scenario_names,
            )

            sequential_case.evaluate()
            parallel_case.evaluate(parallel=True, max_workers=2)

            for scenario_name in scenario_names:
                self.assertEqual(
                    parallel_case[scenario_name].data.sources["Region0"].value.val,
                    sequential_case[scenario_name].data.sources["Region0"].value.val,
                )
                self.assertEqual(
                    parallel_case[scenario_name].data.sources["Region1"].value.val,
                    sequential_case[scenario_name].data.sources["Region1"].value.val,
                )
                self.assertEqual(
                    parallel_case[scenario_name]
                    .data.arbitrary_level_combos["Region0.Max"]
                    .value.val,
                    sequential_case[scenario_name]
                    .data.arbitrary_level_combos["Region0.Max"]
                    .value.val,
                )

    def test_latex_escapes_special_characters(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale,
            tempfile.NamedTemporaryFile(suffix=".tex") as command_output_file,
            tempfile.NamedTemporaryFile(suffix=".tex") as variable_output_file,
        ):
            tfile = ROOT.TFile(tmp_root.name, "RECREATE")
            create_test_histogram(name="Zone_#1%", scale=1.0).Write()
            tfile.Close()

            with open(tmp_scale.name, "w") as scale_file:
                scale_file.write("1.0")

            case = Case(
                scenarios={
                    "Scenario_#1%": Scenario(
                        name="Scenario_#1%",
                        data=Data(
                            sources={
                                "Region_&1": Level(
                                    sub_levels={
                                        "Area_{1}": Level(
                                            sub_levels={
                                                "Zone_#1%": Zone(hist="Zone_#1%")
                                            }
                                        )
                                    }
                                )
                            }
                        ),
                        root_file_name=Path(tmp_root.name),
                        scale_file_name=Path(tmp_scale.name),
                    )
                }
            )

            case.evaluate()
            case.toLaTeX(
                command_output_file_name=Path(command_output_file.name),
                variable_output_file_name=Path(variable_output_file.name),
            )

            commands = Path(command_output_file.name).read_text(encoding="utf-8")
            variables = Path(variable_output_file.name).read_text(encoding="utf-8")

            self.assertIn(r"\ifthenelse{\equal{#1}{Scenario\_\#1\%}}", commands)
            self.assertIn(r"\section{Scenario\_\#1\%}", variables)
            self.assertIn(r"\def\region{Region\_\&1}", variables)
            self.assertIn(r"\def\area{Area\_\{1\}}", variables)
            self.assertIn(r"\def\zone{Zone\_\#1\%}", variables)
            self.assertIn(r"\input{", variables)
