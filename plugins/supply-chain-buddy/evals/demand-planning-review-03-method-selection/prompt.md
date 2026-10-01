---
description: Analysis with file data. Method selection for a mix of smooth and intermittent items.
tags: [demand-planning-review, analysis]
expected_outcome: Classifies VLV/GSK items as smooth and SPR items as intermittent/lumpy; recommends SES/MA for smooth and Croston-SBA/TSB-type methods for intermittent items, backed by a holdout comparison against naive.
max_turns: 25
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

weekly_demand.csv in the current folder has one year of weekly demand for six items. We currently forecast everything with a 4-week moving average. Which forecasting method should we use for which items?
