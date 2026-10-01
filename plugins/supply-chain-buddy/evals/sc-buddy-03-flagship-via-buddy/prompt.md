---
description: FLAGSHIP via the orchestrator. Full diagnosis on fictional Brightvale data, integrated brief.
tags: [sc-buddy, analysis, demo-brightvale, flagship]
expected_outcome: Buddy routes to diagnostic (and specialists), finds SUP-03 lead time as service driver and HYDR/FAST/PNEU as inventory drivers, delivers one integrated, prioritised answer.
max_turns: 45
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

Hey Supply Chain Buddy, our fill rate dropped from about 96-97% last autumn to about 88% this summer, while our average inventory value went up roughly 15%. What's going on, and what should we do first?

All exports are in the current folder: monthly_kpis.csv, order_fulfillment.csv, inventory_snapshots.csv, item_master.csv, supplier_receipts.csv, replenishment_params.csv, demand_history.csv and forecast_history.csv.
