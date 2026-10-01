#!/usr/bin/env python3
"""KPI bridge: compare a KPI between two periods and attribute the change to groups.

Works on any long-format CSV with a period column. Two KPI types:
  --ratio NUM DEN   ratio KPI = sum(NUM) / sum(DEN), e.g. fill rate = shipped_qty / demand_qty
  --value COL       additive KPI, e.g. inventory value; --agg sum (flows) or mean (stocks: mean
                    over the periods in the window of the per-period total)

Decomposition for ratio KPIs (shift-share, exact, symmetric):
    weight w_g = DEN_g / DEN_total, rate r_g = NUM_g / DEN_g, averages over both windows marked ¯
    rate effect_g = (r2_g - r1_g) * w¯_g          (the group got better or worse)
    mix effect_g  = (w2_g - w1_g) * (r¯_g - R¯)   (volume shifted toward groups above/below average)
    sum over groups of (rate + mix) = R2 - R1
For value KPIs: contribution_g = V2_g - V1_g and its share of the total change.

Options
    --period-col period        name of the period column
    --base FROM:TO             inclusive period range (string comparison, e.g. 2025-W41:2025-W53)
    --compare FROM:TO
    --by COLUMN                group dimension (e.g. supplier_id, category); optional
    --join FILE --on KEY       left-join extra columns (e.g. item master) on KEY
    --multiply-by COLUMN       multiply NUM/DEN/VALUE by this column first (e.g. unit_cost -> value)
    --top N                    show the N largest contributors (default all)

Usage examples
    python3 kpi_bridge.py fulfillment.csv --ratio shipped_qty demand_qty --base 2025-W41:2025-W53 \
        --compare 2026-W28:2026-W40 --by supplier_id --join items.csv --on sku_id --multiply-by unit_cost
    python3 kpi_bridge.py snapshots.csv --value on_hand_qty --agg mean --base ... --compare ... \
        --by category --join items.csv --on sku_id --multiply-by unit_cost

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


def read(path: str) -> Tuple[List[str], List[Dict[str, str]]]:
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            r = csv.DictReader(fh)
            r.fieldnames = [c.strip() for c in (r.fieldnames or [])]
            return r.fieldnames, list(r)
    except FileNotFoundError:
        fail(f"file not found: {path}")
    return [], []


def num(raw, col, i) -> float:
    s = "" if raw is None else str(raw).strip()
    if s == "":
        return 0.0
    try:
        v = float(s.replace(",", ""))
    except ValueError:
        fail(f"row {i}: column '{col}' is not a number: {raw!r}")
    if math.isnan(v) or math.isinf(v):
        fail(f"row {i}: column '{col}' is not finite")
    return v


def parse_range(spec: str, name: str) -> Tuple[str, str]:
    if ":" not in spec:
        fail(f"--{name} must be FROM:TO, got {spec!r}")
    a, b = spec.split(":", 1)
    if a > b:
        fail(f"--{name}: FROM > TO ({spec})")
    return a.strip(), b.strip()


def bridge(rows: List[Dict[str, str]], period_col: str, base: Tuple[str, str], comp: Tuple[str, str],
           by: Optional[str], ratio: Optional[Tuple[str, str]], value: Optional[str], agg: str,
           multiply_by: Optional[str]) -> Dict[str, object]:
    # window -> group -> [num, den] or value-by-period
    sums: Dict[str, Dict[str, List[float]]] = {"base": defaultdict(lambda: [0.0, 0.0]),
                                               "compare": defaultdict(lambda: [0.0, 0.0])}
    per_period: Dict[str, Dict[str, Dict[str, float]]] = {"base": defaultdict(lambda: defaultdict(float)),
                                                           "compare": defaultdict(lambda: defaultdict(float))}
    periods = {"base": set(), "compare": set()}
    missing_mult = 0
    for i, r in enumerate(rows, start=2):
        p = (r.get(period_col) or "").strip()
        win = "base" if base[0] <= p <= base[1] else ("compare" if comp[0] <= p <= comp[1] else None)
        if win is None:
            continue
        periods[win].add(p)
        g = (r.get(by) or "(blank)").strip() if by else "(all)"
        m = 1.0
        if multiply_by:
            raw = r.get(multiply_by)
            if raw is None or str(raw).strip() == "":
                missing_mult += 1
                continue
            m = num(raw, multiply_by, i)
        if ratio:
            sums[win][g][0] += num(r.get(ratio[0]), ratio[0], i) * m
            sums[win][g][1] += num(r.get(ratio[1]), ratio[1], i) * m
        else:
            per_period[win][g][p] += num(r.get(value), value, i) * m
    for w in ("base", "compare"):
        if not periods[w]:
            fail(f"no rows in the {w} window; check --{w} against the '{period_col}' values")

    groups = sorted(set(sums["base"]) | set(sums["compare"]) | set(per_period["base"]) | set(per_period["compare"]))
    res: Dict[str, object] = {"type": "ratio" if ratio else "value", "by": by, "base": list(base), "compare": list(comp),
                              "periods": {k: len(v) for k, v in periods.items()}, "multiply_by": multiply_by,
                              "rows_skipped_missing_multiplier": missing_mult}
    out_groups = []
    if ratio:
        tn = {w: sum(v[0] for v in sums[w].values()) for w in sums}
        td = {w: sum(v[1] for v in sums[w].values()) for w in sums}
        if td["base"] <= 0 or td["compare"] <= 0:
            fail("denominator total is zero in a window")
        r1, r2 = tn["base"] / td["base"], tn["compare"] / td["compare"]
        rbar = (r1 + r2) / 2
        for g in groups:
            n1, d1 = sums["base"][g] if g in sums["base"] else (0.0, 0.0)
            n2, d2 = sums["compare"][g] if g in sums["compare"] else (0.0, 0.0)
            w1, w2 = d1 / td["base"], d2 / td["compare"]
            g1 = n1 / d1 if d1 > 0 else None
            g2 = n2 / d2 if d2 > 0 else None
            if g1 is None and g2 is None:
                continue
            g1v = g1 if g1 is not None else g2
            g2v = g2 if g2 is not None else g1
            rate = (g2v - g1v) * (w1 + w2) / 2
            mix = (w2 - w1) * ((g1v + g2v) / 2 - rbar)
            out_groups.append({"group": g, "base_kpi": g1, "compare_kpi": g2, "base_weight": w1, "compare_weight": w2,
                               "base_num": n1, "base_den": d1, "compare_num": n2, "compare_den": d2,
                               "rate_effect": rate, "mix_effect": mix, "contribution": rate + mix})
        res.update({"base_kpi": r1, "compare_kpi": r2, "delta": r2 - r1,
                    "check_sum": sum(x["contribution"] for x in out_groups)})
    else:
        def window_value(w: str, g: str) -> float:
            vals = per_period[w].get(g, {})
            if agg == "sum":
                return sum(vals.values())
            # mean over all periods of the window (missing period for a group = 0)
            return sum(vals.values()) / len(periods[w])
        v1 = sum(window_value("base", g) for g in groups)
        v2 = sum(window_value("compare", g) for g in groups)
        for g in groups:
            a, b = window_value("base", g), window_value("compare", g)
            out_groups.append({"group": g, "base_value": a, "compare_value": b, "contribution": b - a,
                               "change_pct": ((b - a) / a) if a else None})
        delta = v2 - v1
        for x in out_groups:
            x["share_of_delta"] = (x["contribution"] / delta) if delta else None
        res.update({"agg": agg, "base_kpi": v1, "compare_kpi": v2, "delta": delta,
                    "delta_pct": (delta / v1) if v1 else None})
    out_groups.sort(key=lambda x: -abs(x["contribution"]))
    res["groups"] = out_groups
    return res


def to_markdown(res: Dict[str, object], top: Optional[int]) -> str:
    g = res["groups"][:top] if top else res["groups"]
    head = f"base {res['base'][0]}–{res['base'][1]} ({res['periods']['base']} periods) vs. compare " \
           f"{res['compare'][0]}–{res['compare'][1]} ({res['periods']['compare']} periods)"
    out = ["## KPI bridge", f"- {head}" + (f"; weighted by `{res['multiply_by']}`" if res["multiply_by"] else "")]
    if res["rows_skipped_missing_multiplier"]:
        out.append(f"- ⚠ {res['rows_skipped_missing_multiplier']} row(s) skipped: missing `{res['multiply_by']}`")
    if res["type"] == "ratio":
        out.append(f"- KPI: **{res['base_kpi']:.1%} → {res['compare_kpi']:.1%}** (Δ {res['delta'] * 100:+.2f} pts)")
        if res["by"]:
            out += ["", f"### Contribution by `{res['by']}` (pts of the KPI)", "",
                    "| group | KPI base | KPI compare | weight base | weight compare | rate effect | mix effect | total | share of Δ |",
                    "|---|---|---|---|---|---|---|---|---|"]
            for x in g:
                share = (x["contribution"] / res["delta"]) if res["delta"] else None
                kb = "–" if x["base_kpi"] is None else f"{x['base_kpi']:.1%}"
                kc = "–" if x["compare_kpi"] is None else f"{x['compare_kpi']:.1%}"
                out.append(f"| {x['group']} | {kb} | {kc} | {x['base_weight']:.1%} | {x['compare_weight']:.1%} | "
                           f"{x['rate_effect'] * 100:+.2f} | {x['mix_effect'] * 100:+.2f} | **{x['contribution'] * 100:+.2f}** | "
                           + ("–" if share is None else f"{share:.0%}") + " |")
            out.append("")
            out.append("Rate effect = the group's own KPI changed; mix effect = its share of the denominator changed "
                       "relative to an above/below-average KPI. Rate + mix over all groups = Δ.")
    else:
        dp = "" if res["delta_pct"] is None else f" ({res['delta_pct']:+.1%})"
        out.append(f"- KPI ({res['agg']} over the window): **{res['base_kpi']:,.0f} → {res['compare_kpi']:,.0f}** "
                   f"(Δ {res['delta']:+,.0f}{dp})")
        if res["by"]:
            out += ["", f"### Contribution by `{res['by']}`", "",
                    "| group | base | compare | Δ | Δ % | share of total Δ |", "|---|---|---|---|---|---|"]
            for x in g:
                cp = "–" if x["change_pct"] is None else f"{x['change_pct']:+.0%}"
                sh = "–" if x["share_of_delta"] is None else f"{x['share_of_delta']:.0%}"
                out.append(f"| {x['group']} | {x['base_value']:,.0f} | {x['compare_value']:,.0f} | "
                           f"**{x['contribution']:+,.0f}** | {cp} | {sh} |")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data")
    kpi = ap.add_mutually_exclusive_group(required=True)
    kpi.add_argument("--ratio", nargs=2, metavar=("NUM", "DEN"))
    kpi.add_argument("--value")
    ap.add_argument("--agg", choices=["sum", "mean"], default="sum")
    ap.add_argument("--period-col", default="period")
    ap.add_argument("--base", required=True)
    ap.add_argument("--compare", required=True)
    ap.add_argument("--by")
    ap.add_argument("--join")
    ap.add_argument("--on", default="sku_id")
    ap.add_argument("--multiply-by")
    ap.add_argument("--top", type=int)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    cols, rows = read(a.data)
    if a.join:
        jcols, jrows = read(a.join)
        if a.on not in cols or a.on not in jcols:
            fail(f"--on column '{a.on}' must exist in both files")
        lookup = {r[a.on].strip(): r for r in jrows}
        unmatched = 0
        for r in rows:
            extra = lookup.get((r.get(a.on) or "").strip())
            if extra is None:
                unmatched += 1
                continue
            for k, v in extra.items():
                if k not in r:
                    r[k] = v
        cols = cols + [c for c in jcols if c not in cols]
        if unmatched:
            print(f"Note: {unmatched} row(s) without a match in {a.join}", file=sys.stderr)
    needed = [a.period_col] + (list(a.ratio) if a.ratio else [a.value]) + ([a.by] if a.by else []) \
        + ([a.multiply_by] if a.multiply_by else [])
    missing = [c for c in needed if c not in cols]
    if missing:
        fail(f"missing column(s) {missing}. Available: {cols}")
    res = bridge(rows, a.period_col, parse_range(a.base, "base"), parse_range(a.compare, "compare"), a.by,
                 tuple(a.ratio) if a.ratio else None, a.value, a.agg, a.multiply_by)
    print(json.dumps(res, indent=2) if a.json else to_markdown(res, a.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
