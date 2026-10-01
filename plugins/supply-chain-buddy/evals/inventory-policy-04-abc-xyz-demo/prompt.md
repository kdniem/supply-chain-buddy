---
description: Analysis with file data (fictional Brightvale dataset). ABC/XYZ segmentation and treatment recommendations.
tags: [inventory-policy, analysis, demo-brightvale]
expected_outcome: Value-based ABC (18 A items ≈ 81% of value, 14 AX), identifies intermittent/lumpy items, recommends differentiated treatment.
max_turns: 20
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

I've put two files in the current folder: demand_history.csv (weekly customer demand for our 40 stocked SKUs over the last 52 weeks) and item_master.csv (incl. unit costs). Please do an ABC/XYZ analysis and tell me which groups of items need a different inventory treatment than they get today. Today every item gets the same safety stock rule.
