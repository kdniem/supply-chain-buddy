#!/usr/bin/env python3
"""TODO One-line purpose.

Input CSV columns (header required):
    sku_id      TODO description
    value       TODO description

Usage:
    python3 example_script.py input.csv [--json]

Standard library only. Deterministic. Prints a Markdown table (default) or JSON.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import Dict, List

REQUIRED_COLUMNS = ["sku_id", "value"]


def load_rows(path: str) -> List[Dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"Input error: missing column(s) {missing}. Found: {reader.fieldnames}")
        return list(reader)


def parse_float(raw: str, column: str, row_number: int) -> float:
    try:
        return float(raw)
    except (TypeError, ValueError):
        sys.exit(f"Input error: column '{column}' row {row_number} is not a number: {raw!r}")


def compute(rows: List[Dict[str, str]]) -> List[Dict[str, object]]:
    """TODO Replace with the real calculation."""
    results = []
    for i, row in enumerate(rows, start=2):  # row 1 is the header
        results.append({"sku_id": row["sku_id"], "value": parse_float(row["value"], "value", i)})
    return results


def to_markdown(results: List[Dict[str, object]]) -> str:
    if not results:
        return "_No rows._"
    headers = list(results[0].keys())
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in results:
        lines.append("| " + " | ".join(str(r[h]) for h in headers) + " |")
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", help="Path to input CSV")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown")
    args = parser.parse_args(argv)

    results = compute(load_rows(args.input))
    print(json.dumps(results, indent=2) if args.json else to_markdown(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
