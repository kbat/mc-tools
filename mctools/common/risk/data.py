from mctools.common.risk.level import BaseLevel, depth_first_search_with_path, Level
from mctools.common.risk.value import Value

Result = tuple[tuple[str, ...], BaseLevel]


class SourceCombination(BaseLevel):
    def __init__(
        self,
        combination: list[list[str]],
        name: str = "",
        title: str = "",
        path: str = "",
    ):
        super().__init__(name=name, title=title, path=path)
        self.combination = combination
        self.sources: dict[str, Level] | None = None

    def set_sources(self, sources: dict[str, Level]):
        self.sources = sources

    def evaluate(self, root_input_cache=None):
        values: list[Value] = []
        for source in self.combination:
            level: BaseLevel = self.sources[source[0]]
            # Step down in the level hierarchy using the given keys.
            for lvl in source[1:]:
                level = level[lvl]
            values.append(level.get_max_value(root_input_cache=root_input_cache))
        self.value = max(values)


class Data:
    def __init__(
        self,
        sources: dict[str, Level],
        arbitrary_level_combos: dict[str, SourceCombination] | None = None,
    ):
        self.sources = sources
        self.arbitrary_level_combos: dict[str, SourceCombination] = {}
        if arbitrary_level_combos is not None:
            self.arbitrary_level_combos = arbitrary_level_combos

    def get_max_path_length(self) -> int:
        max_length = 0
        for result in self.get_results(include_top_level=True):
            l = len(result[1].path)
            if l > max_length:
                max_length = l
        return max_length

    def __str__(self):
        results = self.get_results(include_top_level=True)
        max_path_length = self.get_max_path_length()
        buffer = (
            f"{"PATH":{max_path_length}}   {"VALUE":11}  {"ERROR":11}  "
            f"{"X":11}  {"Y":11}  {"Z":10}\n"
        )
        n_results = len(results)
        for n_result, result in enumerate(results):
            buffer += (
                f"{result[1].path:{max_path_length}}  "
                f"{result[1].value.val: 10.4e}  "
                f"{result[1].value.err: 10.4e}  "
                f"{result[1].value.x: 10.4e}  "
                f"{result[1].value.y: 10.4e}  "
                f"{result[1].value.z: 10.4e}"
            )
            if n_result < n_results - 1:
                buffer += "\n"
        return buffer

    def print(
        self,
        threshold: float = float("inf"),
        unit: str = "",
        include_top_level: bool = True,
    ):
        buffer = []
        results = self.get_results(include_top_level=include_top_level)
        for result in results:
            title = result[1].title if result[1].title != "" else result[1].path
            buffer.append(
                f"{title}:"
                f" {result[1].value} at {result[1].value.x:.4f} "
                f"{result[1].value.y:.4f} {result[1].value.z:.4f}"
                f"\t{result[1].path}\n"
            )
            if result[1].value.val > threshold:
                buffer.append(
                    f"\033[31m Above {threshold} {unit}: \033[0m {title}: {result[1].value}\n"
                )
        return "".join(buffer)

    def set_sub_level_paths(self, separator: str = ".", path_prefix: str = ""):
        for source in self.sources:
            self.sources[source].path = path_prefix + source
            self.sources[source].set_sub_level_paths(separator=separator)
        for combo in self.arbitrary_level_combos:
            self.arbitrary_level_combos[combo].name = combo
            self.arbitrary_level_combos[combo].path = path_prefix + combo

    def get_results(self, include_top_level: bool = True) -> list[Result]:
        """Return the results as a flat list"""
        data: list[Result] = []
        for source in self.sources:
            if include_top_level:
                data.append(((self.sources[source].path,), self.sources[source]))
            for path, level in depth_first_search_with_path(self.sources[source]):
                data.append((path, level))
        for combo in self.arbitrary_level_combos:
            data.append(
                (
                    (self.arbitrary_level_combos[combo].path,),
                    self.arbitrary_level_combos[combo],
                )
            )
        return data

    def __getitem__(self, key: str):
        if key in self.sources:
            return self.sources[key]
        return self.arbitrary_level_combos[key]

    def evaluate(self, root_input_cache=None):
        for source in self.sources:
            self.sources[source].evaluate(root_input_cache=root_input_cache)

        for combo in self.arbitrary_level_combos:
            self.arbitrary_level_combos[combo].set_sources(self.sources)
            self.arbitrary_level_combos[combo].evaluate(
                root_input_cache=root_input_cache
            )
