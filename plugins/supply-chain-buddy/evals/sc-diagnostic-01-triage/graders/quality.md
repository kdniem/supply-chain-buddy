---
type: llm
---

PASS only if ALL of the following hold:
1. The response points out that falling service and rising inventory at the same time suggests inventory sitting on the wrong items (misallocation) and/or different drivers for the two symptoms, rather than a simple lack of stock.
2. It offers structured hypotheses covering at least three of: supply side (lead times, supplier reliability, MOQs), demand side (volume/mix shifts, forecast bias), planning parameters/policy (stale or flat safety stock rules), execution, measurement/KPI definition.
3. It asks for or lists specific data to test the hypotheses (e.g. fill rate by SKU/supplier/category over time, inventory by category over time, actual supplier lead times, forecast vs actual).
4. It suggests a way to locate where the change comes from (e.g. breaking the KPI change down by supplier/category/segment, comparing periods).

FAIL if the main recommendation is to increase safety stock across the board.
