# Inventory parameter review: <scope>

*Data tier: <T0–T3> · Basis: <n SKUs, period from–to, demand unit> · Service metric: <CSL / fill rate (unit/line)>*

## Bottom line
*2–4 sentences: what changes, which items are most affected, net inventory impact, expected service effect.*

## Segmentation
*ABC/XYZ matrix (counts and value share) and demand patterns. One sentence on what stands out.*

## Recommended parameters
| SKU | Segment | Target | d̄ / period | σ | L (+R) | SS | ROP / S | Q | Current SS | Δ SS | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | | | |

*Formula: SS = k · √(P·σ_d² + d̄²·σ_L²) [SPT-2017]. Offer the full table as CSV if longer than ~15 rows.*

## Impact
| | Current | Recommended | Δ |
|---|---|---|---|
| Safety stock value | | | |
| Target average stock value (SS + Q/2) | | | |
| Expected service (aggregate) | | | |

## Stock health (if on-hand provided)
*Counts and value: below SS / ok / excess. Top 5 excess and top 5 shortfall items.*

## Assumptions
- [Assumption] *e.g. lead time CV 0.2 where no receipts were available*
- [Assumption] *…*

## Next steps
1. *Fix master data first (lead times, MOQs).*
2. *Load new parameters for segment …; monitor for … weeks.*
3. *Set the review cadence: …*

## What would change this answer
*1–3 inputs with the largest influence on the result.*
