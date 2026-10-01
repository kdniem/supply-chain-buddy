#!/usr/bin/env python3
"""Forecast accuracy, bias and forecast value added (FVA), per SKU, per group and in total.

Input 1: actuals CSV      sku_id, period, demand_qty
Input 2: forecasts CSV    sku_id, period, <forecast column> [, <compare column>] [, forecast_lag*]
Optional --items CSV      sku_id [, unit_cost] [, <group column>]

Conventions (see references/_shared/kpi-glossary.md)
    error e = F - A (positive = over-forecast)
    bias % = sum(F - A) / sum(A)
    wMAPE  = sum|F - A| / sum(A)          forecast accuracy = 1 - wMAPE (floored at 0)   [KS-2007]
    MAPE   = mean(|F - A| / A) over periods with A > 0 only (count of excluded zeros reported)
    MASE   = MAE / in-sample MAE of the one-step naive forecast on the actuals series   [HK-2006]
    tracking signal TS = sum(e) / MAD;  |TS| > 4 is a common warning threshold (rule of thumb)
    Naive benchmark at lag h: F_t = A_(t-h). FVA vs naive = wMAPE(naive) - wMAPE(forecast),
    in percentage points; positive = the forecast adds value.                       [GIL-2010]
    With --compare-col (e.g. the statistical forecast): FVA of the step from compare to final.
Aggregates are value-weighted when unit_cost is available for all SKUs, else unit-based
(mixing units of different items is only meaningful if they are comparable; this is stated).

Usage
    python3 forecast_accuracy.py actuals.csv forecasts.csv [--forecast-col forecast_qty]
        [--compare-col stat_forecast_qty] [--lag 4] [--items items.csv --group-col category]
        [--from 2026-W01] [--to 2026-W40] [--bias-threshold 0.1] [--json] [--out per_sku.csv]

Standard library only. Deterministic.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple


def fail(msg: str) -> None:
    sys.exit(f"Input error: {msg}")


def read(path: str, required: List[str]) -> List[Dict[str, str]]:
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            r = csv.DictReader(fh)
            r.fieldnames = [c.strip() for c in (r.fieldnames or [])]
            missing = [c for c in required if c not in r.fieldnames]
            if missing:
                fail(f"{path}: missing column(s) {missing}. Found: {r.fieldnames}")
            return list(r)
    except FileNotFoundError:
        fail(f"file not found: {path}")
    return []


def num(raw, col, i, path) -> Optional[float]:
    raw = "" if raw is None else str(raw).strip()
    if raw == "":
        return None
    try:
        v = float(raw.replace(",", ""))
    except ValueError:
        fail(f"{path} row {i}: '{col}' is not a number: {raw!r}")
    if math.isnan(v) or math.isinf(v):
        fail(f"{path} row {i}: '{col}' is not finite")
    return v


def metrics(pairs: List[Tuple[float, float]], scale: Optional[float]) -> Dict[str, Optional[float]]:
    """pairs = [(actual, forecast)]; scale = MASE denominator."""
    n = len(pairs)
    if n == 0:
        return {"n": 0}
    sa = sum(a for a, _ in pairs)
    sf = sum(f for _, f in pairs)
    errs = [f - a for a, f in pairs]
    abs_errs = [abs(e) for e in errs]
    mae = sum(abs_errs) / n
    nz = [(a, f) for a, f in pairs if a > 0]
    return {
        "n": n, "sum_actual": sa, "sum_forecast": sf,
        "bias": (sf - sa) / sa if sa > 0 else None,
        "mae": mae,
        "rmse": math.sqrt(sum(e * e for e in errs) / n),
        "wmape": sum(abs_errs) / sa if sa > 0 else None,
        "mape": (sum(abs(f - a) / a for a, f in nz) / len(nz)) if nz else None,
        "mape_zero_periods_excluded": n - len(nz),
        "mase": (mae / scale) if scale else None,
        "tracking_signal": (sum(errs) / mae) if mae > 0 else 0.0,
        "abs_error_sum": sum(abs_errs),
    }


def analyse(actual_rows, forecast_rows, fcol, ccol, lag, items, group_col, p_from, p_to,
            bias_threshold, a_path="actuals", f_path="forecasts") -> Dict[str, object]:
    actual: Dict[str, Dict[str, float]] = defaultdict(dict)
    for i, r in enumerate(actual_rows, start=2):
        v = num(r.get("demand_qty"), "demand_qty", i, a_path)
        actual[r["sku_id"].strip()][r["period"].strip()] = (actual[r["sku_id"].strip()].get(r["period"].strip(), 0.0)
                                                           + (v or 0.0))
    fc: Dict[str, Dict[str, Tuple[Optional[float], Optional[float]]]] = defaultdict(dict)
    for i, r in enumerate(forecast_rows, start=2):
        fc[r["sku_id"].strip()][r["period"].strip()] = (num(r.get(fcol), fcol, i, f_path),
                                                         num(r.get(ccol), ccol, i, f_path) if ccol else None)
    all_periods = sorted({p for s in actual.values() for p in s})
    index = {p: k for k, p in enumerate(all_periods)}

    def in_window(p: str) -> bool:
        return (p_from is None or p >= p_from) and (p_to is None or p <= p_to)

    per_sku = []
    for sku in sorted(set(actual) & set(fc)):
        series = [actual[sku].get(p, 0.0) for p in all_periods]
        diffs = [abs(series[k] - series[k - 1]) for k in range(1, len(series))]
        scale = (sum(diffs) / len(diffs)) if diffs and sum(diffs) > 0 else None
        main, comp, naive = [], [], []
        for p, (f, c) in fc[sku].items():
            if p not in index or not in_window(p) or f is None:
                continue
            a = series[index[p]]
            main.append((a, f))
            if c is not None:
                comp.append((a, c))
            k = index[p] - lag
            if k >= 0:
                naive.append((a, series[k], f))
        m = metrics(main, scale)
        naive_pairs = [(a, nv) for a, nv, _ in naive]
        main_on_naive = [(a, f) for a, _, f in naive]
        mn = metrics(naive_pairs, scale)
        mf = metrics(main_on_naive, scale)
        row = {"sku_id": sku, **m}
        row["naive_wmape"] = mn.get("wmape")
        row["fva_vs_naive_pts"] = (None if mn.get("wmape") is None or mf.get("wmape") is None
                                   else (mn["wmape"] - mf["wmape"]) * 100)
        if ccol:
            mc = metrics(comp, scale)
            row["compare_wmape"] = mc.get("wmape")
            row["compare_bias"] = mc.get("bias")
            row["fva_vs_compare_pts"] = (None if mc.get("wmape") is None or m.get("wmape") is None
                                         else (mc["wmape"] - m["wmape"]) * 100)
        cost = items.get(sku, {}).get("unit_cost")
        row["unit_cost"] = cost
        row["group"] = items.get(sku, {}).get("group")
        row["abs_error_value"] = (m.get("abs_error_sum", 0.0) * cost) if cost is not None else None
        b, ts = m.get("bias"), m.get("tracking_signal")
        row["bias_flag"] = bool(b is not None and abs(b) > bias_threshold and ts is not None and abs(ts) > 4)
        row["_pairs"], row["_comp"], row["_naive"] = main, comp, naive
        per_sku.append(row)

    if not per_sku:
        fail("no SKU/period overlap between actuals and forecasts (check sku_id and period labels)")

    value_based = all(r["unit_cost"] is not None for r in per_sku)

    def aggregate(rows) -> Dict[str, Optional[float]]:
        w = (lambda r: r["unit_cost"]) if value_based else (lambda r: 1.0)
        sa = sum(a * w(r) for r in rows for a, _ in r["_pairs"])
        sf = sum(f * w(r) for r in rows for _, f in r["_pairs"])
        sae = sum(abs(f - a) * w(r) for r in rows for a, f in r["_pairs"])
        out = {"skus": len(rows), "bias": (sf - sa) / sa if sa else None, "wmape": sae / sa if sa else None}
        na = sum(a * w(r) for r in rows for a, _, _ in r["_naive"])
        n_err = sum(abs(nv - a) * w(r) for r in rows for a, nv, _ in r["_naive"])
        f_err = sum(abs(f - a) * w(r) for r in rows for a, _, f in r["_naive"])
        out["naive_wmape"] = n_err / na if na else None
        out["fva_vs_naive_pts"] = ((n_err - f_err) / na * 100) if na else None
        if ccol:
            ca = sum(a * w(r) for r in rows for a, _ in r["_comp"])
            ce = sum(abs(c - a) * w(r) for r in rows for a, c in r["_comp"])
            cf = sum(c * w(r) for r in rows for _, c in r["_comp"])
            out["compare_wmape"] = ce / ca if ca else None
            out["compare_bias"] = (cf - ca) / ca if ca else None
            out["fva_vs_compare_pts"] = ((ce / ca - out["wmape"]) * 100) if (ca and out["wmape"] is not None) else None
        return out

    groups = defaultdict(list)
    for r in per_sku:
        if r["group"]:
            groups[r["group"]].append(r)
    result = {
        "forecast_col": fcol, "compare_col": ccol, "lag": lag, "window": [p_from, p_to],
        "weighting": "value (unit_cost)" if value_based else "units",
        "bias_threshold": bias_threshold,
        "total": aggregate(per_sku),
        "by_group": {g: aggregate(rs) for g, rs in sorted(groups.items())},
        "items": [{k: v for k, v in r.items() if not k.startswith("_")} for r in per_sku],
    }
    return result


def pct(v, d=1) -> str:
    return "–" if v is None else f"{v * 100:.{d}f}%"


def spct(v, d=1) -> str:
    return "–" if v is None else f"{v * 100:+.{d}f}%"


def pts(v, d=1) -> str:
    return "–" if v is None else f"{v:+.{d}f}"


def to_markdown(res: Dict[str, object]) -> str:
    t = res["total"]
    has_c = bool(res["compare_col"])
    out = ["## Forecast accuracy and bias",
           f"- Forecast evaluated: `{res['forecast_col']}`" + (f" vs. `{res['compare_col']}`" if has_c else "")
           + f" · naive benchmark at lag {res['lag']} · weighting: {res['weighting']}"
           + (f" · window {res['window'][0] or 'start'} to {res['window'][1] or 'end'}" if any(res["window"]) else ""),
           f"- Total: wMAPE **{pct(t['wmape'])}** (accuracy {pct(max(0.0, 1 - t['wmape']) if t['wmape'] is not None else None)}), "
           f"bias **{spct(t['bias'])}**, naive wMAPE {pct(t['naive_wmape'])}, FVA vs. naive **{pts(t['fva_vs_naive_pts'])} pts**"
           + (f"; `{res['compare_col']}`: wMAPE {pct(t['compare_wmape'])}, bias {spct(t['compare_bias'])}, "
              f"FVA of the step **{pts(t['fva_vs_compare_pts'])} pts**" if has_c else "")]
    flagged = [r for r in res["items"] if r["bias_flag"]]
    if flagged:
        out.append(f"- ⚠ Persistent bias (|bias| > {res['bias_threshold']:.0%} and |TS| > 4): "
                   + ", ".join(f"{r['sku_id']} ({spct(r['bias'], 0)})" for r in flagged[:20]))
    if res["by_group"]:
        out += ["", "### By group", "",
                "| group | SKUs | wMAPE | bias | naive wMAPE | FVA vs naive | " + ("compare wMAPE | compare bias | FVA step |" if has_c else ""),
                "|---|---|---|---|---|---|" + ("---|---|---|" if has_c else "")]
        for g, a in res["by_group"].items():
            out.append(f"| {g} | {a['skus']} | {pct(a['wmape'])} | {spct(a['bias'])} | {pct(a['naive_wmape'])} | "
                       f"{pts(a['fva_vs_naive_pts'])} | "
                       + (f"{pct(a['compare_wmape'])} | {spct(a['compare_bias'])} | {pts(a['fva_vs_compare_pts'])} |" if has_c else ""))
    key = (lambda r: -(r["abs_error_value"] or 0)) if res["weighting"].startswith("value") else (lambda r: -r.get("abs_error_sum", 0))
    out += ["", "### Items (sorted by absolute error" + (" value" if res["weighting"].startswith("value") else "") + ")", "",
            "| sku_id | group | n | wMAPE | bias | MASE | TS | FVA vs naive | " + ("FVA step | " if has_c else "") + "MAPE (zeros excl.) |",
            "|---|---|---|---|---|---|---|---|" + ("---|" if has_c else "") + "---|"]
    for r in sorted(res["items"], key=key):
        mase = "–" if r.get("mase") is None else f"{r['mase']:.2f}"
        out.append(f"| {r['sku_id']}{' ⚠' if r['bias_flag'] else ''} | {r['group'] or ''} | {r['n']} | {pct(r.get('wmape'))} | "
                   f"{spct(r.get('bias'))} | {mase} | {r.get('tracking_signal', 0):.1f} | {pts(r['fva_vs_naive_pts'])} | "
                   + (f"{pts(r.get('fva_vs_compare_pts'))} | " if has_c else "")
                   + f"{pct(r.get('mape'))} ({r.get('mape_zero_periods_excluded', 0)}) |")
    out += ["", "Error = forecast − actual (positive = over-forecast). FVA in percentage points of wMAPE; positive = adds value."]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("actuals")
    ap.add_argument("forecasts")
    ap.add_argument("--forecast-col", default="forecast_qty")
    ap.add_argument("--compare-col", help="second forecast column, e.g. stat_forecast_qty, for FVA of the step")
    ap.add_argument("--lag", type=int, help="forecast lag in periods for the naive benchmark (default: forecast_lag* column or 1)")
    ap.add_argument("--items", help="item CSV with sku_id and optional unit_cost / group column")
    ap.add_argument("--group-col", default="category")
    ap.add_argument("--from", dest="p_from")
    ap.add_argument("--to", dest="p_to")
    ap.add_argument("--bias-threshold", type=float, default=0.10)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write per-SKU metrics CSV")
    a = ap.parse_args(argv)

    actual_rows = read(a.actuals, ["sku_id", "period", "demand_qty"])
    forecast_rows = read(a.forecasts, ["sku_id", "period", a.forecast_col] + ([a.compare_col] if a.compare_col else []))
    lag = a.lag
    if lag is None:
        lag_cols = [c for c in (forecast_rows[0].keys() if forecast_rows else []) if c.startswith("forecast_lag")]
        lag = int(float(forecast_rows[0][lag_cols[0]])) if lag_cols and forecast_rows[0][lag_cols[0]] else 1
    if lag < 1:
        fail("--lag must be >= 1")
    items: Dict[str, Dict[str, object]] = {}
    if a.items:
        for i, r in enumerate(read(a.items, ["sku_id"]), start=2):
            items[r["sku_id"].strip()] = {"unit_cost": num(r.get("unit_cost"), "unit_cost", i, a.items),
                                          "group": (r.get(a.group_col) or "").strip() or None}

    res = analyse(actual_rows, forecast_rows, a.forecast_col, a.compare_col, lag, items, a.group_col,
                  a.p_from, a.p_to, a.bias_threshold, a.actuals, a.forecasts)
    if a.out:
        cols = [c for c in res["items"][0].keys()]
        with open(a.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in res["items"]:
                w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})
    print(json.dumps(res, indent=2) if a.json else to_markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
