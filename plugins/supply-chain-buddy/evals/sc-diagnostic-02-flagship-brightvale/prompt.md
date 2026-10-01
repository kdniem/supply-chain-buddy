---
description: FLAGSHIP. Full diagnosis on the fictional Brightvale dataset (service down, inventory up).
tags: [sc-diagnostic, analysis, demo-brightvale, flagship]
expected_outcome: SUP-03 lead time doubling (ERP not updated) as main fill-rate driver; inventory increase from HYDR project/forecast uplift, FAST MOQ increase (SUP-05) and PNEU demand decline; no blanket SS increase; actions incl. lead time master data update.
max_turns: 40
timeout_seconds: 1500
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

Our fill rate dropped from about 96-97% last autumn to about 88% this summer, while our average inventory value went up roughly 15%. What's going on, and what should we do?

All our data exports are in the current folder: monthly_kpis.csv, order_fulfillment.csv (weekly demand and shipped quantity per SKU), inventory_snapshots.csv (weekly on-hand per SKU), item_master.csv, supplier_receipts.csv (purchase orders with order, promised and receipt dates), replenishment_params.csv (current ERP settings), demand_history.csv and forecast_history.csv.
