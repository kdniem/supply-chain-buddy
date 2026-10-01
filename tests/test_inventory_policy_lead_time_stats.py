"""Tests for inventory-policy/scripts/lead_time_stats.py with hand-checked numbers.

Fixture: SKU A from supplier S1. Orders in January take 14, 14, 16 days; orders in June take 28, 30.
With --recent-days 60 (cutoff = 2026-06-20 - 60 days = 2026-04-21):
  before = [14, 14, 16] -> mean 14.667; recent = [28, 30] -> mean 29.0; drift = 29/14.667 - 1 = +97.7%
  all = [14,14,16,28,30] -> mean 20.4, sample std = sqrt(251.2/4) = 7.925
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins/supply-chain-buddy/skills/inventory-policy/scripts"))

import lead_time_stats as lts  # noqa: E402

ROWS = [
    {"sku_id": "A", "supplier_id": "S1", "order_date": "2026-01-05", "received_date": "2026-01-19", "promised_date": "2026-01-19"},
    {"sku_id": "A", "supplier_id": "S1", "order_date": "2026-01-12", "received_date": "2026-01-26", "promised_date": "2026-01-26"},
    {"sku_id": "A", "supplier_id": "S1", "order_date": "2026-01-19", "received_date": "2026-02-04", "promised_date": "2026-02-02"},
    {"sku_id": "A", "supplier_id": "S1", "order_date": "2026-06-01", "received_date": "2026-06-29", "promised_date": "2026-06-15"},
    {"sku_id": "A", "supplier_id": "S1", "order_date": "2026-06-20", "received_date": "2026-07-20", "promised_date": "2026-07-04"},
    {"sku_id": "A", "supplier_id": "S1", "order_date": "2026-06-22", "received_date": "", "promised_date": "2026-07-06"},
]


class LeadTimeTests(unittest.TestCase):
    def test_stats_and_drift(self):
        res = lts.analyse(ROWS, 60, 0.2, min_n=2)
        self.assertEqual(res["receipts"], 5)
        self.assertEqual(res["open_orders_ignored"], 1)
        a = res["by_sku"][0]
        self.assertAlmostEqual(a["all"]["mean"], 20.4)
        self.assertAlmostEqual(a["all"]["std"], 7.925, places=3)
        self.assertAlmostEqual(a["before"]["mean"], 44 / 3)
        self.assertAlmostEqual(a["recent"]["mean"], 29.0)
        self.assertAlmostEqual(a["drift"], 29 / (44 / 3) - 1)
        self.assertTrue(a["drift_flag"])
        self.assertAlmostEqual(a["promised_mean"], 14.0)
        self.assertEqual(res["by_supplier"][0]["supplier_id"], "S1")

    def test_no_drift_when_stable(self):
        stable = [dict(r, received_date=r["promised_date"]) for r in ROWS[:5]]
        res = lts.analyse(stable, 60, 0.2)
        self.assertFalse(res["by_sku"][0]["drift_flag"])

    def test_bad_date_fails(self):
        with self.assertRaises(SystemExit):
            lts.analyse([{"sku_id": "A", "order_date": "05/01/2026", "received_date": "2026-01-19"}], 60, 0.2)

    def test_markdown(self):
        md = lts.to_markdown(lts.analyse(ROWS, 60, 0.2, min_n=2))
        self.assertIn("Drift flagged for 1 SKU", md)

    def test_min_n_suppresses_flag(self):
        res = lts.analyse(ROWS, 60, 0.2, min_n=3)
        self.assertFalse(res["by_sku"][0]["drift_flag"])  # only 2 recent receipts


if __name__ == "__main__":
    unittest.main()
