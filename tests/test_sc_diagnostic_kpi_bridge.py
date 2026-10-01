"""Tests for sc-diagnostic/scripts/kpi_bridge.py with a hand-checked shift-share example.

Ratio KPI (fill rate):
  G1: base 90/100, compare 60/100   (rate 0.90 -> 0.60)
  G2: base 95/100, compare 190/200  (rate 0.95 -> 0.95)
  R1 = 185/200 = 0.925, R2 = 250/300 = 0.8333, delta = -0.091667, R¯ = 0.879167
  weights: G1 0.5 -> 1/3, G2 0.5 -> 2/3
  G1 rate = (0.60 - 0.90) * (0.5 + 1/3)/2 = -0.125;  G1 mix = (1/3 - 0.5) * (0.75 - 0.879167) = +0.021528
  G2 rate = 0;                                     G2 mix = (2/3 - 0.5) * (0.95 - 0.879167) = +0.011806
  sum = -0.091667 = delta
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins/supply-chain-buddy/skills/sc-diagnostic/scripts"))

import kpi_bridge as kb  # noqa: E402

ROWS = [
    {"period": "B1", "grp": "G1", "num": "90", "den": "100"},
    {"period": "B1", "grp": "G2", "num": "95", "den": "100"},
    {"period": "C1", "grp": "G1", "num": "60", "den": "100"},
    {"period": "C1", "grp": "G2", "num": "190", "den": "200"},
]


class RatioBridgeTests(unittest.TestCase):
    def setUp(self):
        self.res = kb.bridge(ROWS, "period", ("B1", "B9"), ("C1", "C9"), "grp", ("num", "den"), None, "sum", None)
        self.g = {x["group"]: x for x in self.res["groups"]}

    def test_totals(self):
        self.assertAlmostEqual(self.res["base_kpi"], 0.925)
        self.assertAlmostEqual(self.res["compare_kpi"], 250 / 300)
        self.assertAlmostEqual(self.res["delta"], 250 / 300 - 0.925)

    def test_decomposition(self):
        self.assertAlmostEqual(self.g["G1"]["rate_effect"], -0.125)
        self.assertAlmostEqual(self.g["G1"]["mix_effect"], 0.021528, places=5)
        self.assertAlmostEqual(self.g["G2"]["rate_effect"], 0.0)
        self.assertAlmostEqual(self.g["G2"]["mix_effect"], 0.011806, places=5)
        self.assertAlmostEqual(self.res["check_sum"], self.res["delta"])

    def test_sorted_by_abs_contribution(self):
        self.assertEqual(self.res["groups"][0]["group"], "G1")

    def test_multiplier(self):
        rows = [dict(r, cost="2") for r in ROWS]
        res = kb.bridge(rows, "period", ("B1", "B9"), ("C1", "C9"), "grp", ("num", "den"), None, "sum", "cost")
        self.assertAlmostEqual(res["delta"], self.res["delta"])  # ratio invariant to a constant multiplier


class ValueBridgeTests(unittest.TestCase):
    def test_mean_aggregation_and_shares(self):
        rows = [
            {"period": "B1", "cat": "X", "inv": "100"}, {"period": "B2", "cat": "X", "inv": "300"},
            {"period": "B1", "cat": "Y", "inv": "50"},  # Y missing in B2 -> counts as 0
            {"period": "C1", "cat": "X", "inv": "200"}, {"period": "C1", "cat": "Y", "inv": "150"},
        ]
        res = kb.bridge(rows, "period", ("B1", "B2"), ("C1", "C1"), "cat", None, "inv", "mean", None)
        g = {x["group"]: x for x in res["groups"]}
        self.assertAlmostEqual(g["X"]["base_value"], 200.0)   # (100 + 300) / 2
        self.assertAlmostEqual(g["Y"]["base_value"], 25.0)    # (50 + 0) / 2
        self.assertAlmostEqual(res["delta"], 350 - 225)
        self.assertAlmostEqual(g["Y"]["share_of_delta"], 125 / 125)
        self.assertAlmostEqual(g["X"]["contribution"], 0.0)

    def test_empty_window_fails(self):
        with self.assertRaises(SystemExit):
            kb.bridge(ROWS, "period", ("X1", "X9"), ("C1", "C9"), None, ("num", "den"), None, "sum", None)

    def test_markdown(self):
        res = kb.bridge(ROWS, "period", ("B1", "B9"), ("C1", "C9"), "grp", ("num", "den"), None, "sum", None)
        self.assertIn("rate effect", kb.to_markdown(res, None))


if __name__ == "__main__":
    unittest.main()
