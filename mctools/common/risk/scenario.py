from pathlib import Path

from mctools.common.risk.data import Data
from mctools.common.risk.level import depth_first_search
from mctools.common.risk.zone import ROOTFileInput, Zone


class Scenario:
    """Wrapper for Data class

    Assumes that all Zones obtain their histogram data from the same ROOT file and use
    the same scaling factor.
    """

    def __init__(
        self,
        name: str,
        data: Data,
        root_file_name: Path,
        scale_file_name: Path,
    ):
        self.name = name
        self.data = data
        self.root_file_name = root_file_name
        self.scale_file_name = scale_file_name

        # Find the Zone objects at the lowest levels of the hierarchy and assign
        # the ROOTFileInput (data, scale factor, and histogram name) to them.
        for source in self.data.sources:
            for base_level in depth_first_search(data.sources[source]):
                if isinstance(base_level, Zone):
                    if isinstance(base_level.hist, str):
                        hist_name = base_level.hist
                        base_level.hist = ROOTFileInput(
                            root_file_name=self.root_file_name,
                            histogram_name=hist_name,
                            scale_file_name=scale_file_name,
                        )
                    else:
                        raise ValueError(
                            "Scenario assumes that all histograms are"
                            "given by name (str)."
                        )
        self.set_sub_level_paths()

    def set_sub_level_paths(self, separator: str = "."):
        self.data.set_sub_level_paths(
            separator=separator, path_prefix=self.name + separator
        )

    def __getitem__(self, key: str):
        return self.data[key]

    def evaluate(self):
        self.data.evaluate()
