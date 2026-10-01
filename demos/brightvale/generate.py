#!/usr/bin/env python3
"""Generate the fictional Brightvale Industrial Supply dataset (deterministic).

Brightvale is a FICTIONAL mid-sized distributor of industrial MRO components. Any resemblance to a
real company is coincidental. The dataset backs the flagship demo:
  "Our fill rate dropped from ~96% to ~89% while inventory went up ~15%. What's going on?"

A weekly inventory simulation (52 weeks, 2025-W41 .. 2026-W40) produces internally consistent data.
Hidden root causes (see ANSWER_KEY.md):
  1. Supplier SUP-03 lead time roughly doubled from week 22 on; ERP lead times were never updated
     -> stock-outs on several A items.
  2. A legacy pneumatics range (category PNEU) lost ~30% of demand from week 18 on; forecasts and
     order quantities were not adjusted -> excess stock.
  3. Supplier SUP-05 raised minimum order quantities from week 20 on -> more cycle stock on C items.
  4. Hydraulics (HYDR): safety stock raised by ~2 weeks of demand from week 24 on for an anticipated
     customer project that never materialised -> expensive excess stock.
  Forecasts: the final (consensus) forecast overrides the statistical one. PNEU stays locked to
  the budget after the decline; HYDR gets a +35% sales uplift for the project from week 20 on.
  5. Safety stock is a flat "0.5 weeks of average demand" for every SKU -> too little for volatile
     A items, too much for stable or slow items; lumpy items are not treated differently.

Usage:  python3 generate.py            (writes ./data/*.csv)
"""
from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

SEED = 7
WEEKS = 52
START = date(2025, 10, 6)  # Monday of ISO week 2025-W41
OUT = Path(__file__).resolve().parent / "data"

SUP03_SHIFT_WEEK = 22
PNEU_DECLINE_WEEK = 18
PNEU_DECLINE = 0.70   # demand multiplier after decline
SUP05_MOQ_WEEK = 20
SUP05_MOQ_FACTOR = 3.0
SS_WEEKS_OF_COVER = 0.5
SALES_UPLIFT_WEEK = 20     # sales adds the expected project to the HYDR forecast
SALES_UPLIFT = 1.35
PROJECT_WEEK = 24          # anticipated project demand -> stock build on hydraulics
PROJECT_WEEKS_OF_DEMAND = 2

