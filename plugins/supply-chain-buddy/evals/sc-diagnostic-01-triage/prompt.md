---
description: Triage without data. Fill rate down and inventory up at the same time.
tags: [sc-diagnostic, routing, advisory]
expected_outcome: Separates the two symptoms, builds hypotheses across supply/demand/parameters/process, requests specific data, warns against a blanket safety stock increase.
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

Over the past year our fill rate dropped from about 96% to 88%, while our average inventory value went up roughly 15%. I need to explain this to management next week. Where do I start?
