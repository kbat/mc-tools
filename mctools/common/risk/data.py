from mctools.common.risk.level import BaseLevel, depth_first_search_with_path, Level
from mctools.common.risk.value import Value


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

    def evaluate(self):
        values: list[Value] = []
        for source in self.combination:
            level: BaseLevel = self.sources[source[0]]
            for lvl in source[1:]:
                level = level[lvl]
            values.append(level.get_max_value())
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

    def __str__(
        self,
        threshold: float = float("inf"),
        unit: str = "",
        include_top_level: bool = True,
    ):
        buffer = []
        results: tuple[tuple[str], BaseLevel] = self.get_results(
            include_top_level=include_top_level
        )
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

    def get_results(
        self, include_top_level: bool = True
    ) -> tuple[tuple[str], BaseLevel]:
        """Return the results as a flat list"""
        data: tuple[tuple[str], Value] = []
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

    def evaluate(self):
        for source in self.sources:
            self.sources[source].evaluate()

        for combo in self.arbitrary_level_combos:
            self.arbitrary_level_combos[combo].set_sources(self.sources)
            self.arbitrary_level_combos[combo].evaluate()
