"""Tests for inventory-policy/scripts/abc_xyz.py with hand-checked numbers.

Fixture (4 periods):
  S1: 10,10,10,10  cost 10 -> value 400, CV 0      -> A X smooth
  S3: 5,15,5,15    cost 2  -> value  80, CV 0.577  -> A Y smooth   (cum share before = 76.9% < 80%)
  S2: 0,20,0,20    cost 1  -> value  40, CV 1.155  -> B Z intermittent (ADI 2, CV² 0)
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "plugins/supply-chain-buddy/skills/inventory-policy/scripts"))

import abc_xyz  # noqa: E402

PERIODS = ["2026-W01", "2026-W02", "2026-W03", "2026-W04"]


def demand(sku, values):
    return [{"sku_id": sku, "period": p, "demand_qty": str(v)} for p, v in zip(PERIODS, values)]


class AbcXyzTests(unittest.TestCase):
    def setUp(self):
        self.rows = demand("S1", [10, 10, 10, 10]) + demand("S2", [0, 20, 0, 20]) + demand("S3", [5, 15, 5, 15])
        self.costs = {"S1": 10.0, "S2": 1.0, "S3": 2.0}

    def run_default(self, rows=None, costs=None, fill=True):
        return abc_xyz.analyse(rows or self.rows, self.costs if costs is None else costs, 0.8, 0.95, 0.5, 1.0, fill)

    def test_classes(self):
        res = self.run_default()
        by = {it["sku_id"]: it for it in res["items"]}
        self.assertEqual(res["basis"], "value")
        self.assertEqual([it["sku_id"] for it in res["items"]], ["S1", "S3", "S2"])
        self.assertEqual((by["S1"]["abc"], by["S1"]["xyz"], by["S1"]["pattern"]), ("A", "X", "smooth"))
        self.assertEqual((by["S3"]["abc"], by["S3"]["xyz"], by["S3"]["pattern"]), ("A", "Y", "smooth"))
        self.assertEqual((by["S2"]["abc"], by["S2"]["xyz"], by["S2"]["pattern"]), ("B", "Z", "intermittent"))
        self.assertAlmostEqual(by["S3"]["cv"], 0.57735, places=4)
        self.assertAlmostEqual(by["S2"]["adi"], 2.0)
        self.assertAlmostEqual(by["S2"]["cv2"], 0.0)
        self.assertAlmostEqual(by["S1"]["share"], 400 / 520)

    def test_matrix(self):
        m = self.run_default()["matrix"]
        self.assertEqual((m["AX"]["count"], m["AY"]["count"], m["BZ"]["count"]), (1, 1, 1))
        self.assertAlmostEqual(m["AX"]["share"] + m["AY"]["share"], 480 / 520)

    def test_volume_basis_without_costs(self):
        res = self.run_default(costs={})
        self.assertEqual(res["basis"], "volume")

    def test_missing_periods_filled_with_zero(self):
        rows = self.rows + [{"sku_id": "S4", "period": "2026-W01", "demand_qty": "8"},
                            {"sku_id": "S4", "period": "2026-W03", "demand_qty": "8"}]
        res = abc_xyz.analyse(rows, {}, 0.8, 0.95, 0.5, 1.0, True)
        s4 = next(it for it in res["items"] if it["sku_id"] == "S4")
        self.assertEqual(s4["periods"], 4)
        self.assertAlmostEqual(s4["mean_demand"], 4.0)
        self.assertEqual(s4["pattern"], "intermittent")
        res2 = abc_xyz.analyse(rows, {}, 0.8, 0.95, 0.5, 1.0, False)
        s4b = next(it for it in res2["items"] if it["sku_id"] == "S4")
        self.assertEqual(s4b["periods"], 2)

    def test_lumpy_and_erratic(self):
        self.assertEqual(abc_xyz.classify_pattern(1.0, 0.6), "erratic")
        self.assertEqual(abc_xyz.classify_pattern(2.0, 0.6), "lumpy")
        self.assertEqual(abc_xyz.classify_pattern(None, None), "no demand")

    def test_missing_cost_for_some_sku_fails(self):
        with self.assertRaises(SystemExit):
            abc_xyz.analyse(self.rows, {"S1": 1.0}, 0.8, 0.95, 0.5, 1.0, True)

    def test_markdown_renders(self):
        md = abc_xyz.to_markdown(self.run_default())
        self.assertIn("| **A** |", md)
        self.assertIn("intermittent", md)


if __name__ == "__main__":
    unittest.main()
