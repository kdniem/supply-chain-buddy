---
description: Multi-topic symptom without data. Buddy should plan a route (diagnose first), consolidate the data request, and not dump three separate reports.
tags: [sc-buddy, routing]
expected_outcome: Frames the decision, proposes a sequence starting with diagnosis, gives initial hypotheses, one consolidated data request.
max_turns: 12
timeout_seconds: 400
allowed_tools: [Read, Glob, Grep, Skill]
---

Hey Supply Chain Buddy, our forecast always seems too high, the warehouse is full, and yet we still miss customer deliveries every week. I don't know where to start.
