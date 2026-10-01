"""Tests for demand-planning-review/scripts/method_backtest.py (hand-checked recursions)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins/supply-chain-buddy/skills/demand-planning-review/scripts"))

import method_backtest as mb  # noqa: E402


class RecursionTests(unittest.TestCase):
    def test_moving_average(self):
        self.assertEqual(mb.fc_ma(4)([1, 2, 3, 4, 5]), [1, 1.5, 2, 2.5, 3.5])

    def test_ses(self):
        # level starts at y0 = 10; after 10 -> 10; after 20 -> 0.5*20 + 0.5*10 = 15
        self.assertEqual(mb.fc_ses([10, 20], 0.5), [10, 15])

    def test_croston_sba(self):
        # first demand at index 1: z = 4, p = 2 -> SBA = (1 - 0.25) * 4 / 2 = 1.5; next demand after interval 2 keeps p = 2
        self.assertEqual(mb.fc_croston_sba([0, 4, 0, 4], 0.5), [0.0, 1.5, 1.5, 1.5])

    def test_tsb(self):
        # prob0 = 0.5, size0 = 4; v=0 -> p=.25 (1.0); v=4 -> p=.625 (2.5); v=0 -> p=.3125 (1.25); v=4 -> p=.65625 (2.625)
        out = mb.fc_tsb([0, 4, 0, 4], (0.5, 0.5))
        for got, exp in zip(out, [1.0, 2.5, 1.25, 2.625]):
            self.assertAlmostEqual(got, exp)

    def test_pattern(self):
        self.assertEqual(mb.pattern([5, 5, 5, 5])[2], "smooth")
        self.assertEqual(mb.pattern([0, 0, 10, 0, 0, 10])[2], "intermittent")
        self.assertEqual(mb.pattern([0, 0, 1, 0, 0, 30])[2], "lumpy")


class BacktestTests(unittest.TestCase):
    def test_constant_series_any_method_perfect(self):
        y = [10.0] * 40
        r = mb.backtest_series(y, 1, 8)
        self.assertEqual(r["best"], "naive")  # all MAE 0 -> simplest wins
        self.assertEqual(r["methods"]["ses"]["mae"], 0.0)

    def test_intermittent_prefers_smoothing_over_naive(self):
        y = ([0, 0, 0, 12] * 13)[:52]
        r = mb.backtest_series([float(v) for v in y], 1, 13)
        self.assertEqual(r["pattern"], "intermittent")
        self.assertNotEqual(r["best"], "naive")
        self.assertLess(r["methods"]["croston_sba"]["mae"], r["methods"]["naive"]["mae"])

    def test_run_requires_enough_periods(self):
        rows = [{"sku_id": "A", "period": f"P{i:02d}", "demand_qty": "1"} for i in range(10)]
        with self.assertRaises(SystemExit):
            mb.run(rows, 1, 13)

    def test_run_and_markdown(self):
        rows = [{"sku_id": s, "period": f"P{i:02d}", "demand_qty": str(v)}
                for s, base in (("A", 10), ("B", 0)) for i, v in enumerate([base + (i % 3) for i in range(30)])]
        res = mb.run(rows, 1, 8)
        self.assertEqual(len(res["items"]), 2)
        self.assertIn("Best method by demand pattern", mb.to_markdown(res))


if __name__ == "__main__":
    unittest.main()
