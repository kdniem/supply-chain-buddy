# Data intake protocol

How the Buddy asks for, receives and checks data. Each skill lists its specific needs in its *Data requirements* table. This protocol covers the common mechanics.

## 1. Data tiers: always know which tier you are working at
| Tier | What the user provided | What you can deliver | How to label it |
|---|---|---|---|
| **T0: No data** | Only a description | Method, framework, structured hypotheses, an illustrative example with stated assumptions | "Illustrative, based on assumptions" |
| **T1: Summary figures** | A few aggregates (e.g. average demand, lead time, total inventory) | Order-of-magnitude calculations, first prioritisation | "Indicative, based on aggregates" |
| **T2: Item-level extract** | Tables per SKU / supplier / period | Real analysis via scripts: segmentation, parameters, error metrics | "Based on your data (n = …, period …)" |
| **T3: Rich dataset** | T2 plus history, master data and cost data | Full diagnostic and quantified options | Same as T2, plus a data quality statement |

State the tier you are working at once, near the start of the answer. Offer to move up a tier when it would change the conclusion.

## 2. How to ask for data
1. **Explain the purpose** in one line per item ("Lead time variability. Without it, safety stock is likely understated").
2. **Specify the form:** columns, granularity (day/week/month), horizon (e.g. 12–24 months of history), units.
3. **Offer a template:** show a CSV header and two example rows the user can copy.
4. **Give a minimum and an ideal version.** Users often have the minimum ready today.
5. **Accept any format.** CSV, Excel, pasted tables and screenshots of tables are all fine. Convert Excel to CSV before running scripts.
6. **Suggest anonymising** names that the analysis does not need.

Example request block:
```
To size safety stocks I need, per SKU:
  sku_id, period, demand_qty        (weekly, last 52+ weeks)
  sku_id, lead_time_days[, lead_time_std_days], unit_cost
Minimum: average weekly demand, its standard deviation and lead time for your top 20 SKUs.
Template:
  sku_id,period,demand_qty
  A-100,2026-W01,120
```

## 3. Standard data objects
| Object | Typical columns (snake_case) | Typical source |
|---|---|---|
| Demand history | `sku_id, period, demand_qty` [, `location_id`, `customer_id`] | ERP sales orders/shipments; prefer **demand** (orders) over shipments when stock-outs occurred |
| Forecast history | `sku_id, period, forecast_qty, forecast_lag` | Planning system snapshots (the lag matters!) |
| Item master | `sku_id, description, unit_cost, uom, lifecycle_status, category` | ERP |
| Inventory snapshot | `sku_id, location_id, on_hand_qty, date` | ERP / WMS |
| Replenishment parameters | `sku_id, lead_time_days, moq, order_multiple, review_period_days, safety_stock_qty` | ERP / APS |
| Supplier performance | `supplier_id, po_id, promised_date, received_date, qty_ordered, qty_received` | ERP purchasing |
| Spend | `supplier_id, category, spend_amount, period` | ERP / spend cube |
| Service | `period, order_lines, lines_on_time_in_full` (or order level) | ERP / BI |

## 4. Checks on received data (run before analysing)
Report the results in a short **data quality note**:
- **Completeness:** missing values per column, SKUs without history, gaps in periods.
- **Plausibility:** negative or zero quantities, extreme outliers (> 4 standard deviations or > 10× the median), returns netted into demand.
- **Units and time basis:** consistent UoM, days vs. weeks, calendar vs. working days.
- **Censored demand:** periods with stock-outs understate true demand. Ask whether shipments or orders were provided.
- **Coverage:** period length vs. lead time and seasonality (aim for at least 2 seasonal cycles for seasonal items).
- **Sample size:** state *n* and the period covered.

If issues are material, say how they affect conclusions and how you treated them (excluded, capped or flagged). Never silently "fix" data.

## 5. When the user cannot provide data
Proceed at T0/T1. Use explicit, conservative, replaceable assumptions. Show which assumptions drive the result most, so the user knows what to collect first.
