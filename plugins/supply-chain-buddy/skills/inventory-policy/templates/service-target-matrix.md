# Inventory policy concept: <scope>

*Purpose: which items we stock, to what service level, with which replenishment policy, and how we keep parameters current.*

## 1. Principles
- *e.g. Service targets are differentiated by segment; no flat weeks-of-cover rules.*
- *e.g. Safety stock is sized statistically for lead time + review period.*
- *e.g. Parameters are reviewed on a fixed cadence and on trigger events.*

## 2. Segmentation logic
| Dimension | Measure | Cut-offs | Source |
|---|---|---|---|
| Importance (ABC) | Consumption value, last 12 months | A < 80%, B < 95% cumulative | [SPT-2017] |
| Predictability (XYZ) | CV of weekly demand (or forecast error) | X ≤ 0.5, Y ≤ 1.0 | [SPT-2017] |
| Demand pattern | ADI / CV² | 1.32 / 0.49 | [SB-2005] |
| Overrides | Criticality, lifecycle, contractual SLAs | *define* | |

## 3. Service target and policy matrix
| | X | Y | Z |
|---|---|---|---|
| **A** | *target · policy* | | |
| **B** | | | |
| **C** | | | *e.g. make-to-order / min-max* |

*Targets are cycle service levels unless stated otherwise. Show the implied aggregate fill rate and the inventory value per segment.*

## 4. Parameter calculation rules
- Uncertainty measure: *forecast error at lag L, else demand std*
- Lead time: *actual receipts, last 6–12 months, mean and σ*
- Lot sizes: *EOQ, rounded to MOQ and order multiples*
- Intermittent and lumpy items: *special rule*

## 5. Governance
| Activity | Frequency | Owner (role) | Trigger events |
|---|---|---|---|
| Recalculate A-item parameters | *monthly* | *Inventory planner* | *lead time drift > 20%, demand shift > 25%* |
| Re-segment assortment | *quarterly* | | |
| Review excess and obsolescence | *monthly* | | |

## 6. Expected impact and risks
*Inventory value, service, change effort, transition plan (do not cut excess stock faster than it is consumed).*
