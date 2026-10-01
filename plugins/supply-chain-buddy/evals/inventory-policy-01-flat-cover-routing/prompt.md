---
description: Routing + first response. A flat weeks-of-cover rule causing stock-outs and excess at the same time.
tags: [inventory-policy, routing]
expected_outcome: Skill fires; the answer rejects the flat rule, proposes segmentation and statistical safety stock, and asks for the specific data needed.
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill]
---

We're a spare parts distributor with roughly 1,200 SKUs in one central warehouse. Our ERP sets safety stock to 3 weeks of average demand for every item. We keep running out of some of our best sellers, but the warehouse is also full of stuff that barely moves. How should we set this up properly?
