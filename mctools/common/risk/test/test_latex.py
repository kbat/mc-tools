import unittest


from mctools.common.risk.case import get_exponent, getPrintedValue
from mctools.common.risk.value import UnknownValue, Value


class TestLaTeX(unittest.TestCase):
    def test_unknown_value(self):
        self.assertEqual(getPrintedValue(value=UnknownValue()), "\\num{0.0}")
        self.assertEqual(getPrintedValue(value=Value(0.0, err=0.0)), "\\num{0.0}")

    def test_value_range(self):
        self.assertEqual(
            getPrintedValue(value=Value(0.1, err=0.01), exponent_threshold=3),
            "\\num{0.100000 +- 0.010000}",
        )
        self.assertEqual(
            getPrintedValue(value=Value(0.3, err=0.01), exponent_threshold=3),
            "\\num[color=abovequater]{0.300000 +- 0.010000}",
        )
        self.assertEqual(
            getPrintedValue(value=Value(0.6, err=0.01), exponent_threshold=3),
            "\\num[color=abovehalf]{0.600000 +- 0.010000}",
        )

    def test_large_error(self):
        self.assertEqual(
            getPrintedValue(value=Value(0.1, err=0.019), exponent_threshold=3),
            "\\num{0.100000 +- 0.019000}",
        )
        self.assertEqual(
            getPrintedValue(value=Value(0.1, err=0.021), exponent_threshold=3),
            "\\num{0.100000 +- 0.021000}\\bigerror",
        )

    def test_exponent(self):
        for i in range(-3, 3):
            self.assertEqual(get_exponent(10**i), i)

        with self.assertRaisesRegex(ValueError, "Cannot handle NaN or Infinity."):
            get_exponent(float("nan"))
        with self.assertRaisesRegex(ValueError, "Cannot handle NaN or Infinity."):
            get_exponent(float("inf"))
        with self.assertRaisesRegex(ValueError, "Cannot handle NaN or Infinity."):
            get_exponent(float("-inf"))

    def test_exponent_threshold(self):
        self.assertEqual(
            getPrintedValue(value=Value(1e-2, err=1e-3), exponent_threshold=3),
            "\\num{0.010000 +- 0.001000}",
        )
        self.assertEqual(
            getPrintedValue(value=Value(1e-3, err=1e-4)),
            "\\num{1.000000 +- 0.100000 e-3}",
        )

        self.assertEqual(
            getPrintedValue(value=Value(1e2, err=1e1), exponent_threshold=3),
            "\\num[color=abovehalf]{100.000000 +- 10.000000}",
        )
        self.assertEqual(
            getPrintedValue(value=Value(1e3, err=1e2)),
            "\\num[color=abovehalf]{1.000000 +- 0.100000 e3}",
        )
        self.assertEqual(
            getPrintedValue(value=Value(1e0, err=1e-2)),
            "\\num[color=abovehalf]{1.000000 +- 0.010000 e0}",
        )
        self.assertEqual(
            getPrintedValue(value=Value(1e6, err=1e-6)),
            "\\num[color=abovehalf]{1.000000 +- 0.000000 e6}",
        )

    def test_latex(self):
        values = (
            (UnknownValue(), r"\verb|UnknownValue()|"),
            (Value(0.0, 0.0), r"\verb|Value(0.0, 0.0)|"),
            (Value(0.1, 0.01), "No special case"),
            (Value(0.1, 0.021), "Large Error"),
            (Value(0.3, 0.01), r"Dose $>$ 0.25"),
            (Value(0.3, 0.07), r"Dose $>$ 0.25 + Large Error"),
            (Value(0.6, 0.01), r"Dose $>$ 0.5"),
            (Value(0.6, 0.15), r"Dose $>$ 0.5 + Large Error"),
            (Value(1.2345e-5, 0.012345e-5), "Exponent below lower limit"),
            (Value(1.2345e-4, 0.012345e-4), "Exponent within [-5,3]"),
            (Value(1.2345e-3, 0.012345e-3), "Exponent within [-5,3]"),
            (Value(1.2345e-2, 0.012345e-2), "Exponent within [-5,3]"),
            (Value(1.2345e-1, 0.012345e-1), "Exponent within [-5,3]"),
            (Value(1.2345e0, 0.012345e0), "Exponent within [-5,3]"),
            (Value(1.2345e1, 0.012345e1), "Exponent within [-5,3]"),
            (Value(1.2345e2, 0.012345e2), "Exponent within [-5,3]"),
            (Value(1.2345e3, 0.012345e3), "Exponent above upper limit"),
            (Value(1.2345e0, 1.2345e3), "Error exponent above upper limit"),
            (Value(1.2345e1, 1.2345e3), "Error exponent above upper limit"),
            (Value(1.2345e2, 1.2345e3), "Error exponent above upper limit"),
            (Value(1.2345e3, 1.2345e3), "Both exponents above upper limit"),
            (Value(1.2345e0, 1.2345e-6), "Error exponent below lower limit"),
            (Value(1.2345e-1, 1.2345e-6), "Error exponent below lower limit"),
            (Value(1.2345e-2, 1.2345e-6), "Error exponent below lower limit"),
            (Value(1.2345e-3, 1.2345e-6), "Error exponent below lower limit"),
            (Value(1.2345e-4, 1.2345e-6), "Error exponent below lower limit"),
            (Value(1.2345e-5, 1.2345e-6), "Both exponents below lower limit"),
            (Value(0.12345, 0.12345), "Value = Error"),
            (Value(0.12345, 1.2345e-2), "Value = Error x $10^{1}$"),
            (Value(0.12345, 1.2345e-3), "Value = Error x $10^{2}$"),
            (Value(0.12345, 1.2345e-4), "Value = Error x $10^{3}$"),
            (Value(0.12345, 1.2345e-5), "Value = Error x $10^{4}$"),
            (Value(0.12345, 1.2345e-6), "Value = Error x $10^{5}$"),
            (Value(0.12345, 1.2345e-7), "Value = Error x $10^{6}$"),
            (Value(0.12345, 1.2345e-8), "Value = Error x $10^{7}$"),
        )

        buf = (
            r"\documentclass{article}"
            "\n\n"
            r"\usepackage[a4paper, landscape, margin=2cm]{geometry}"
            "\n"
            r"\usepackage{siunitx}"
            "\n"
            r"\sisetup{round-mode = uncertainty, round-precision = 1}"
            "\n"
            r"\sisetup{exponent-mode = threshold, exponent-thresholds = -5:3}"
            "\n"
            r"\usepackage{xcolor}"
            "\n"
            r"\definecolor{abovequater}{HTML}{ff8b00}"
            "\n"
            r"\definecolor{abovehalf}{HTML}{ff0000}"
            "\n"
            r"\newcommand\bigerror{}"
            "\n\n"
            r"\begin{document}"
            "\n\n"
            r"\begin{tabular}{ccccc}"
            "\n"
            "\tValue & Uncertainty & Code & Result & Comment \\\\\n\t"
            r"\hline"
            "\n"
        )
        for value in values:
            result = getPrintedValue(value[0])
            buf += (
                "\t"
                r"\verb|"
                f"{value[0].val}| & "
                r"\verb|"
                f"{value[0].err}| & "
                r"\verb|"
                f"{result}| & "
                f"{result} & "
                f"{value[1]}"
                "\\\\\n"
            )
        buf += r"\end{tabular}" "\n\n" r"\end{document}" "\n"

        with open("test_latex.tex", "w", encoding="utf-8") as output_file:
            output_file.write(buf)

        print(
            "The 'test_latex' unit test has created an output file 'test_latex.tex'"
            "which demonstrates how different input is formatted in a LaTeX document."
            "\n\nBuild document with\n\tLATEX test_latex.tex\nwhere LATEX is your "
            "LATEX compiler.\nNote that the LaTeX packages 'geometry', 'siunitx', and "
            "'xcolor' are required."
        )
