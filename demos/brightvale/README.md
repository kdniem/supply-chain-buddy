# Demo dataset: Brightvale Industrial Supply (fictional)

**Brightvale Industrial Supply** is a *fictional* mid-sized distributor of industrial MRO components: bearings, seals, hydraulics, electrical, pneumatics, fasteners and safety equipment. It runs one central warehouse, carries 40 stocked SKUs and buys from 7 suppliers. All data is synthetic. It comes from a deterministic weekly inventory simulation (`generate.py`), so the files are internally consistent.

## The situation (flagship demo prompt)
> "Our fill rate dropped from about 96–97% last autumn to about 88% this summer, while our average inventory value went up roughly 15%. What's going on and what should we do?"

`monthly_kpis.csv` shows this pattern. Comparing Q4 2025 with Q3 2026:

| Metric | Q4 2025 | Q3 2026 |
|---|---|---|
| Value-weighted unit fill rate | ≈ 96.7% | ≈ 88% |
| Average inventory value | ≈ 67k | ≈ 78k (+16%) |

## Files (`data/`)
| File | Grain | Columns |
|---|---|---|
| `demand_history.csv` | SKU × ISO week, 2025-W41 … 2026-W40 | `sku_id, period, demand_qty`. **Customer demand including unfilled demand**, not just shipments |
| `forecast_history.csv` | SKU × week | `sku_id, period, forecast_qty, forecast_lag_weeks` (forecast made 4 weeks ahead) |
| `item_master.csv` | SKU | `sku_id, description, category, supplier_id, unit_cost` |
| `replenishment_params.csv` | SKU, current ERP settings at end of 2026-W40 | `sku_id, lead_time_days, order_qty, safety_stock_qty, reorder_point_qty, on_hand_qty, open_po_qty` |
| `supplier_receipts.csv` | Purchase order | `po_id, supplier_id, sku_id, order_date, promised_date, received_date, qty` (`received_date` empty = still open) |
| `monthly_kpis.csv` | Month | `month, demand_value, fill_rate_value` (value-weighted unit fill rate), `sku_weeks_with_demand, sku_week_fill_complete, avg_inventory_value` |

Replenishment logic in the simulation: continuous review (s, Q). An order of Q is placed when the inventory position (on hand + on order) falls to the reorder point or below. Unfilled demand is lost, because customers buy elsewhere.

## How to use it
- **Flagship demo:** give the prompt above plus the files to Supply Chain Buddy.
- **Inventory policy:** `inventory-policy` scripts on `demand_history.csv` + `item_master.csv` (ABC/XYZ), then safety stocks with lead times from `supplier_receipts.csv`.
- **Forecasting:** `forecast_history.csv` vs. `demand_history.csv` (bias, wMAPE, FVA vs. naive).
- **Facilitators:** the root causes are documented in [ANSWER_KEY.md](ANSWER_KEY.md). Don't show it to the model.

Regenerate with `python3 generate.py` (same seed, same files).
