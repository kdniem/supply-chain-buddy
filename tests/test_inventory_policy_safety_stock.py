"""Tests for inventory-policy/scripts/safety_stock.py with hand-checked numbers.

Worked example (also used in references/methods.md):
  d = 100 units/week, sigma_d = 30, L = 2 weeks, sigma_L = 0.5 weeks
  sigma_P = sqrt(2*30^2 + 100^2*0.5^2) = sqrt(1800 + 2500) = sqrt(4300) = 65.574
  95% CSL: z = 1.6449 -> SS = 107.86, ROP = 200 + 107.86 = 307.86
  98% fill rate, Q = 400: G(k) = 0.02*400/65.574 = 0.12200 -> k ~ 0.7916 (between G(0.79)=0.12234
  and G(0.80)=0.12021) -> SS ~ 51.9
"""
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins/supply-chain-buddy/skills/inventory-policy/scripts"))

import safety_stock as ss  # noqa: E402


def row(**kw):
    return {k: str(v) for k, v in kw.items()}


class LossFunctionTests(unittest.TestCase):
    def test_known_values(self):
        self.assertAlmostEqual(ss.loss(0.0), 0.398942, places=5)
        self.assertAlmostEqual(ss.loss(0.8), 0.120207, places=5)
        self.assertAlmostEqual(ss.loss(1.6449), 0.020893, places=5)

    def test_inverse(self):
        for k in (-1.0, 0.0, 0.79, 2.5):
            self.assertAlmostEqual(ss.k_for_fill_rate(ss.loss(k)), k, places=6)


class SafetyStockTests(unittest.TestCase):
    def test_csl_continuous_review(self):
        res = ss.compute([row(sku_id="A", mean_demand=100, std_demand=30, lead_time=2, lead_time_std=0.5,
                              order_qty=400)], 0.95, "csl", None, None, {})
        r = res["items"][0]
        self.assertAlmostEqual(r["sigma_p"], math.sqrt(4300), places=6)
        self.assertAlmostEqual(r["safety_stock"], 107.86, places=2)
        self.assertAlmostEqual(r["reorder_point"], 307.86, places=2)
        self.assertAlmostEqual(r["implied_fill_rate"], 0.99657, places=4)
        self.assertAlmostEqual(r["cycle_stock"], 200.0)

    def test_fill_rate_method(self):
        res = ss.compute([row(sku_id="A", mean_demand=100, std_demand=30, lead_time=2, lead_time_std=0.5,
                              order_qty=400, service_level=98)], 0.95, "fill-rate", None, None, {})
        r = res["items"][0]
        self.assertAlmostEqual(r["k"], 0.7916, places=3)
        self.assertAlmostEqual(r["safety_stock"], 51.91, delta=0.05)

    def test_periodic_review_order_up_to(self):
        res = ss.compute([row(sku_id="B", mean_demand=100, std_demand=30, lead_time=2, review_period=1)],
                         0.95, "csl", None, None, {})
        r = res["items"][0]
        self.assertAlmostEqual(r["sigma_p"], math.sqrt(2700), places=6)
        self.assertAlmostEqual(r["safety_stock"], 85.47, places=2)
        self.assertAlmostEqual(r["order_up_to"], 385.47, places=2)
        self.assertAlmostEqual(r["order_qty"], 100.0)  # d * R

    def test_days_conversion_requires_period_days(self):
        with self.assertRaises(SystemExit):
            ss.compute([row(sku_id="A", mean_demand=10, std_demand=3, lead_time_days=14)], 0.95, "csl", None, None, {})
        res = ss.compute([row(sku_id="A", mean_demand=10, std_demand=3, lead_time_days=14)], 0.95, "csl", 7, None, {})
        self.assertAlmostEqual(res["items"][0]["lead_time"], 2.0)

    def test_forecast_error_overrides_demand_std(self):
        res = ss.compute([row(sku_id="A", mean_demand=100, std_demand=60, forecast_error_std=20, lead_time=1)],
                         0.95, "csl", None, None, {})
        r = res["items"][0]
        self.assertEqual(r["sigma_source"], "forecast error")
        self.assertAlmostEqual(r["safety_stock"], 1.644854 * 20, places=3)

    def test_health_classification_and_values(self):
        params = [
            row(sku_id="LOW", mean_demand=100, std_demand=30, lead_time=2, order_qty=400, unit_cost=2, on_hand_qty=50),
            row(sku_id="OK", mean_demand=100, std_demand=30, lead_time=2, order_qty=400, unit_cost=2, on_hand_qty=300),
            row(sku_id="HIGH", mean_demand=100, std_demand=30, lead_time=2, order_qty=400, unit_cost=2, on_hand_qty=1000),
        ]
        res = ss.compute(params, 0.95, "csl", None, None, {})
        health = {r["sku_id"]: r["health"] for r in res["items"]}
        self.assertEqual(health, {"LOW": "below_ss", "OK": "ok", "HIGH": "excess"})
        high = res["items"][2]
        sst = 1.644854 * math.sqrt(2 * 900)
        self.assertAlmostEqual(high["excess_qty"], 1000 - (sst + 400), places=3)
        self.assertAlmostEqual(res["summary"]["excess_value"], high["excess_qty"] * 2, places=3)
        self.assertEqual(res["summary"]["health_counts"], {"below_ss": 1, "ok": 1, "excess": 1})

    def test_history_and_pattern_flag(self):
        hist = {"A": {"mean": 10.0, "std": 15.0, "periods": 52}}
        res = ss.compute([row(sku_id="A", lead_time=1)], 0.9, "csl", None, hist, {"A": "lumpy"})
        r = res["items"][0]
        self.assertAlmostEqual(r["mean_demand"], 10.0)
        self.assertIn("lumpy", r["notes"])

    def test_invalid_service_level(self):
        with self.assertRaises(SystemExit):
            ss.compute([row(sku_id="A", mean_demand=1, std_demand=1, lead_time=1, service_level=100)],
                       0.95, "csl", None, None, {})

    def test_markdown_renders(self):
        res = ss.compute([row(sku_id="A", mean_demand=100, std_demand=30, lead_time=2, order_qty=400,
                              on_hand_qty=10, unit_cost=1)], 0.95, "csl", None, None, {})
        md = ss.to_markdown(res)
        self.assertIn("| A |", md)
        self.assertIn("below_ss", md)


if __name__ == "__main__":
    unittest.main()