# sku_id, description, category, supplier, unit_cost, mean weekly demand, cv, prob of demand per week
CATALOG = [
    ("BRG-6204", "Deep groove ball bearing 6204-2RS", "BEAR", "SUP-03", 4.80, 420, 0.30, 1.0),
    ("BRG-6305", "Deep groove ball bearing 6305-2RS", "BEAR", "SUP-03", 9.60, 210, 0.45, 1.0),
    ("BRG-UCP208", "Pillow block bearing UCP208", "BEAR", "SUP-03", 27.50, 60, 0.55, 1.0),
    ("SEAL-OR-50", "O-ring kit NBR 50 pcs", "SEAL", "SUP-01", 12.40, 160, 0.25, 1.0),
    ("SEAL-SH-40", "Shaft seal 40x62x8", "SEAL", "SUP-03", 6.90, 140, 0.50, 1.0),
    ("HYD-HOSE-12", "Hydraulic hose 1/2in per 10m", "HYDR", "SUP-02", 58.00, 38, 0.35, 1.0),
    ("HYD-FIT-08", "Hydraulic fitting JIC 1/2in", "HYDR", "SUP-02", 7.20, 260, 0.30, 1.0),
    ("HYD-PUMP-G2", "Gear pump group 2", "HYDR", "SUP-02", 410.00, 4, 0.60, 0.95),
    ("ELE-CONT-25", "Contactor 25A 24VDC", "ELEC", "SUP-04", 38.50, 45, 0.40, 1.0),
    ("ELE-PROX-M18", "Inductive proximity sensor M18", "ELEC", "SUP-03", 31.00, 70, 0.50, 1.0),
    ("ELE-RELAY-4", "Plug-in relay 4CO", "ELEC", "SUP-04", 8.90, 120, 0.35, 1.0),
    ("ELE-PSU-10", "DIN rail power supply 24V 10A", "ELEC", "SUP-04", 96.00, 9, 0.55, 0.95),
    ("PNEU-CYL-50", "Pneumatic cylinder 50x200", "PNEU", "SUP-06", 74.00, 22, 0.45, 1.0),
    ("PNEU-VAL-52", "5/2 solenoid valve G1/4", "PNEU", "SUP-06", 52.00, 30, 0.40, 1.0),
    ("PNEU-FRL-14", "Filter regulator lubricator G1/4", "PNEU", "SUP-06", 64.00, 14, 0.50, 1.0),
    ("PNEU-FIT-08", "Push-in fitting 8mm", "PNEU", "SUP-06", 1.90, 380, 0.30, 1.0),
    ("PNEU-TUBE-08", "PU tubing 8mm per 50m", "PNEU", "SUP-06", 29.00, 40, 0.35, 1.0),
    ("FAS-M8-25", "Hex bolt M8x25 8.8 box 100", "FAST", "SUP-05", 6.20, 150, 0.30, 1.0),
    ("FAS-M10-40", "Hex bolt M10x40 8.8 box 50", "FAST", "SUP-05", 7.80, 95, 0.35, 1.0),
    ("FAS-NUT-M8", "Hex nut M8 box 200", "FAST", "SUP-05", 4.10, 120, 0.30, 1.0),
    ("FAS-WSH-M10", "Washer M10 box 200", "FAST", "SUP-05", 3.20, 70, 0.40, 1.0),
    ("FAS-ANC-12", "Heavy duty anchor M12", "FAST", "SUP-05", 2.60, 60, 0.70, 0.85),
    ("SAF-GLV-L", "Cut resistant gloves L (pair)", "SAFE", "SUP-07", 4.50, 230, 0.25, 1.0),
    ("SAF-GLS-CL", "Safety glasses clear", "SAFE", "SUP-07", 3.80, 140, 0.30, 1.0),
    ("SAF-EAR-200", "Ear plugs box 200", "SAFE", "SUP-07", 18.00, 25, 0.45, 1.0),
    ("SAF-HARN-1", "Fall arrest harness", "SAFE", "SUP-07", 89.00, 3, 0.70, 0.55),
    ("BRG-6206", "Deep groove ball bearing 6206-2RS", "BEAR", "SUP-01", 6.10, 35, 0.60, 0.95),
    ("BRG-NU210", "Cylindrical roller bearing NU210", "BEAR", "SUP-01", 64.00, 3, 0.80, 0.45),
    ("SEAL-GSK-DN50", "Flange gasket DN50", "SEAL", "SUP-01", 3.40, 22, 0.80, 0.70),
    ("SEAL-PACK-12", "Gland packing 12mm per kg", "SEAL", "SUP-01", 46.00, 2, 0.90, 0.35),
    ("HYD-CYL-63", "Hydraulic cylinder 63x300", "HYDR", "SUP-02", 380.00, 1.5, 0.80, 0.30),
    ("HYD-FILT-10", "Return line filter element 10um", "HYDR", "SUP-02", 24.00, 18, 0.60, 0.85),
    ("ELE-VFD-2K2", "Frequency inverter 2.2kW", "ELEC", "SUP-04", 520.00, 1.2, 0.90, 0.30),
    ("ELE-CBL-3G15", "Control cable 3G1.5 per 100m", "ELEC", "SUP-04", 71.00, 6, 0.70, 0.60),
    ("FAS-THR-M12", "Threaded rod M12 1m", "FAST", "SUP-05", 3.90, 14, 0.90, 0.60),
    ("FAS-CLIP-20", "Spring clip 20mm box 100", "FAST", "SUP-05", 5.50, 6, 1.00, 0.40),
    ("FAS-RIV-48", "Blind rivet 4.8 box 500", "FAST", "SUP-05", 14.00, 4, 1.10, 0.35),
    ("SAF-SIGN-EX", "Emergency exit sign", "SAFE", "SUP-07", 21.00, 1.0, 0.90, 0.30),
    ("PNEU-SIL-14", "Pneumatic silencer G1/4", "PNEU", "SUP-06", 2.40, 12, 0.90, 0.55),
    ("PNEU-GAUGE-63", "Pressure gauge 63mm 0-10bar", "PNEU", "SUP-06", 11.00, 5, 0.90, 0.45),
]

