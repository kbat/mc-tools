import unittest

from mctools.common.risk.test.input_histogram import create_test_histogram


class TestHistogram(unittest.TestCase):
    def test_histogram(self):
        hist = create_test_histogram()

        self.assertEqual(hist.GetBinContent(1, 1, 1), 0.0)
        self.assertEqual(hist.GetBinContent(1, 1, 2), 1.0)
        self.assertEqual(hist.GetBinContent(1, 2, 1), 2.0)
        self.assertEqual(hist.GetBinContent(1, 2, 2), 3.0)
        self.assertEqual(hist.GetBinContent(2, 1, 1), 4.0)
        self.assertEqual(hist.GetBinContent(2, 1, 2), 5.0)
        self.assertEqual(hist.GetBinContent(2, 2, 1), 6.0)
        self.assertEqual(hist.GetBinContent(2, 2, 2), 7.0)

        self.assertEqual(hist.GetXaxis().GetBinLowEdge(1), -1.0)
        self.assertEqual(hist.GetXaxis().GetBinCenter(1), -0.5)
        self.assertEqual(hist.GetXaxis().GetBinUpEdge(1), 0.0)
        self.assertEqual(hist.GetXaxis().GetBinLowEdge(2), 0.0)
        self.assertEqual(hist.GetXaxis().GetBinCenter(2), 0.5)
        self.assertEqual(hist.GetXaxis().GetBinUpEdge(2), 1.0)

        self.assertEqual(hist.GetYaxis().GetBinLowEdge(1), -1.0)
        self.assertEqual(hist.GetYaxis().GetBinCenter(1), -0.5)
        self.assertEqual(hist.GetYaxis().GetBinUpEdge(1), 0.0)
        self.assertEqual(hist.GetYaxis().GetBinLowEdge(2), 0.0)
        self.assertEqual(hist.GetYaxis().GetBinCenter(2), 0.5)
        self.assertEqual(hist.GetYaxis().GetBinUpEdge(2), 1.0)

        self.assertEqual(hist.GetZaxis().GetBinLowEdge(1), -1.0)
        self.assertEqual(hist.GetZaxis().GetBinCenter(1), -0.5)
        self.assertEqual(hist.GetZaxis().GetBinUpEdge(1), 0.0)
        self.assertEqual(hist.GetZaxis().GetBinLowEdge(2), 0.0)
        self.assertEqual(hist.GetZaxis().GetBinCenter(2), 0.5)
        self.assertEqual(hist.GetZaxis().GetBinUpEdge(2), 1.0)
