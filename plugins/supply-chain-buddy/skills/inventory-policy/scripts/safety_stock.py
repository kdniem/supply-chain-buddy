#!/usr/bin/env python3
"""Safety stock, reorder point / order-up-to level, and (optional) stock health per SKU.

Input: parameter CSV, one row per SKU (header required). Time unit = one demand PERIOD
(e.g. a week). Lead times may be given in periods or in days (then pass --period-days).

    sku_id                 required
    mean_demand            mean demand per period        } required unless --history is given
    std_demand             std dev of demand per period  } (then computed from history)
    forecast_error_std     optional; if present, used INSTEAD of std_demand (preferred when a
                           forecast exists: RMSE of the forecast at the relevant lag)
    lead_time | lead_time_days           required (one of them)
    lead_time_std | lead_time_std_days   optional, default 0
    review_period | review_period_days   optional, default 0 (= continuous review)
    service_level          optional per-SKU target, e.g. 0.95 or 95 (else --target)
    order_qty              optional; lot size Q (needed for fill-rate method with continuous review)
    unit_cost              optional; enables values
    on_hand_qty            optional; enables stock health classification
    segment                optional; passed through (e.g. AX, CZ)

Method                                                             [SPT-2017]
    Protection interval P = L + R (periods)
    sigma_P = sqrt(P * sigma_d^2 + d^2 * sigma_L^2)
    csl:        k = z = Phi^-1(CSL)
    fill-rate:  choose k with sigma_P * G(k) = (1 - beta) * Q, G = standard normal loss function,
                Q = order_qty (continuous review) or d * R (periodic review)
    SS = max(0, k * sigma_P)
    Continuous review (R = 0): reorder point  ROP = d * L + SS
    Periodic review   (R > 0): order-up-to    S   = d * (L + R) + SS
    Cycle stock = Q / 2;  target average stock = SS + Q / 2;  max stock = SS + Q
    For the csl method with a known Q, the implied unit fill rate 1 - sigma_P * G(z) / Q is reported.
    Stock health (if on_hand_qty): below_ss if on_hand < SS; excess if on_hand > SS + Q; else ok.
    Health uses on-hand only (no open orders / backorders); treat it as a first screen.

The normal approximation is poor for intermittent or lumpy demand (check with abc_xyz.py);
results for such SKUs are flagged.

Usage
    python3 safety_stock.py params.csv [--target 0.95] [--method csl|fill-rate]
                            [--period-days 7] [--history demand.csv] [--patterns stats.csv]
                            [--json] [--out results.csv]

Standard library only. Deterministic.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from statistics import NormalDist
from typing import Dict, List, Optional

N = NormalDist()


def fail(msg: str) -> None:
    sys.exit(f"Input error: {msg}")


def loss(k: float) -> float:
    """Standard normal loss function G(k) = phi(k) - k * (1 - Phi(k))."""
    return N.pdf(k) - k * (1.0 - N.cdf(k))


def k_for_fill_rate(target_loss: float) -> float:
    """Solve G(k) = target_loss by bisection on [-4, 8] (G is strictly decreasing)."""
    lo, hi = -4.0, 8.0
    if target_loss >= loss(lo):
        return lo
    if target_loss <= loss(hi):
        return hi
    for _ in range(200):
        mid = (lo + hi) / 2
        if loss(mid) > target_loss:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def read_csv(path: str) -> List[Dict[str, str]]:
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            reader.fieldnames = [f.strip() for f in (reader.fieldnames or [])]
            return list(reader)
    except FileNotFoundError:
        fail(f"file not found: {path}")
    return []


def num(row: Dict[str, str], col: str, i: int, path: str, default: Optional[float] = None) -> Optional[float]:
    raw = row.get(col)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        value = float(str(raw).strip().replace(",", ""))
    except ValueError:
        fail(f"{path} row {i}: column '{col}' is not a number: {raw!r}")
    if math.isnan(value) or math.isinf(value):
        fail(f"{path} row {i}: column '{col}' is not finite: {raw!r}")
    return value


def history_stats(path: str) -> Dict[str, Dict[str, float]]:
    rows = read_csv(path)
    if rows and not {"sku_id", "period", "demand_qty"} <= set(rows[0].keys()):
        fail(f"{path}: needs columns sku_id, period, demand_qty")
    series: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for i, row in enumerate(rows, start=2):
        series[row["sku_id"].strip()][row["period"].strip()] += num(row, "demand_qty", i, path, 0.0)
    periods = sorted({p for s in series.values() for p in s})
    stats = {}
    for sku, by_period in series.items():
        values = [by_period.get(p, 0.0) for p in periods]
        stats[sku] = {
            "mean": sum(values) / len(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0.0,
            "periods": len(values),
        }
    return stats


def periods_from(row, col_periods, col_days, i, path, period_days, default=None):
    v = num(row, col_periods, i, path)
    if v is not None:
        return v
    d = num(row, col_days, i, path)
    if d is not None:
        if not period_days:
            fail(f"{path} row {i}: '{col_days}' given; pass --period-days (e.g. 7 for weekly demand)")
        return d / period_days
    return default


def compute(params: List[Dict[str, str]], target: float, method: str, period_days: Optional[float],
            hist: Optional[Dict[str, Dict[str, float]]], patterns: Dict[str, str], path: str = "params") -> Dict[str, object]:
    results = []
    for i, row in enumerate(params, start=2):
        sku = (row.get("sku_id") or "").strip()
        if not sku:
            fail(f"{path} row {i}: empty sku_id")
        notes: List[str] = []

        d = num(row, "mean_demand", i, path)
        sd = num(row, "std_demand", i, path)
        if (d is None or sd is None) and hist is not None:
            if sku not in hist:
                fail(f"{path} row {i}: no mean/std given and SKU '{sku}' not found in --history")
            d = hist[sku]["mean"] if d is None else d
            sd = hist[sku]["std"] if sd is None else sd
            notes.append(f"demand stats from history ({hist[sku]['periods']} periods)")
        if d is None or sd is None:
            fail(f"{path} row {i}: need mean_demand and std_demand (or pass --history)")
        fe = num(row, "forecast_error_std", i, path)
        sigma_d = fe if fe is not None else sd
        sigma_source = "forecast error" if fe is not None else "demand std"

        lt = periods_from(row, "lead_time", "lead_time_days", i, path, period_days)
        if lt is None:
            fail(f"{path} row {i}: need lead_time (periods) or lead_time_days")
        lt_sd = periods_from(row, "lead_time_std", "lead_time_std_days", i, path, period_days, 0.0)
        rp = periods_from(row, "review_period", "review_period_days", i, path, period_days, 0.0)
        if min(d, sigma_d, lt, lt_sd, rp) < 0:
            fail(f"{path} row {i}: negative demand, std, lead time or review period")

        sl = num(row, "service_level", i, path)
        sl = target if sl is None else (sl / 100.0 if sl > 1 else sl)
        if not 0 < sl < 1:
            fail(f"{path} row {i}: service level must be between 0 and 1 (exclusive), got {sl}")

        q = num(row, "order_qty", i, path)
        if rp > 0 and q is None:
            q_cycle = d * rp
        else:
            q_cycle = q

        p = lt + rp
        sigma_p = math.sqrt(p * sigma_d ** 2 + d ** 2 * lt_sd ** 2)

        implied_fill = None
        if method == "csl":
            k = N.inv_cdf(sl)
            if q_cycle and q_cycle > 0 and sigma_p > 0:
                implied_fill = max(0.0, 1.0 - sigma_p * loss(k) / q_cycle)
        else:
            if not q_cycle or q_cycle <= 0:
                fail(f"{path} row {i}: fill-rate method needs order_qty (or a review period)")
            k = k_for_fill_rate((1.0 - sl) * q_cycle / sigma_p) if sigma_p > 0 else 0.0
        ss_raw = k * sigma_p
        ss = max(0.0, ss_raw)
        if ss_raw < 0:
            notes.append("target met without safety stock (k < 0); SS floored at 0")

        if rp > 0:
            level_name, level = "order_up_to", d * (lt + rp) + ss
        else:
            level_name, level = "reorder_point", d * lt + ss

        pattern = patterns.get(sku)
        if pattern in ("intermittent", "lumpy"):
            notes.append(f"{pattern} demand: normal approximation unreliable; treat SS as indicative")
        if d > 0 and sigma_d / d > 1.0 and pattern is None:
            notes.append("CV > 1: check for intermittent demand before relying on normal approximation")
        if lt_sd == 0:
            notes.append("lead time variability assumed 0")

        cost = num(row, "unit_cost", i, path)
        on_hand = num(row, "on_hand_qty", i, path)
        cycle = (q_cycle / 2.0) if q_cycle else None
        avg_target = ss + cycle if cycle is not None else None
        max_stock = ss + q_cycle if q_cycle else None
        health, excess, shortfall = None, None, None
        if on_hand is not None:
            if on_hand < ss:
                health, shortfall = "below_ss", ss - on_hand
            elif max_stock is not None and on_hand > max_stock:
                health, excess = "excess", on_hand - max_stock
            else:
                health = "ok" if max_stock is not None else "ok (no Q: excess not tested)"

        def val(x):
            return None if (x is None or cost is None) else x * cost

        results.append({
            "sku_id": sku, "segment": (row.get("segment") or "").strip() or None,
            "mean_demand": d, "sigma_d": sigma_d, "sigma_source": sigma_source,
            "lead_time": lt, "lead_time_std": lt_sd, "review_period": rp, "protection_interval": p,
            "sigma_p": sigma_p, "service_level": sl, "method": method, "k": k,
            "safety_stock": ss, level_name: level, "order_qty": q_cycle,
            "implied_fill_rate": implied_fill, "cycle_stock": cycle, "target_avg_stock": avg_target,
            "max_stock": max_stock, "unit_cost": cost, "on_hand_qty": on_hand, "health": health,
            "excess_qty": excess, "shortfall_qty": shortfall,
            "ss_value": val(ss), "target_avg_value": val(avg_target), "on_hand_value": val(on_hand),
            "excess_value": val(excess), "notes": "; ".join(notes),
        })

    summary = {"skus": len(results), "method": method, "default_target": target}
    if all(r["unit_cost"] is not None for r in results) and results:
        summary["ss_value"] = sum(r["ss_value"] for r in results)
        if all(r["target_avg_value"] is not None for r in results):
            summary["target_avg_value"] = sum(r["target_avg_value"] for r in results)
        if all(r["on_hand_value"] is not None for r in results):
            summary["on_hand_value"] = sum(r["on_hand_value"] for r in results)
            summary["excess_value"] = sum(r["excess_value"] or 0.0 for r in results)
    if any(r["health"] for r in results):
        counts: Dict[str, int] = defaultdict(int)
        for r in results:
            counts[r["health"] or "n/a"] += 1
        summary["health_counts"] = dict(counts)
    return {"summary": summary, "items": results}


def f(v, digits=1) -> str:
    if v is None:
        return "–"
    if isinstance(v, float):
        return f"{v:,.{digits}f}"
    return str(v)


def to_markdown(res: Dict[str, object]) -> str:
    s = res["summary"]
    items = res["items"]
    out = ["## Safety stock and replenishment parameters",
           f"- SKUs: {s['skus']} · method: **{s['method']}** · default target: {s['default_target']:.1%}"
           + (" cycle service level" if s["method"] == "csl" else " fill rate"),
           "- Formula: SS = k · √(P·σ_d² + d̄²·σ_L²), P = lead time + review period (periods) [SPT-2017]"]
    for key, label in (("ss_value", "Safety stock value"), ("target_avg_value", "Target average stock value"),
                       ("on_hand_value", "Current on-hand value"), ("excess_value", "Excess above SS + Q (value)")):
        if key in s:
            out.append(f"- {label}: {s[key]:,.0f}")
    if "health_counts" in s:
        out.append("- Stock health: " + ", ".join(f"{k}: {v}" for k, v in sorted(s["health_counts"].items())))
    has_health = any(r["health"] for r in items)
    out += ["", "| sku_id | seg | d̄ | σ | P | target | k | SS | ROP / S | Q | impl. fill | "
            + ("on hand | health | " if has_health else "") + "notes |",
            "|---|---|---|---|---|---|---|---|---|---|---|" + ("---|---|" if has_health else "") + "---|"]
    for r in items:
        level = r.get("reorder_point", r.get("order_up_to"))
        tag = "ROP" if "reorder_point" in r else "S"
        fill = "–" if r["implied_fill_rate"] is None else "{:.1%}".format(r["implied_fill_rate"])
        out.append(
            f"| {r['sku_id']} | {r['segment'] or ''} | {f(r['mean_demand'])} | {f(r['sigma_d'])} | {f(r['protection_interval'], 2)} | "
            f"{r['service_level']:.1%} | {r['k']:.3f} | {f(r['safety_stock'], 0)} | {tag} {f(level, 0)} | {f(r['order_qty'], 0)} | "
            f"{fill} | "
            + (f"{f(r['on_hand_qty'], 0)} | {r['health'] or '–'} | " if has_health else "")
            + f"{r['notes']} |"
        )
    out.append("")
    out.append("σ = demand std per period, or forecast error std where given; P in periods; "
               "health compares on-hand only (no open orders).")
    return "\n".join(out)


def write_out(res: Dict[str, object], path: str) -> None:
    cols = sorted({k for r in res["items"] for k in r})
    first = ["sku_id", "segment", "safety_stock", "reorder_point", "order_up_to", "order_qty", "health"]
    cols = [c for c in first if c in cols] + [c for c in cols if c not in first]
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=cols)
        writer.writeheader()
        for r in res["items"]:
            writer.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("params", help="parameter CSV (see above)")
    parser.add_argument("--target", type=float, default=0.95, help="default service level if no per-SKU value (0-1)")
    parser.add_argument("--method", choices=["csl", "fill-rate"], default="csl")
    parser.add_argument("--period-days", type=float, help="days per demand period (needed for *_days columns)")
    parser.add_argument("--history", help="demand history CSV (sku_id, period, demand_qty) to derive mean/std")
    parser.add_argument("--patterns", help="abc_xyz.py --out CSV; flags intermittent/lumpy SKUs")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out", help="write per-SKU results CSV")
    args = parser.parse_args(argv)

    target = args.target / 100.0 if args.target > 1 else args.target
    if not 0 < target < 1:
        fail("--target must be between 0 and 1 (exclusive)")
    params = read_csv(args.params)
    if not params:
        fail(f"{args.params}: no rows")
    if "sku_id" not in params[0]:
        fail(f"{args.params}: missing column 'sku_id'")
    hist = history_stats(args.history) if args.history else None
    patterns: Dict[str, str] = {}
    if args.patterns:
        for row in read_csv(args.patterns):
            if row.get("sku_id") and row.get("pattern"):
                patterns[row["sku_id"].strip()] = row["pattern"].strip()

    res = compute(params, target, args.method, args.period_days, hist, patterns, args.params)
    if args.out:
        write_out(res, args.out)
    print(json.dumps(res, indent=2) if args.json else to_markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