# supplier: (lead time weeks mean, std) in normal times; SUP-03 changes after SUP03_SHIFT_WEEK
SUPPLIERS = {
    "SUP-01": (2.0, 0.4), "SUP-02": (3.0, 0.6), "SUP-03": (2.0, 0.4), "SUP-04": (2.0, 0.5),
    "SUP-05": (1.0, 0.3), "SUP-06": (3.0, 0.5), "SUP-07": (1.0, 0.3),
}
SUP03_AFTER = (4.5, 1.2)


def iso_label(week_index: int) -> str:
    d = START + timedelta(weeks=week_index)
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def month_label(week_index: int) -> str:
    d = START + timedelta(weeks=week_index)
    return f"{d.year}-{d.month:02d}"


def draw_demand(rng: random.Random, mean: float, cv: float, p: float) -> int:
    if rng.random() > p:
        return 0
    size_mean = mean / p
    sigma = math.sqrt(math.log(1 + cv ** 2))
    mu = math.log(size_mean) - sigma ** 2 / 2
    return max(0, int(round(rng.lognormvariate(mu, sigma))))


def draw_lead_time(rng: random.Random, supplier: str, week: int) -> int:
    mean, std = SUP03_AFTER if (supplier == "SUP-03" and week >= SUP03_SHIFT_WEEK) else SUPPLIERS[supplier]
    return max(1, int(round(rng.gauss(mean, std))))


