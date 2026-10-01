---
type: llm
---

PASS only if ALL of the following hold:
1. Proposes a structured approach that starts by locating/diagnosing the causes (e.g. where service fails and where stock sits) before prescribing fixes, and explains the order of the next steps (e.g. diagnosis → forecast bias → inventory parameters).
2. Offers initial hypotheses connecting the symptoms (e.g. over-forecast or stale parameters building excess on some items while others are short; misallocation; supply issues).
3. Gives ONE consolidated, concrete data request covering the needs (e.g. demand and shipments per SKU, inventory per SKU, forecasts vs actuals, lead times/receipts, item master).
4. Contains substantive content in this reply (not only questions).

FAIL if it recommends raising or cutting inventory across the board as the first step.
