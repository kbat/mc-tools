import tempfile
import unittest

import ROOT

from mctools.common.risk.level import Level
from mctools.common.risk.test.input_histogram import create_test_histogram
from mctools.common.risk.zone import (
    BoxLimits3D,
    Limits,
    ROOTFileInput,
    ROOTInputCache,
    Zone,
)


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

    def test_root_input_cache_reuses_scaled_histogram(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale,
        ):
            tfile = ROOT.TFile(tmp_root.name, "RECREATE")
            create_test_histogram(name="shared", scale=1.0).Write()
            tfile.Close()

            with open(tmp_scale.name, "w") as scale_file:
                scale_file.write("2.0")

            root_input = ROOTFileInput(
                root_file_name=tmp_root.name,
                histogram_name="shared",
                scale_file_name=tmp_scale.name,
            )
            low_zone = Zone(
                hist=root_input,
                lim=[BoxLimits3D(zlim=Limits(upper=-0.1))],
            )
            high_zone = Zone(
                hist=root_input,
                lim=[BoxLimits3D(zlim=Limits(lower=0.1))],
            )

            with ROOTInputCache() as root_input_cache:
                low_zone.evaluate(root_input_cache=root_input_cache)
                high_zone.evaluate(root_input_cache=root_input_cache)

                self.assertEqual(low_zone.value.val, 12.0)
                self.assertEqual(high_zone.value.val, 14.0)
                self.assertEqual(len(root_input_cache.root_files), 1)
                self.assertEqual(len(root_input_cache.scales), 1)
                self.assertEqual(len(root_input_cache.histograms), 1)

    def test_root_input_cache_keeps_scale_files_distinct(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale_0,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale_1,
        ):
            tfile = ROOT.TFile(tmp_root.name, "RECREATE")
            create_test_histogram(name="shared", scale=1.0).Write()
            tfile.Close()

            with open(tmp_scale_0.name, "w") as scale_file:
                scale_file.write("2.0")
            with open(tmp_scale_1.name, "w") as scale_file:
                scale_file.write("3.0")

            zone_0 = Zone(
                hist=ROOTFileInput(
                    root_file_name=tmp_root.name,
                    histogram_name="shared",
                    scale_file_name=tmp_scale_0.name,
                )
            )
            zone_1 = Zone(
                hist=ROOTFileInput(
                    root_file_name=tmp_root.name,
                    histogram_name="shared",
                    scale_file_name=tmp_scale_1.name,
                )
            )

            with ROOTInputCache() as root_input_cache:
                zone_0.evaluate(root_input_cache=root_input_cache)
                zone_1.evaluate(root_input_cache=root_input_cache)

                self.assertEqual(zone_0.value.val, 14.0)
                self.assertEqual(zone_1.value.val, 21.0)
                self.assertEqual(len(root_input_cache.root_files), 1)
                self.assertEqual(len(root_input_cache.scales), 2)
                self.assertEqual(len(root_input_cache.histograms), 2)

    def test_root_input_cache_missing_histogram(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale,
        ):
            tfile = ROOT.TFile(tmp_root.name, "RECREATE")
            create_test_histogram(name="present", scale=1.0).Write()
            tfile.Close()

            with open(tmp_scale.name, "w") as scale_file:
                scale_file.write("1.0")

            zone = Zone(
                hist=ROOTFileInput(
                    root_file_name=tmp_root.name,
                    histogram_name="missing",
                    scale_file_name=tmp_scale.name,
                )
            )

            with ROOTInputCache() as root_input_cache:
                with self.assertRaisesRegex(KeyError, "missing"):
                    zone.evaluate(root_input_cache=root_input_cache)

    def test_root_input_cache_missing_root_file(self):
        with (
            tempfile.TemporaryDirectory() as tmp_dir,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale,
        ):
            missing_root = f"{tmp_dir}/missing.root"
            with open(tmp_scale.name, "w") as scale_file:
                scale_file.write("1.0")

            zone = Zone(
                hist=ROOTFileInput(
                    root_file_name=missing_root,
                    histogram_name="hist",
                    scale_file_name=tmp_scale.name,
                )
            )

            with ROOTInputCache() as root_input_cache:
                with self.assertRaisesRegex(OSError, "Failed to open file"):
                    zone.evaluate(root_input_cache=root_input_cache)

    def test_root_input_cache_missing_scale_file(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.TemporaryDirectory() as tmp_dir,
        ):
            tfile = ROOT.TFile(tmp_root.name, "RECREATE")
            create_test_histogram(name="present", scale=1.0).Write()
            tfile.Close()

            missing_scale = f"{tmp_dir}/missing.txt"
            zone = Zone(
                hist=ROOTFileInput(
                    root_file_name=tmp_root.name,
                    histogram_name="present",
                    scale_file_name=missing_scale,
                )
            )

            with ROOTInputCache() as root_input_cache:
                with self.assertRaisesRegex(FileNotFoundError, "missing.txt"):
                    zone.evaluate(root_input_cache=root_input_cache)

    def test_root_input_cache_invalid_scale_file(self):
        with (
            tempfile.NamedTemporaryFile(suffix=".root") as tmp_root,
            tempfile.NamedTemporaryFile(suffix=".txt") as tmp_scale,
        ):
            tfile = ROOT.TFile(tmp_root.name, "RECREATE")
            create_test_histogram(name="present", scale=1.0).Write()
            tfile.Close()

            with open(tmp_scale.name, "w") as scale_file:
                scale_file.write("not-a-number")

            zone = Zone(
                hist=ROOTFileInput(
                    root_file_name=tmp_root.name,
                    histogram_name="present",
                    scale_file_name=tmp_scale.name,
                )
            )

            with ROOTInputCache() as root_input_cache:
                with self.assertRaisesRegex(
                    ValueError, "could not convert string to float"
                ):
                    zone.evaluate(root_input_cache=root_input_cache)
