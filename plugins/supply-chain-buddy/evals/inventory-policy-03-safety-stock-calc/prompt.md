---
description: Analysis with inline data. Safety stock and reorder points at 95% CSL incl. lead time variability.
tags: [inventory-policy, analysis]
expected_outcome: Correct SS/ROP per SKU (P-100 SS≈108, ROP≈308; P-300 SS≈59, ROP≈139), lead time variability included, formula shown.
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

Can you calculate safety stock and reorder points for these four items? We use continuous review and want a 95% cycle service level. Demand figures are per week, lead times in weeks.

```
sku_id,mean_demand,std_demand,lead_time,lead_time_std,order_qty
P-100,100,30,2,0.5,400
P-200,50,10,1,0,200
P-300,20,15,4,1,60
P-400,5,6,3,0,20
```

Please also tell me which of the four I should worry about most and why.
