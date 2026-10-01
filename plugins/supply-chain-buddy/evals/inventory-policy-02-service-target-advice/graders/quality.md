---
type: llm
---

PASS only if ALL of the following hold:
1. The response identifies that the reported metric is a (line) fill rate and distinguishes it from cycle service level (probability of no stock-out per replenishment cycle), noting that the two lead to different safety stocks.
2. It explains that safety stock grows disproportionately (non-linearly) as the target approaches 100%, ideally with a concrete illustration (e.g. z ≈ 1.64 at 95% vs ≈ 2.33 at 99% cycle service level, roughly +40% safety stock).
3. It recommends differentiated targets by segment (e.g. ABC/XYZ, criticality, margin) instead of one uniform 99%.
4. It gives the user something actionable to bring to the CFO (e.g. a trade-off curve of inventory value vs. service, or a proposal for segment targets).

FAIL if it simply endorses 99% for all items, or rejects it without explaining the trade-off.
FAIL if it states specific industry benchmark percentages as facts without labelling them as rules of thumb or citing a source.
