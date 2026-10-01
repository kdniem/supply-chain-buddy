---
description: Advisory/routing. MAPE-based accuracy target on SKU level with many low-volume items.
tags: [demand-planning-review, advisory, routing]
expected_outcome: Explains MAPE problems at low volumes, proposes wMAPE/MASE + bias + naive benchmark at a defined lag/level, pushes back on an externally copied target.
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Our monthly report shows a forecast error of 58% MAPE at SKU level. Management read that "best in class" companies reach 85% forecast accuracy and wants that as our target for next year. About a third of our SKUs sell fewer than 10 units a month. How should I respond, and how should we actually measure this?
