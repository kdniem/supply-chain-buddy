"""Tests for demand-planning-review/scripts/forecast_accuracy.py with hand-checked numbers.

SKU A: actuals 10, 20, 30, 40; final forecast 12, 18, 33, 40; statistical forecast = actuals (perfect).
  errors F-A = 2, -2, 3, 0 -> bias = 3/100 = +3%, wMAPE = 7/100 = 7%, MAE = 1.75,
  MAPE = (0.2 + 0.1 + 0.1 + 0) / 4 = 10%, RMSE = sqrt(17/4) = 2.0616,
  MASE scale = mean |diff| = 10 -> MASE = 0.175, TS = 3 / 1.75 = 1.714
  Naive lag 1 on P2..P4: |10-20| + |20-30| + |30-40| = 30 over sum A 90 -> 33.33%;
  forecast on the same periods: 2 + 3 + 0 = 5 / 90 = 5.56% -> FVA vs naive = +27.78 pts
  FVA of the step from stat (0%) to final (7%) = -7 pts
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins/supply-chain-buddy/skills/demand-planning-review/scripts"))

import forecast_accuracy as fa  # noqa: E402

P = ["P1", "P2", "P3", "P4"]


def actuals(sku, vals):
    return [{"sku_id": sku, "period": p, "demand_qty": str(v)} for p, v in zip(P, vals)]


def forecasts(sku, final, stat):
    return [{"sku_id": sku, "period": p, "forecast_qty": str(f), "stat_forecast_qty": str(s)}
            for p, f, s in zip(P, final, stat)]


class ForecastAccuracyTests(unittest.TestCase):
    def setUp(self):
        self.res = fa.analyse(actuals("A", [10, 20, 30, 40]), forecasts("A", [12, 18, 33, 40], [10, 20, 30, 40]),
                              "forecast_qty", "stat_forecast_qty", 1, {}, "category", None, None, 0.1)
        self.a = self.res["items"][0]

    def test_core_metrics(self):
        a = self.a
        self.assertAlmostEqual(a["bias"], 0.03)
        self.assertAlmostEqual(a["wmape"], 0.07)
        self.assertAlmostEqual(a["mae"], 1.75)
        self.assertAlmostEqual(a["mape"], 0.10)
        self.assertAlmostEqual(a["rmse"], 2.0616, places=4)
        self.assertAlmostEqual(a["mase"], 0.175)
        self.assertAlmostEqual(a["tracking_signal"], 3 / 1.75)

    def test_fva(self):
        self.assertAlmostEqual(self.a["naive_wmape"], 30 / 90)
        self.assertAlmostEqual(self.a["fva_vs_naive_pts"], (30 - 5) / 90 * 100)
        self.assertAlmostEqual(self.a["fva_vs_compare_pts"], -7.0)
        self.assertAlmostEqual(self.res["total"]["fva_vs_compare_pts"], -7.0)

    def test_mape_excludes_zero_actuals(self):
        res = fa.analyse(actuals("Z", [0, 10, 0, 10]), forecasts("Z", [1, 12, 1, 8], [0, 0, 0, 0]),
                         "forecast_qty", None, 1, {}, "category", None, None, 0.1)
        z = res["items"][0]
        self.assertEqual(z["mape_zero_periods_excluded"], 2)
        self.assertAlmostEqual(z["mape"], 0.2)
        self.assertAlmostEqual(z["wmape"], 6 / 20)

    def test_value_weighting_and_groups(self):
        acts = actuals("A", [10, 20, 30, 40]) + actuals("B", [100, 100, 100, 100])
        fcs = forecasts("A", [12, 18, 33, 40], [0] * 4) + forecasts("B", [150, 150, 150, 150], [0] * 4)
        items = {"A": {"unit_cost": 10.0, "group": "G1"}, "B": {"unit_cost": 1.0, "group": "G2"}}
        res = fa.analyse(acts, fcs, "forecast_qty", None, 1, items, "category", None, None, 0.1)
        self.assertEqual(res["weighting"], "value (unit_cost)")
        # value-weighted wMAPE = (7*10 + 200*1) / (100*10 + 400*1) = 270 / 1400
        self.assertAlmostEqual(res["total"]["wmape"], 270 / 1400)
        self.assertAlmostEqual(res["by_group"]["G2"]["bias"], 0.5)
        b = next(r for r in res["items"] if r["sku_id"] == "B")
        # constant +50 error over 4 periods: TS = 200 / 50 = 4, not > 4 -> not flagged (boundary)
        self.assertAlmostEqual(b["tracking_signal"], 4.0)
        self.assertFalse(b["bias_flag"])

    def test_window_filter(self):
        res = fa.analyse(actuals("A", [10, 20, 30, 40]), forecasts("A", [12, 18, 33, 40], [0] * 4),
                         "forecast_qty", None, 1, {}, "category", "P3", None, 0.1)
        self.assertEqual(res["items"][0]["n"], 2)

    def test_no_overlap_fails(self):
        with self.assertRaises(SystemExit):
            fa.analyse(actuals("A", [1, 2, 3, 4]), forecasts("B", [1, 2, 3, 4], [0] * 4),
                       "forecast_qty", None, 1, {}, "category", None, None, 0.1)

    def test_markdown(self):
        md = fa.to_markdown(self.res)
        self.assertIn("FVA of the step", md)


if __name__ == "__main__":
    unittest.main()
