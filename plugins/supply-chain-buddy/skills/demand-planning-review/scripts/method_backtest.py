#!/usr/bin/env python3
"""Backtest simple forecasting methods per SKU on a holdout window and recommend a method.

Input: demand CSV  sku_id, period, demand_qty   (missing periods = zero demand)

Methods (all produce a flat forecast from the information available at the forecast origin)
    naive        last observed value                                          [HA-2021]
    ma4/ma8/ma13 moving average of the last k periods                         [HA-2021]
    ses          simple exponential smoothing, alpha from a grid               [GAR-1985]
    croston_sba  Croston with Syntetos-Boylan bias correction (1 - a/2)       [CRO-1972] [SBA-2005]
    tsb          Teunter-Syntetos-Babai (demand probability updated every period) [TSB-2011]

Procedure (rolling origin, fixed parameters)
    Train = all periods before the last --holdout periods. Smoothing parameters are chosen per SKU
    and method on the train window (min MAE of lag-h forecasts). Each holdout period t is then
    forecast from origin t - h (h = --lag), using only data up to the origin.
    Metrics on the holdout: MAE, wMAPE, bias, MASE (scale = in-sample MAE of the one-step naive
    on the train window [HK-2006]). Best method per SKU = lowest MASE (ties -> simpler method).
    Demand pattern per SKU (ADI / CV^2 on the train window) is reported [SB-2005].

Limits: no trend or seasonal methods (need ETS/ARIMA with >= 2 seasonal cycles; use a proper
forecasting library for those). A short holdout gives noisy rankings; treat results as indicative.

Usage
    python3 method_backtest.py demand.csv [--lag 1] [--holdout 13] [--json] [--out best.csv]

Standard library only. Deterministic.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from typing import Callable, Dict, List, Optional, Tuple

GRID = [0.05, 0.1, 0.2, 0.3, 0.5]
SIMPLICITY = ["naive", "ma4", "ma8", "ma13", "ses", "croston_sba", "tsb"]


def fail(msg: str) -> None:
    sys.exit(f"Input error: {msg}")


# --- state recursions: return list f where f[o] = flat forecast made at origin o (using y[0..o]) ---

def fc_naive(y: List[float], _p=None) -> List[float]:
    return list(y)


def fc_ma(k: int) -> Callable:
    def run(y: List[float], _p=None) -> List[float]:
        out, s = [], 0.0
        for i, v in enumerate(y):
            s += v
            if i >= k:
                s -= y[i - k]
            out.append(s / min(i + 1, k))
        return out
    return run


def fc_ses(y: List[float], alpha: float) -> List[float]:
    out, level = [], y[0]
    for v in y:
        level = alpha * v + (1 - alpha) * level
        out.append(level)
    return out


def fc_croston_sba(y: List[float], alpha: float) -> List[float]:
    out = []
    first = next((i for i, v in enumerate(y) if v > 0), None)
    if first is None:
        return [0.0] * len(y)
    z, p, q = y[first], float(first + 1), 1
    for i, v in enumerate(y):
        if i > first:
            if v > 0:
                z = alpha * v + (1 - alpha) * z
                p = alpha * q + (1 - alpha) * p
                q = 1
            else:
                q += 1
        out.append((1 - alpha / 2) * z / p if i >= first else 0.0)
    return out


def fc_tsb(y: List[float], params: Tuple[float, float]) -> List[float]:
    alpha, beta = params
    out = []
    nz = [v for v in y if v > 0]
    if not nz:
        return [0.0] * len(y)
    prob, size = len(nz) / len(y), nz[0]
    for v in y:
        if v > 0:
            prob = prob + beta * (1 - prob)
            size = size + alpha * (v - size)
        else:
            prob = prob * (1 - beta)
        out.append(prob * size)
    return out


METHODS: Dict[str, Tuple[Callable, List]] = {
    "naive": (fc_naive, [None]),
    "ma4": (fc_ma(4), [None]),
    "ma8": (fc_ma(8), [None]),
    "ma13": (fc_ma(13), [None]),
    "ses": (fc_ses, GRID),
    "croston_sba": (fc_croston_sba, GRID[:4]),
    "tsb": (fc_tsb, [(a, b) for a in GRID[:4] for b in GRID[:4]]),
}


def lag_pairs(y: List[float], f: List[float], lag: int, start: int, end: int) -> List[Tuple[float, float]]:
    """Pairs (actual_t, forecast made at t-lag) for t in [start, end)."""
    return [(y[t], f[t - lag]) for t in range(max(start, lag), end)]


def mae(pairs) -> float:
    return sum(abs(f - a) for a, f in pairs) / len(pairs) if pairs else float("inf")


def pattern(train: List[float]) -> Tuple[Optional[float], Optional[float], str]:
    nz = [v for v in train if v > 0]
    if not nz:
        return None, None, "no demand"
    adi = len(train) / len(nz)
    cv2 = (statistics.stdev(nz) / statistics.mean(nz)) ** 2 if len(nz) > 1 else 0.0
    if adi < 1.32:
        name = "smooth" if cv2 < 0.49 else "erratic"
    else:
        name = "intermittent" if cv2 < 0.49 else "lumpy"
    return adi, cv2, name


def backtest_series(y: List[float], lag: int, holdout: int) -> Dict[str, object]:
    n = len(y)
    split = n - holdout
    train = y[:split]
    diffs = [abs(train[i] - train[i - 1]) for i in range(1, len(train))]
    scale = (sum(diffs) / len(diffs)) if diffs and sum(diffs) > 0 else None
    warmup = min(8, max(1, split // 3))
    results = {}
    for name, (fn, grid) in METHODS.items():
        best_param, best_err = None, float("inf")
        for param in grid:
            f_train = fn(train, param)
            err = mae(lag_pairs(train, f_train, lag, warmup, split))
            if err < best_err - 1e-12:
                best_param, best_err = param, err
        f_all = fn(y, best_param)  # recursion only uses data up to each origin
        pairs = lag_pairs(y, f_all, lag, split, n)
        sa = sum(a for a, _ in pairs)
        m = mae(pairs)
        results[name] = {
            "param": best_param, "mae": m,
            "wmape": (sum(abs(f - a) for a, f in pairs) / sa) if sa > 0 else None,
            "bias": (sum(f - a for a, f in pairs) / sa) if sa > 0 else None,
            "mase": (m / scale) if scale else None,
        }
    ranked = sorted(results, key=lambda k: ((results[k]["mase"] if results[k]["mase"] is not None else results[k]["mae"]),
                                            SIMPLICITY.index(k)))
    adi, cv2, pat = pattern(train)
    return {"methods": results, "best": ranked[0], "adi": adi, "cv2": cv2, "pattern": pat}


def run(rows: List[Dict[str, str]], lag: int, holdout: int, path: str = "demand") -> Dict[str, object]:
    series: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for i, r in enumerate(rows, start=2):
        try:
            series[r["sku_id"].strip()][r["period"].strip()] += float(str(r["demand_qty"]).strip() or 0)
        except ValueError:
            fail(f"{path} row {i}: demand_qty is not a number: {r['demand_qty']!r}")
    periods = sorted({p for s in series.values() for p in s})
    if len(periods) < holdout + 13:
        fail(f"need at least holdout + 13 periods ({holdout + 13}); found {len(periods)}")
    items = []
    for sku in sorted(series):
        y = [series[sku].get(p, 0.0) for p in periods]
        r = backtest_series(y, lag, holdout)
        r["sku_id"] = sku
        items.append(r)
    wins: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for it in items:
        wins[it["pattern"]][it["best"]] += 1
    med = {}
    for m in METHODS:
        vals = [it["methods"][m]["mase"] for it in items if it["methods"][m]["mase"] is not None]
        med[m] = statistics.median(vals) if vals else None
    return {"lag": lag, "holdout": holdout, "periods": len(periods),
            "holdout_from": periods[-holdout], "holdout_to": periods[-1],
            "median_mase": med, "wins_by_pattern": {k: dict(v) for k, v in wins.items()}, "items": items}


def f2(v) -> str:
    return "–" if v is None else f"{v:.2f}"


def to_markdown(res: Dict[str, object]) -> str:
    out = ["## Forecast method backtest",
           f"- Holdout: {res['holdout']} periods ({res['holdout_from']} to {res['holdout_to']}), forecast lag {res['lag']}, "
           f"{len(res['items'])} SKUs. MASE < 1 = better than the one-step naive on the train window.",
           "", "### Median MASE by method", "", "| " + " | ".join(METHODS) + " |", "|" + "---|" * len(METHODS),
           "| " + " | ".join(f2(res["median_mase"][m]) for m in METHODS) + " |",
           "", "### Best method by demand pattern (count of SKUs)", "",
           "| pattern | " + " | ".join(METHODS) + " |", "|---|" + "---|" * len(METHODS)]
    for pat, w in sorted(res["wins_by_pattern"].items()):
        out.append(f"| {pat} | " + " | ".join(str(w.get(m, 0)) for m in METHODS) + " |")
    out += ["", "### Per SKU", "", "| sku_id | pattern | best | MASE best | MASE naive | MASE ses | MASE croston_sba | MASE tsb | bias best |",
            "|---|---|---|---|---|---|---|---|---|"]
    for it in res["items"]:
        mm = it["methods"]
        b = mm[it["best"]]
        bias = "–" if b["bias"] is None else f"{b['bias'] * 100:+.0f}%"
        out.append(f"| {it['sku_id']} | {it['pattern']} | {it['best']} | {f2(b['mase'])} | {f2(mm['naive']['mase'])} | "
                   f"{f2(mm['ses']['mase'])} | {f2(mm['croston_sba']['mase'])} | {f2(mm['tsb']['mase'])} | {bias} |")
    out += ["", "Indicative: short holdouts give noisy rankings; no trend/seasonal methods included."]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("demand")
    ap.add_argument("--lag", type=int, default=1)
    ap.add_argument("--holdout", type=int, default=13)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write best method per SKU CSV")
    a = ap.parse_args(argv)
    if a.lag < 1 or a.holdout < 4:
        fail("--lag must be >= 1 and --holdout >= 4")
    try:
        with open(a.demand, newline="", encoding="utf-8-sig") as fh:
            r = csv.DictReader(fh)
            r.fieldnames = [c.strip() for c in (r.fieldnames or [])]
            if not {"sku_id", "period", "demand_qty"} <= set(r.fieldnames):
                fail(f"{a.demand}: needs columns sku_id, period, demand_qty")
            rows = list(r)
    except FileNotFoundError:
        fail(f"file not found: {a.demand}")
    res = run(rows, a.lag, a.holdout, a.demand)
    if a.out:
        with open(a.out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["sku_id", "pattern", "best_method", "param", "mase_best", "mase_naive"])
            for it in res["items"]:
                b = it["methods"][it["best"]]
                w.writerow([it["sku_id"], it["pattern"], it["best"], b["param"], b["mase"], it["methods"]["naive"]["mase"]])
    print(json.dumps(res, indent=2, default=str) if a.json else to_markdown(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
