#!/usr/bin/env python3
"""Turn one or more `claude plugin eval --json` result files into Markdown tables for evals/README.md.

Usage:
    python3 tools/eval_table.py "<label>=<path/to/result.json>" ["<label>=<path>" ...]
Prints a summary table (one row per result file) and a per-case table (one column pair per file).
"""
from __future__ import annotations

import json
import sys
from typing import Dict, List, Tuple


def load(spec: str) -> Tuple[str, dict]:
    if "=" not in spec:
        sys.exit(f"argument must be LABEL=PATH, got {spec!r}")
    label, path = spec.split("=", 1)
    with open(path, encoding="utf-8") as fh:
        return label, json.load(fh)


def mean(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main(argv: List[str]) -> int:
    if not argv:
        sys.exit(__doc__)
    results = [load(a) for a in argv]
    out = ["| Run | Claude Code | Cases | Runs/arm | With plugin | Without | Mean Δ |", "|---|---|---|---|---|---|---|"]
    for label, d in results:
        cases = d["cases"]
        with_s = mean([c["aggregates"]["score"] for c in cases])
        without_s = mean([c["aggregates"].get("scoreWithout", 0.0) for c in cases])
        runs = cases[0].get("runsPerCase", "?") if cases else "?"
        out.append(f"| {label} | {d.get('claudeVersion', '?')} | {len(cases)} | {runs} | {with_s:.2f} | {without_s:.2f} | "
                   f"{d['aggregates'].get('meanDelta', with_s - without_s):+.2f} |")
    names: List[str] = []
    for _, d in results:
        for c in d["cases"]:
            if c["name"] not in names:
                names.append(c["name"])
    out += ["", "| Case | " + " | ".join(f"{lbl}: with / without" for lbl, _ in results) + " |",
            "|---|" + "---|" * len(results)]
    for n in sorted(names):
        cells = []
        for _, d in results:
            c: Dict = next((x for x in d["cases"] if x["name"] == n), None)
            if c is None:
                cells.append("–")
            else:
                a = c["aggregates"]
                cells.append(f"{a['score']:.2f} / {a.get('scoreWithout', 0.0):.2f}")
        out.append(f"| {n} | " + " | ".join(cells) + " |")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
