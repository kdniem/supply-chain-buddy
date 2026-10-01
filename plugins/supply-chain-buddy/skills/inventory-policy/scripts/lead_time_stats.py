#!/usr/bin/env python3
"""Actual supplier lead times from purchase order receipts, with drift detection.

Input CSV (header required):
    sku_id          item
    order_date      YYYY-MM-DD
    received_date   YYYY-MM-DD (rows without it = still open, ignored)
    supplier_id     optional; enables a per-supplier summary
    promised_date   optional; enables "promised vs. actual" comparison

Method
    lead time (days) = received_date - order_date, per receipt.
    Per SKU and per supplier: n, mean, std (sample), min, max.
    Drift: compares receipts ordered in the last --recent-days of the data window
    ("recent") with all earlier receipts ("before"). Flags drift when the recent mean
    differs from the earlier mean by more than --drift-threshold (default 20%) and both
    windows have at least --min-n receipts (default 3).

Why: system lead times are often outdated, and lead time variability is a major
safety stock driver (see references/methods.md §4). Use this before sizing safety stock.

Usage
    python3 lead_time_stats.py receipts.csv [--recent-days 120] [--drift-threshold 0.2]
                               [--json] [--out lead_times.csv] [--use-recent]
--out writes sku_id, lead_time_days, lead_time_std_days (whole window, or the recent
window with --use-recent), ready to merge into the safety_stock.py parameter file.

Standard library only. Deterministic.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List, Optional


def fail(msg: str) -> None:
    sys.exit(f"Input error: {msg}")


def parse_date(raw: str, col: str, row: int, path: str) -> Optional[date]:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        return date.fromisoformat(raw[:10])
    except ValueError:
        fail(f"{path} row {row}: column '{col}' is not a YYYY-MM-DD date: {raw!r}")
    return None


def describe(values: List[float]) -> Dict[str, Optional[float]]:
    if not values:
        return {"n": 0, "mean": None, "std": None, "min": None, "max": None}
    return {
        "n": len(values),
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def analyse(rows: List[Dict[str, str]], recent_days: int, threshold: float, path: str = "receipts",
            min_n: int = 3) -> Dict[str, object]:
    receipts = []
    open_count = 0
    for i, row in enumerate(rows, start=2):
        sku = (row.get("sku_id") or "").strip()
        if not sku:
            fail(f"{path} row {i}: empty sku_id")
        od = parse_date(row.get("order_date", ""), "order_date", i, path)
        rd = parse_date(row.get("received_date", ""), "received_date", i, path)
        pd = parse_date(row.get("promised_date", ""), "promised_date", i, path)
        if od is None:
            fail(f"{path} row {i}: missing order_date")
        if rd is None:
            open_count += 1
            continue
        lt = (rd - od).days
        if lt < 0:
            fail(f"{path} row {i}: received_date before order_date")
        receipts.append({
            "sku_id": sku, "supplier_id": (row.get("supplier_id") or "").strip() or None,
            "order_date": od, "lt": float(lt),
            "promised_lt": float((pd - od).days) if pd else None,
        })
    if not receipts:
        fail(f"{path}: no received orders")

    cutoff = max(r["order_date"] for r in receipts) - timedelta(days=recent_days)

    def group(key: str) -> List[Dict[str, object]]:
        buckets: Dict[str, List[dict]] = defaultdict(list)
        for r in receipts:
            if r[key]:
                buckets[r[key]].append(r)
        out = []
        for k in sorted(buckets):
            rs = buckets[k]
            allv = [r["lt"] for r in rs]
            before = [r["lt"] for r in rs if r["order_date"] <= cutoff]
            recent = [r["lt"] for r in rs if r["order_date"] > cutoff]
            promised = [r["promised_lt"] for r in rs if r["promised_lt"] is not None]
            d_all, d_before, d_recent = describe(allv), describe(before), describe(recent)
            drift = None
            if d_before["n"] and d_recent["n"] and d_before["mean"]:
                drift = d_recent["mean"] / d_before["mean"] - 1.0
            item = {
                key: k,
                "all": d_all, "before": d_before, "recent": d_recent,
                "promised_mean": statistics.mean(promised) if promised else None,
                "drift": drift,
                "drift_flag": (drift is not None and abs(drift) > threshold
                               and d_before["n"] >= min_n and d_recent["n"] >= min_n),
            }
            if key == "sku_id":
                sups = sorted({r["supplier_id"] for r in rs if r["supplier_id"]})
                item["supplier_id"] = ", ".join(sups) if sups else None
            out.append(item)
        return out

    return {
        "receipts": len(receipts), "open_orders_ignored": open_count,
        "window": [min(r["order_date"] for r in receipts).isoformat(), max(r["order_date"] for r in receipts).isoformat()],
        "recent_cutoff": cutoff.isoformat(), "recent_days": recent_days, "drift_threshold": threshold, "min_n": min_n,
        "by_supplier": group("supplier_id") if any(r["supplier_id"] for r in receipts) else [],
        "by_sku": group("sku_id"),
    }


def f(v, d=1) -> str:
    return "–" if v is None else f"{v:,.{d}f}"


def to_markdown(res: Dict[str, object]) -> str:
    out = ["## Actual lead times from receipts",
           f"- Receipts: {res['receipts']} (open orders ignored: {res['open_orders_ignored']}); "
           f"orders from {res['window'][0]} to {res['window'][1]}",
           f"- Drift test: orders after {res['recent_cutoff']} (last {res['recent_days']} days) vs. earlier; "
           f"flag if the mean changes by more than {res['drift_threshold']:.0%} (min {res['min_n']} receipts per window)"]
    flagged = [x for x in res["by_sku"] if x["drift_flag"]]
    if flagged:
        out.append(f"- ⚠ Drift flagged for {len(flagged)} SKU(s): " + ", ".join(x["sku_id"] for x in flagged[:15])
                   + (" …" if len(flagged) > 15 else ""))
    for title, key, rows in (("By supplier", "supplier_id", res["by_supplier"]), ("By SKU", "sku_id", res["by_sku"])):
        if not rows:
            continue
        out += ["", f"### {title}", "",
                f"| {key} | n | mean days | std | min–max | promised | before | recent | drift |",
                "|---|---|---|---|---|---|---|---|---|"]
        for x in rows:
            a = x["all"]
            drift = "–" if x["drift"] is None else f"{x['drift']:+.0%}" + (" ⚠" if x["drift_flag"] else "")
            out.append(f"| {x[key]} | {a['n']} | {f(a['mean'])} | {f(a['std'])} | {f(a['min'], 0)}–{f(a['max'], 0)} | "
                       f"{f(x['promised_mean'])} | {f(x['before']['mean'])} | {f(x['recent']['mean'])} | {drift} |")
    return "\n".join(out)


def write_out(res: Dict[str, object], path: str, use_recent: bool) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sku_id", "lead_time_days", "lead_time_std_days", "n_receipts", "basis"])
        for x in res["by_sku"]:
            stats = x["recent"] if (use_recent and x["recent"]["n"]) else x["all"]
            basis = "recent" if (use_recent and x["recent"]["n"]) else "all"
            writer.writerow([x["sku_id"], round(stats["mean"], 2), round(stats["std"], 2), stats["n"], basis])


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("receipts", help="receipts CSV: sku_id, order_date, received_date [, supplier_id, promised_date]")
    parser.add_argument("--recent-days", type=int, default=120)
    parser.add_argument("--drift-threshold", type=float, default=0.2)
    parser.add_argument("--min-n", type=int, default=3, help="min receipts per window to flag drift")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", help="write per-SKU lead time stats CSV")
    parser.add_argument("--use-recent", action="store_true", help="--out uses the recent window where available")
    args = parser.parse_args(argv)

    try:
        with open(args.receipts, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            reader.fieldnames = [c.strip() for c in (reader.fieldnames or [])]
            missing = [c for c in ("sku_id", "order_date", "received_date") if c not in reader.fieldnames]
            if missing:
                fail(f"{args.receipts}: missing column(s) {missing}. Found: {reader.fieldnames}")
            rows = list(reader)
    except FileNotFoundError:
        fail(f"file not found: {args.receipts}")

    res = analyse(rows, args.recent_days, args.drift_threshold, args.receipts, args.min_n)
    if args.out:
        write_out(res, args.out, args.use_recent)
    print(json.dumps(res, indent=2, default=str) if args.json else to_markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
