"""Hierarchy of logical levels with associated sublevels"""

from abc import abstractmethod

from mctools.common.risk.value import UnknownValue, Value


class BaseLevel:
    """Base level without sublevels"""

    def __init__(self, name: str = "", title: str = "", path: str = ""):
        self.name = name
        if self.name != "" and title == "":
            self.title = name
        else:
            self.title = title
        self.path = path
        self.value: Value = UnknownValue()

    def get_max_value(self) -> Value:
        """Retrieve the maximum value. If unknown, evaluate it first."""
        if isinstance(self.value, UnknownValue):
            self.evaluate()
        return self.value

    @abstractmethod
    def evaluate(self):
        """Evaluate the maximum value"""

    @abstractmethod
    def set_sub_level_paths(self, path_prefix: str = "", separator: str = "."): ...


class Level(BaseLevel):
    """Upper and intermediate level with sublevels"""

    def __init__(
        self,
        name: str = "",
        title: str = "",
        path: str = "",
        sub_levels: dict[str, "Level"] | None = None,
    ):
        super().__init__(name=name, title=title, path=path)
        if sub_levels is None:
            self.sub_levels: dict[str, Level] = {}
        else:
            self.sub_levels = sub_levels

    def evaluate(self):
        """Find the maximum value of all sublevels"""
        self.value = max(
            self[sub_level].get_max_value() for sub_level in self.sub_levels
        )

    def set_sub_level_paths(self, separator: str = "."):
        for sub_level in self.sub_levels:
            self[sub_level].path = self.path + separator + sub_level
            self[sub_level].set_sub_level_paths()

    def __getitem__(self, key: str):
        return self.sub_levels[key]


def depth_first_search(obj: Level | BaseLevel):
    if isinstance(obj, Level):
        for level in obj.sub_levels:
            yield from depth_first_search(obj[level])
    else:
        yield obj


def depth_first_search_with_path(obj: Level | BaseLevel, path=()):
    if isinstance(obj, Level):
        for level in obj.sub_levels:
            new_path = path + (level,)
            yield from depth_first_search_with_path(obj[level], new_path)
    else:
        yield path, obj
