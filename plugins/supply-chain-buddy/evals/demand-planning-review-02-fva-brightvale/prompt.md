---
description: Analysis with file data (fictional Brightvale). Accuracy, bias and FVA of the consensus step.
tags: [demand-planning-review, analysis, demo-brightvale]
expected_outcome: Finds that the final/consensus forecast is worse than the statistical one (negative FVA), with over-forecast bias concentrated in PNEU (budget lock after decline) and HYDR (sales uplift).
max_turns: 25
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

In the current folder you'll find demand_history.csv (weekly customer demand), forecast_history.csv (our statistical forecast and the final consensus forecast after the sales/management review, both made 4 weeks ahead) and item_master.csv. How good is our forecasting over the last six months (2026-W14 onwards), and where does it go wrong?