def main() -> None:
    rng = random.Random(SEED)
    OUT.mkdir(parents=True, exist_ok=True)

    demand_rows, forecast_rows, receipt_rows, param_rows, item_rows = [], [], [], [], []
    fulfillment_rows, snapshot_rows = [], []
    weekly = defaultdict(lambda: {"demand": 0.0, "filled": 0.0, "lines": 0, "lines_full": 0, "inv_value": 0.0})
    po_counter = 1

    for sku, desc, cat, sup, cost, mean, cv, p in CATALOG:
        # --- demand path (with PNEU decline) ---
        demand = []
        for w in range(WEEKS):
            m = mean * (PNEU_DECLINE if (cat == "PNEU" and w >= PNEU_DECLINE_WEEK) else 1.0)
            demand.append(draw_demand(rng, m, cv, p))

        # --- static ERP parameters, set at start from the planned (pre-change) mean demand ---
        lt_sys_weeks = int(SUPPLIERS[sup][0])
        q_base = max(1, int(round(mean * (2 if mean >= 20 else 4))))  # ~2-4 weeks of demand per order
        ss_sys = int(math.ceil(SS_WEEKS_OF_COVER * mean))
        rop = int(math.ceil(mean * lt_sys_weeks + ss_sys))

        on_hand = int(rop + q_base / 2)
        pipeline = []  # (arrival_week, qty, po_id)
        for w in range(WEEKS):
            q = int(math.ceil(q_base * SUP05_MOQ_FACTOR)) if (sup == "SUP-05" and w >= SUP05_MOQ_WEEK) else q_base
            # receive
            arrived = [x for x in pipeline if x[0] == w]
            pipeline = [x for x in pipeline if x[0] != w]
            on_hand += sum(x[1] for x in arrived)
            # serve demand (unfilled demand is lost: customers buy elsewhere)
            d = demand[w]
            filled = min(on_hand, d)
            on_hand -= filled
            agg = weekly[w]
            agg["demand"] += d * cost
            agg["filled"] += filled * cost
            if d > 0:
                agg["lines"] += 1
                agg["lines_full"] += 1 if filled == d else 0
            # statistical forecast at lag 4: 8-week moving average of demand known 4 weeks earlier
            hist = demand[max(0, w - 12): max(0, w - 4)]
            stat = (sum(hist) / len(hist)) if hist else mean
            # final (consensus) forecast: planners override the statistical forecast
            final = stat
            if cat == "PNEU" and w >= PNEU_DECLINE_WEEK:
                final = mean                       # locked to the annual budget; decline not accepted
            elif cat == "HYDR" and w >= SALES_UPLIFT_WEEK:
                final = stat * SALES_UPLIFT        # sales expects the customer project
            forecast_rows.append((sku, iso_label(w), round(stat, 1), round(final, 1), 4))
            # replenish (s, Q): order multiples of Q until position > ROP
            uplift = int(math.ceil(PROJECT_WEEKS_OF_DEMAND * mean)) if (cat == "HYDR" and w >= PROJECT_WEEK) else 0
            position = on_hand + sum(x[1] for x in pipeline)
            while position <= rop + uplift:
                lt = draw_lead_time(rng, sup, w)
                po = f"PO-{po_counter:05d}"
                po_counter += 1
                pipeline.append((w + lt, q, po))
                order_date = START + timedelta(weeks=w, days=1)
                received = START + timedelta(weeks=w + lt, days=1)
                receipt_rows.append((po, sup, sku, order_date.isoformat(),
                                     (order_date + timedelta(weeks=lt_sys_weeks)).isoformat(),
                                     received.isoformat() if w + lt < WEEKS else "", q))
                position += q
            agg["inv_value"] += on_hand * cost
            demand_rows.append((sku, iso_label(w), d))
            fulfillment_rows.append((sku, iso_label(w), d, filled))
            snapshot_rows.append((sku, iso_label(w), on_hand, sum(x[1] for x in pipeline)))

        open_po_qty = sum(x[1] for x in pipeline)
        item_rows.append((sku, desc, cat, sup, f"{cost:.2f}"))
        param_rows.append((sku, lt_sys_weeks * 7, q_base if not (sup == "SUP-05") else int(math.ceil(q_base * SUP05_MOQ_FACTOR)),
                           ss_sys + uplift, rop + uplift, on_hand, open_po_qty))

    with open(OUT / "demand_history.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sku_id", "period", "demand_qty"])
        w.writerows(demand_rows)
    with open(OUT / "forecast_history.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sku_id", "period", "stat_forecast_qty", "forecast_qty", "forecast_lag_weeks"])
        w.writerows(forecast_rows)
    with open(OUT / "item_master.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sku_id", "description", "category", "supplier_id", "unit_cost"])
        w.writerows(item_rows)
    with open(OUT / "replenishment_params.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sku_id", "lead_time_days", "order_qty", "safety_stock_qty", "reorder_point_qty",
                    "on_hand_qty", "open_po_qty"])
        w.writerows(param_rows)
    with open(OUT / "supplier_receipts.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["po_id", "supplier_id", "sku_id", "order_date", "promised_date", "received_date", "qty"])
        w.writerows(receipt_rows)

    with open(OUT / "order_fulfillment.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sku_id", "period", "demand_qty", "shipped_qty"])
        w.writerows(fulfillment_rows)
    with open(OUT / "inventory_snapshots.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sku_id", "period", "on_hand_qty", "on_order_qty"])
        w.writerows(snapshot_rows)

    months = defaultdict(lambda: {"demand": 0.0, "filled": 0.0, "lines": 0, "lines_full": 0, "inv": [], })
    for wk in range(WEEKS):
        m = months[month_label(wk)]
        a = weekly[wk]
        m["demand"] += a["demand"]
        m["filled"] += a["filled"]
        m["lines"] += a["lines"]
        m["lines_full"] += a["lines_full"]
        m["inv"].append(a["inv_value"])
    with open(OUT / "monthly_kpis.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["month", "demand_value", "fill_rate_value", "sku_weeks_with_demand",
                    "sku_week_fill_complete", "avg_inventory_value"])
        for month in sorted(months):
            m = months[month]
            w.writerow([month, round(m["demand"], 2), round(m["filled"] / m["demand"], 4), m["lines"],
                        round(m["lines_full"] / m["lines"], 4), round(sum(m["inv"]) / len(m["inv"]), 2)])
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
