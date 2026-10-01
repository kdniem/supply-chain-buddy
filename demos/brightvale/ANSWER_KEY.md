# Answer key: Brightvale flagship demo (facilitators and eval authors only)

The simulation in `generate.py` builds in five root causes. A good diagnosis finds most of them **from the data** and separates the *service* problem from the *inventory* problem. The two symptoms have mostly different causes. More stock overall did not help, because it sits on the wrong items.

| # | Root cause | Effect | Evidence in the data |
|---|---|---|---|
| 1 | **Supplier SUP-03 lead time more than doubled** from about 2026-W11 onwards. The ERP still plans with 14 days | Main driver of the **fill rate drop**: stock-outs on SUP-03 items, several of them A items (BRG-6204, BRG-6305, BRG-UCP208, SEAL-SH-40, ELE-PROX-M18) | `supplier_receipts.csv`: SUP-03 actual lead time averages about 13 days for orders placed before March 2026 and about 34 days for later orders, while promised = order + 14 days. `replenishment_params.csv`: `lead_time_days = 14`. BRG-6305 and SEAL-SH-40 end with zero on-hand |
| 2 | **Pneumatics (PNEU) demand fell by about a third** from about 2026-W07. Reorder points and order quantities were not adjusted | **Inventory up** on PNEU (expensive cylinders, valves, FRLs) | `demand_history.csv`: PNEU weekly demand about 530 before vs. about 340 after (−36%). Reorder points still sized on old demand |
| 3 | **SUP-05 raised minimum order quantities to 3×** from about 2026-W09 | **Inventory up** on fasteners (more cycle stock) | `replenishment_params.csv`: FAS-* `order_qty` is about 6 weeks of demand. `supplier_receipts.csv`: SUP-05 PO quantities triple |
| 4 | **Hydraulics safety stock raised by about 2 weeks of demand** from about 2026-W13 for a customer project that never materialised | **Inventory up** on expensive HYDR items (pump, hose, cylinder) | `replenishment_params.csv`: HYDR `safety_stock_qty` is about 2.5 weeks of demand vs. 0.5 for all other SKUs. Demand did not rise accordingly |
| 5 | **Flat safety stock rule:** 0.5 weeks of average demand for every SKU, regardless of variability, lead time or value | Structural: too little protection for volatile A items with longer lead times, the wrong buffer for lumpy C items, and no response to changed lead times | `safety_stock_qty / mean demand ≈ 0.5` for all non-HYDR SKUs. ABC/XYZ shows 10 lumpy SKUs treated like smooth ones |

## Forecasting layer
The final (consensus) forecast overrides the statistical forecast in two places. Both are visible as **bias and negative forecast value added (FVA)** of the consensus step:
- **PNEU:** after the decline, the final forecast stays locked to the budget (the pre-decline mean). The result is persistent over-forecasting, which is consistent with root cause 2.
- **HYDR:** from about 2026-W09 on, sales adds +35% for the expected customer project, consistent with root cause 4.

## Expected quantitative findings (approximate)
- ABC/XYZ on value (`abc_xyz.py` with `item_master.csv`), using the default cuts 80/95 and CV 0.5/1.0: **18 A items (≈81% of value)**, of which **14 AX**. There are **10 lumpy** and 3 intermittent SKUs.
- Top value SKUs: HYD-HOSE-12, ELE-PROX-M18, BRG-6305, SEAL-OR-50, HYD-FIT-08.
- SUP-03 lead time: about 13 days before vs. about 34 days after the change.

## What a strong answer recommends
1. **Update the SUP-03 lead times** in the ERP now, and expedite or escalate with SUP-03. This is the quickest fix for service.
2. **Replace the flat safety stock rule** with statistical safety stock by segment: higher CSL for AX/AY, lower for C, and a separate treatment for lumpy items.
3. **Re-baseline PNEU demand** and parameters. Stop replenishing until the stock is consumed, and consider returns or redistribution of the excess.
4. **Remove the project uplift** on HYDR. Introduce a governance rule that ties project stock to confirmed orders.
5. **Negotiate the SUP-05 MOQ**, or evaluate a TCO trade-off (holding cost vs. price).
6. **Process:** review parameters regularly, trigger alerts when supplier lead times drift, and add a demand-review step to S&OP.

A weak answer recommends "more safety stock everywhere" or blames forecasting alone without looking at lead times.
