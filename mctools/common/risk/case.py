from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal
from os import cpu_count
from pathlib import Path
from time import time

from mctools.common.risk.scenario import Scenario
from mctools.common.risk.value import Value


def escape_latex(text: str) -> str:
    replacements = (
        ("\\", r"\textbackslash{}"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("#", r"\#"),
        ("$", r"\$"),
        ("%", r"\%"),
        ("&", r"\&"),
        ("_", r"\_"),
        ("^", r"\textasciicircum{}"),
        ("~", r"\textasciitilde{}"),
    )
    escaped = text
    for old, new in replacements:
        escaped = escaped.replace(old, new)
    return escaped


def get_exponent(value: float) -> int:
    """Find base-10 exponent of a floating-point number

    Parameters
    ----------
    value: float
        Input number

    Result
    ------
    int
        Exponent
    """
    _, v_digits, v_raw_exponent = Decimal(value).as_tuple()
    if isinstance(v_raw_exponent, int):
        return len(v_digits) + v_raw_exponent - 1
    raise ValueError("Cannot handle NaN or Infinity.")


def getPrintedValue(
    value: Value, epsilon: float | None = None, exponent_threshold: int = 0
) -> str:
    r"""Create a LaTeX representation for a value with an uncertainty

    The representation uses the \num macro of the siunitx [1] package.
    In particular, the value and the uncertainty are separated by a "+-" string.

    For pasting values into the LaTeX expression, the default f-string formatting of
    Python for floating-point numbers is used. This will almost certainly result in
    undesirably long expressions. To mitigate this, the 'round-mode' option of siunitx
    is recommended.
    This also means that in cases where the uncertainty is many orders of magnitude
    smaller than the value, the value will be displayed as an exact number without an
    uncertainty.

    [1] https://ctan.org/pkg/siunitx

    Parameters
    ----------
    value: Value
        Value to be represented in LaTeX.
    epsilon: float or None
        Threshold for the absolute value. If the value is below the threshold, it will
        be represented as '\num{0.0}'. Default: None, i.e. represent all values as they
        are.
    exponent_threshold: int
        Numbers with an (absolute value of the) exponent above this threshold will be
        displayed in scientific notation, i.e. '\num{1.0 +- 0.1 e3}' instead of
        '\num{1000 +- 100}' for exponent_threshold <= 3. Scientific notation is used if
        any of the value's or the error's exponent is above the threshold, i.e.
        1.0 +- 1000.0 is converted to '\num{0.001 +- 1.0 e3}' for a threshold of 3.
        Note that the 'exponent-mode = threshold' option of siunitx overrides this
        option.
        Default: 0, i.e. use scientific notation for all input.

    Returns
    -------
    str
        LaTeX representation of the value.
    """

    if epsilon is not None:
        if abs(value.val) < epsilon:
            return "\\num{0.0}"

    color = ""
    bigerror = ""
    if value.val > 0.25:
        color = "[color=abovequater]"
    if value.val > 0.5:
        color = "[color=abovehalf]"

    if value.val == 0.0:
        if value.err == 0.0:
            return "\\num{0.0}"
        return "\\num{" "0.0 +- {value.err}" "}"

    if value.err / value.val > 0.2:
        bigerror = "\\bigerror"

    max_exponent = max(get_exponent(value.val), get_exponent(value.err))
    if abs(max_exponent) < exponent_threshold:
        return (
            "\\num" f"{color}" "{" f"{value.val:f} +- {value.err:f}" "}" f"{bigerror}"
        )
    return (
        "\\num"
        f"{color}"
        "{"
        f"{value.val*10**-max_exponent:f} +- "
        f"{value.err*10**-max_exponent:f} e{max_exponent}"
        "}"
        f"{bigerror}"
    )


def _evaluate_scenario(item: tuple[str, Scenario]) -> tuple[str, Scenario]:
    name, scenario = item
    scenario.evaluate()
    return name, scenario


class Case:
    def __init__(self, scenarios: dict[str, Scenario], name: str = ""):
        self.name = name
        self.scenarios = scenarios

    def evaluate(self, parallel: bool = False, max_workers: int | None = None):
        t_start = time()
        n_scenarios = len(self.scenarios)
        if parallel and n_scenarios > 1:
            if max_workers is None:
                max_workers = min(n_scenarios, cpu_count() or 1)
            else:
                max_workers = min(max_workers, n_scenarios)
            print(f"Evaluating {n_scenarios} scenarios with {max_workers} workers.")
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(_evaluate_scenario, item)
                    for item in self.scenarios.items()
                ]
                for n_scenario, future in enumerate(as_completed(futures)):
                    scenario_name, scenario = future.result()
                    self.scenarios[scenario_name] = scenario
                    print(
                        f"Scenario {n_scenario+1:3d}/{n_scenarios:3d}: "
                        f"{(time()-t_start):4.2e} seconds ({scenario_name})"
                    )
            return

        for n_scenario, scenario_name in enumerate(self.scenarios):
            self.scenarios[scenario_name].evaluate()
            print(
                f"Scenario {n_scenario+1:3d}/{n_scenarios:3d}: "
                f"{(time()-t_start):4.2e} seconds ({scenario_name})"
            )

    def toLaTeX(
        self,
        command_output_file_name: Path,
        variable_output_file_name: Path,
        large_error_warnings=True,
    ):
        commands = self.createLaTeXCommands(large_error_warnings=large_error_warnings)
        with open(
            command_output_file_name, "w", encoding="utf-8"
        ) as command_output_file:
            command_output_file.write(commands)
        print(
            f"Created output file '{command_output_file_name}' which defines "
            r"the \rate commands."
        )
        variables = self.createAllVariableLaTeX(
            command_output_file_name=command_output_file_name
        )
        with open(
            variable_output_file_name, "w", encoding="utf-8"
        ) as variable_output_file:
            variable_output_file.write(variables)
        print(
            f"Created output file '{variable_output_file_name}' which calls "
            r"the \rate command for all possible arguments."
            "\n"
            r"It is assumed that the \rate commands are defined in a file "
            f"called '{command_output_file_name}'."
            "\nBuild document with\n\t"
            f"LATEX {variable_output_file_name} && "
            f"LATEX {variable_output_file_name}\n"
            "where LATEX is your LaTeX compiler.\n"
            "(LATEX is invoked twice to build the table of contents.)"
        )

    def createLaTeXCommands(self, large_error_warnings: bool = True) -> str:
        buffer = [
            "% This file is generated by getmax.py. Don't edit it by hand.\n"
            "\\definecolor{abovequater}{HTML}{ff8b00} % for dose rates > 0.25 uSv/h\n"
            "\\definecolor{abovehalf}{HTML}{ff0000}   % for dose rates > 0.5 uSv/h\n"
        ]
        if large_error_warnings:
            buffer.append("\\newcommand\\bigerror{\\textcolor{red}{~(BIG ERROR!)}}\n")
        else:
            buffer.append("\\newcommand\\bigerror{}\n")
        buffer.append(
            "\\NewDocumentCommand\\rate{mmmmg}{%\n"
            "  % 1: scenario\n"
            "  % 2: region\n"
            "  % 3: area\n"
            "  % 4: zone\n"
        )

        for scenario in self.scenarios:
            escaped_scenario = escape_latex(scenario)
            buffer.append(
                r"\ifthenelse{\equal{#1}{"
                f"{escaped_scenario}"
                "}}{% "
                f"{escaped_scenario}\n"
            )
            for region in self.scenarios[scenario].data.sources:
                escaped_region = escape_latex(region)
                buffer.append(
                    r"  \ifthenelse{\equal{#2}{"
                    f"{escaped_region}"
                    "}}{% "
                    f"{escape_latex(self.scenarios[scenario][region].path)}\n"
                )
                for area in self.scenarios[scenario][region].sub_levels:
                    escaped_area = escape_latex(area)
                    buffer.append(
                        r"    \ifthenelse{\equal"
                        "{#3}{" + f"{escaped_area}"
                        "}}{% "
                        f"{escape_latex(self.scenarios[scenario][region][area].path)}\n"
                    )
                    for zone in self.scenarios[scenario][region][area].sub_levels:
                        escaped_zone = escape_latex(zone)
                        buffer.append(
                            r"      \ifthenelse{\equal{#4}{" f"{escaped_zone}" "}}{" f"{
                                getPrintedValue(
                                    value=self.scenarios[scenario][region][area][zone].value
                                )
                            }" "}{" f"% {
                                escape_latex(
                                    self.scenarios[scenario][region][area][zone].path)
                            }\n"
                        )
                    buffer.append(
                        "        "
                        + (
                            "}"
                            * len(
                                self.scenarios[scenario][region]
                                .sub_levels[area]
                                .sub_levels
                            )
                        )
                        + "%\n"
                    )
                    buffer.append("      }{}%\n")
                buffer.append("    }{}%\n")
            for combo in self.scenarios[scenario].data.arbitrary_level_combos:
                path = self.scenarios[scenario][combo].path
                combo_parts = path.split(".")[1:]
                n = len(combo_parts)
                escaped_parts = [escape_latex(p) for p in combo_parts]
                escaped_path = escape_latex(path)
                value_str = getPrintedValue(value=self.scenarios[scenario][combo].value)
                for i, (escaped_part, arg_num) in enumerate(
                    zip(escaped_parts, range(2, n + 2))
                ):
                    indent = "  " * (i + 1)
                    is_last = i == n - 1
                    if is_last:
                        comment = f" {escaped_path}" if n == 1 else ""
                        buffer.append(
                            indent
                            + r"\ifthenelse{\equal{#"
                            + str(arg_num)
                            + "}{"
                            + escaped_part
                            + "}}{"
                            + value_str
                            + "}{}%"
                            + comment
                            + "\n"
                        )
                    elif i == 0:
                        buffer.append(
                            indent
                            + r"\ifthenelse{\equal{#"
                            + str(arg_num)
                            + "}{"
                            + escaped_part
                            + "}}{% "
                            + escaped_path
                            + "\n"
                        )
                    else:
                        buffer.append(
                            indent
                            + r"\ifthenelse{\equal{#"
                            + str(arg_num)
                            + "}{"
                            + escaped_part
                            + "}}{%\n"
                        )
                for i in range(n - 2, -1, -1):
                    buffer.append("  " * (i + 2) + "}{}%\n")
            buffer.append("}{}%\n")
        buffer.append("}%\n")
        return "".join(buffer)

    def createAllVariableLaTeX(
        self, command_output_file_name: Path, large_error_warnings: bool = True
    ) -> str:
        buffer = [
            r"\documentclass{article}"
            "\n\n"
            r"\usepackage[margin=1in]{geometry}"
            "\n"
            r"\usepackage{ifthen}"
            "\n"
            r"\usepackage{siunitx}"
            "\n"
            r"\sisetup{round-mode = uncertainty, round-precision = 1}"
            "\n"
            r"\usepackage{tikz}"
            "\n"
            "\n"
            r"\usepackage{xstring}"
            "\n"
            "\n"
            r"\usepackage{xparse}"
            "\n\n"
            r"\setlength\parindent{0pt}"
            "\n\n"
            r"\input{"
            f"{escape_latex(str(command_output_file_name))}"
            "}\n\n"
            r"\newcommand\print{%"
            "\n"
            r"  \scenario.\region.\area.\zone : \rateval"
            "\n}\n"
            r"\newcommand\printCombo{%"
            "\n"
            r"  \combo : \rateval"
            "\n}\n\n"
            r"\begin{document}"
            "\n"
            r"\tableofcontents"
            "\n"
        ]

        for scenario in self.scenarios:
            escaped_scenario = escape_latex(scenario)
            buffer.append(r"\section{" f"{escaped_scenario}" "}")
            buffer.append(r"\def\scenario{" f"{escaped_scenario}" "}\n")
            for region in self.scenarios[scenario].data.sources:
                escaped_region = escape_latex(region)
                buffer.append(r"\def\region{" f"{escaped_region}" "}\n")
                for area in self.scenarios[scenario][region].sub_levels:
                    escaped_area = escape_latex(area)
                    buffer.append(r"\def\area{" f"{escaped_area}" "}\n")
                    for zone in (
                        self.scenarios[scenario][region].sub_levels[area].sub_levels
                    ):
                        escaped_zone = escape_latex(zone)
                        buffer.append(r"\def\zone{" f"{escaped_zone}" "}\n")
                        buffer.append(
                            r"\def\rateval{\rate{"
                            f"{escaped_scenario}"
                            "}{"
                            f"{escaped_region}"
                            "}{"
                            f"{escaped_area}"
                            "}{"
                            f"{escaped_zone}"
                            "}}\n"
                            r"\print"
                            "\n\n"
                        )
            for combo in self.scenarios[scenario].data.arbitrary_level_combos:
                path = self.scenarios[scenario][combo].path
                combo_parts = path.split(".")[1:]
                while len(combo_parts) < 3:
                    combo_parts.append("")
                escaped_combo_parts = [escape_latex(p) for p in combo_parts]
                buffer.append(r"\def\combo{" f"{escape_latex(path)}" "}\n")
                buffer.append(
                    r"\def\rateval{\rate{"
                    f"{escaped_scenario}"
                    "}{"
                    f"{escaped_combo_parts[0]}"
                    "}{"
                    f"{escaped_combo_parts[1]}"
                    "}{"
                    f"{escaped_combo_parts[2]}"
                    "}}\n"
                    r"\printCombo"
                    "\n\n"
                )
        buffer.append(r"\end{document}")
        return "".join(buffer)

    def __getitem__(self, key: str):
        return self.scenarios[key]
