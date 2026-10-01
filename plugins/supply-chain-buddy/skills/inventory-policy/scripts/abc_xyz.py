#!/usr/bin/env python3
"""ABC/XYZ segmentation plus demand-pattern classification (ADI / CV²).

Input 1: demand history CSV (header required)
    sku_id        item identifier
    period        period label that sorts chronologically (e.g. 2026-W01, 2026-01, 2026-01-05)
    demand_qty    demand in units for that period (prefer customer demand over shipments)

Input 2 (optional, --costs): item master CSV
    sku_id, unit_cost       enables ABC on consumption VALUE (recommended); otherwise ABC uses volume

Method
    ABC  Items sorted by value (or volume) descending. An item is A while the cumulative share
         BEFORE adding it is below --a-cut (so the item crossing the threshold is still A),
         B likewise for --b-cut, else C. Items without demand are C.          [SPT-2017]
    XYZ  Coefficient of variation CV = std / mean of per-period demand (sample std, n-1),
         X if CV <= --x-cut, Y if CV <= --y-cut, else Z. Thresholds are a design choice
         (defaults 0.5 / 1.0 are a common rule of thumb).
    Pattern  ADI = periods / periods with demand; CV² of NON-ZERO demand sizes.
         smooth ADI<1.32 & CV²<0.49 | erratic ADI<1.32 & CV²>=0.49 |
         intermittent ADI>=1.32 & CV²<0.49 | lumpy ADI>=1.32 & CV²>=0.49     [SB-2005]

Periods missing for a SKU are treated as zero demand (the period list is the union over all
SKUs). Use --no-fill-zeros if missing rows mean "item not yet active".

Usage
    python3 abc_xyz.py demand.csv [--costs items.csv] [--a-cut 0.8 --b-cut 0.95]
                       [--x-cut 0.5 --y-cut 1.0] [--json] [--out stats.csv]

Standard library only. Deterministic. Prints a Markdown report (default) or JSON.
--out writes per-SKU statistics (incl. mean_demand, std_demand) as CSV, which
safety_stock.py can use directly.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from typing import Dict, List, Optional

ADI_CUT = 1.32
CV2_CUT = 0.49


def fail(msg: str) -> None:
    sys.exit(f"Input error: {msg}")


def read_csv(path: str, required: List[str]) -> List[Dict[str, str]]:
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fields = [f.strip() for f in (reader.fieldnames or [])]
            reader.fieldnames = fields
            missing = [c for c in required if c not in fields]
            if missing:
                fail(f"{path}: missing column(s) {missing}. Found: {fields}")
            return list(reader)
    except FileNotFoundError:
        fail(f"file not found: {path}")
    return []


def to_float(raw: str, column: str, row: int, path: str) -> float:
    try:
        value = float(str(raw).strip().replace(",", "")) if str(raw).strip() != "" else 0.0
    except ValueError:
        fail(f"{path} row {row}: column '{column}' is not a number: {raw!r}")
    if math.isnan(value) or math.isinf(value):
        fail(f"{path} row {row}: column '{column}' is not finite: {raw!r}")
    return value


def classify_pattern(adi: Optional[float], cv2: Optional[float]) -> str:
    if adi is None:
        return "no demand"
    cv2 = cv2 or 0.0
    if adi < ADI_CUT:
        return "smooth" if cv2 < CV2_CUT else "erratic"
    return "intermittent" if cv2 < CV2_CUT else "lumpy"


def analyse(demand_rows: List[Dict[str, str]], costs: Dict[str, float], a_cut: float, b_cut: float,
            x_cut: float, y_cut: float, fill_zeros: bool, demand_path: str = "demand") -> Dict[str, object]:
    series: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    negatives = 0
    for i, row in enumerate(demand_rows, start=2):
        sku = (row.get("sku_id") or "").strip()
        period = (row.get("period") or "").strip()
        if not sku or not period:
            fail(f"{demand_path} row {i}: empty sku_id or period")
        qty = to_float(row.get("demand_qty", ""), "demand_qty", i, demand_path)
        if qty < 0:
            negatives += 1
        series[sku][period] += qty

    all_periods = sorted({p for s in series.values() for p in s})
    items = []
    for sku, by_period in series.items():
        periods = all_periods if fill_zeros else sorted(by_period)
        values = [by_period.get(p, 0.0) for p in periods]
        n = len(values)
        total = sum(values)
        mean = total / n if n else 0.0
        std = statistics.stdev(values) if n > 1 else 0.0
        cv = (std / mean) if mean > 0 else None
        nonzero = [v for v in values if v > 0]
        adi = (n / len(nonzero)) if nonzero else None
        if len(nonzero) > 1 and statistics.mean(nonzero) > 0:
            cv2 = (statistics.stdev(nonzero) / statistics.mean(nonzero)) ** 2
        elif nonzero:
            cv2 = 0.0
        else:
            cv2 = None
        unit_cost = costs.get(sku)
        value = total * unit_cost if unit_cost is not None else None
        items.append({
            "sku_id": sku, "periods": n, "total_qty": total, "mean_demand": mean, "std_demand": std,
            "cv": cv, "nonzero_periods": len(nonzero), "adi": adi, "cv2": cv2,
            "pattern": classify_pattern(adi, cv2), "unit_cost": unit_cost, "value": value,
        })

    basis = "value" if costs and all(it["unit_cost"] is not None for it in items) else "volume"
    if costs and basis == "volume":
        missing = sorted(it["sku_id"] for it in items if it["unit_cost"] is None)
        fail(f"--costs given but unit_cost missing for {len(missing)} SKU(s), e.g. {missing[:5]}")
    key = "value" if basis == "value" else "total_qty"
    items.sort(key=lambda it: (-(it[key] or 0.0), it["sku_id"]))
    grand = sum(it[key] or 0.0 for it in items)
    cum = 0.0
    for it in items:
        amount = it[key] or 0.0
        share = amount / grand if grand > 0 else 0.0
        before = cum
        cum += share
        it["share"] = share
        it["cum_share"] = cum
        if amount <= 0:
            it["abc"] = "C"
        elif before < a_cut:
            it["abc"] = "A"
        elif before < b_cut:
            it["abc"] = "B"
        else:
            it["abc"] = "C"
        cv = it["cv"]
        it["xyz"] = "Z" if cv is None else ("X" if cv <= x_cut else ("Y" if cv <= y_cut else "Z"))

    matrix = {a + x: {"count": 0, "share": 0.0} for a in "ABC" for x in "XYZ"}
    for it in items:
        cell = matrix[it["abc"] + it["xyz"]]
        cell["count"] += 1
        cell["share"] += it["share"]
    patterns: Dict[str, int] = defaultdict(int)
    for it in items:
        patterns[it["pattern"]] += 1

    return {
        "basis": basis,
        "periods": len(all_periods),
        "first_period": all_periods[0] if all_periods else None,
        "last_period": all_periods[-1] if all_periods else None,
        "sku_count": len(items),
        "negative_rows": negatives,
        "thresholds": {"a_cut": a_cut, "b_cut": b_cut, "x_cut": x_cut, "y_cut": y_cut,
                       "adi_cut": ADI_CUT, "cv2_cut": CV2_CUT, "fill_zeros": fill_zeros},
        "matrix": matrix,
        "patterns": dict(patterns),
        "items": items,
    }


def fmt(v, digits=2) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:,.{digits}f}"
    return str(v)


def to_markdown(res: Dict[str, object]) -> str:
    th = res["thresholds"]
    out = [
        "## ABC/XYZ segmentation",
        f"- Basis for ABC: **{res['basis']}**"
        + ("" if res["basis"] == "value" else " (no unit costs given; value-based ABC is recommended)"),
        f"- SKUs: {res['sku_count']} · periods: {res['periods']} ({res['first_period']} to {res['last_period']})",
        f"- Thresholds: A < {th['a_cut']:.0%} cumulative, B < {th['b_cut']:.0%}; "
        f"X: CV <= {th['x_cut']}, Y: CV <= {th['y_cut']}; missing periods filled with zero: {th['fill_zeros']}",
    ]
    if res["negative_rows"]:
        out.append(f"- ⚠ {res['negative_rows']} row(s) with negative demand (returns netted?); check the data")
    out += ["", "### Matrix: SKU count (share of " + res["basis"] + ")", "", "| | X | Y | Z | Total |", "|---|---|---|---|---|"]
    for a in "ABC":
        cells = [res["matrix"][a + x] for x in "XYZ"]
        row_count = sum(c["count"] for c in cells)
        row_share = sum(c["share"] for c in cells)
        out.append(f"| **{a}** | " + " | ".join(f"{c['count']} ({c['share']:.0%})" for c in cells)
                   + f" | {row_count} ({row_share:.0%}) |")
    out += ["", "### Demand patterns (Syntetos–Boylan–Croston)", ""]
    out += [f"- {k}: {v}" for k, v in sorted(res["patterns"].items())]
    out += ["", "### Items", "",
            "| sku_id | ABC | XYZ | pattern | total_qty | " + ("value | " if res["basis"] == "value" else "")
            + "cum_share | mean | std | CV | ADI | CV² |",
            "|---|---|---|---|---|" + ("---|" if res["basis"] == "value" else "") + "---|---|---|---|---|---|"]
    for it in res["items"]:
        out.append(
            f"| {it['sku_id']} | {it['abc']} | {it['xyz']} | {it['pattern']} | {fmt(it['total_qty'], 0)} | "
            + (f"{fmt(it['value'], 0)} | " if res["basis"] == "value" else "")
            + f"{it['cum_share']:.1%} | {fmt(it['mean_demand'])} | {fmt(it['std_demand'])} | {fmt(it['cv'])} | "
            f"{fmt(it['adi'])} | {fmt(it['cv2'])} |"
        )
    return "\n".join(out)


def write_out(res: Dict[str, object], path: str) -> None:
    cols = ["sku_id", "abc", "xyz", "pattern", "periods", "total_qty", "mean_demand", "std_demand", "cv",
            "nonzero_periods", "adi", "cv2", "unit_cost", "value", "share", "cum_share"]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=cols)
        writer.writeheader()
        for it in res["items"]:
            writer.writerow({c: ("" if it.get(c) is None else it.get(c)) for c in cols})


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("demand", help="demand history CSV: sku_id, period, demand_qty")
    parser.add_argument("--costs", help="item master CSV: sku_id, unit_cost (enables value-based ABC)")
    parser.add_argument("--a-cut", type=float, default=0.80)
    parser.add_argument("--b-cut", type=float, default=0.95)
    parser.add_argument("--x-cut", type=float, default=0.5)
    parser.add_argument("--y-cut", type=float, default=1.0)
    parser.add_argument("--no-fill-zeros", action="store_true", help="do not treat missing periods as zero demand")
    parser.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    parser.add_argument("--out", help="write per-SKU statistics CSV to this path")
    args = parser.parse_args(argv)

    if not (0 < args.a_cut < args.b_cut <= 1):
        fail("require 0 < --a-cut < --b-cut <= 1")
    if not (0 <= args.x_cut < args.y_cut):
        fail("require 0 <= --x-cut < --y-cut")

    demand = read_csv(args.demand, ["sku_id", "period", "demand_qty"])
    costs: Dict[str, float] = {}
    if args.costs:
        for i, row in enumerate(read_csv(args.costs, ["sku_id", "unit_cost"]), start=2):
            costs[row["sku_id"].strip()] = to_float(row["unit_cost"], "unit_cost", i, args.costs)

    res = analyse(demand, costs, args.a_cut, args.b_cut, args.x_cut, args.y_cut, not args.no_fill_zeros, args.demand)
    if args.out:
        write_out(res, args.out)
    print(json.dumps(res, indent=2) if args.json else to_markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
