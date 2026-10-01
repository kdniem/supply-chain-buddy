# Routing: detailed rules and patterns

## §1 Routing rules
1. **Unknown cause → diagnose first.** If the user describes a symptom (a KPI moved, "something is off") and the cause is unknown, start with `sc-diagnostic`. It locates the cause and hands off.
2. **Known area, scoped question → go direct.** "Calculate safety stock for these items" goes to `inventory-policy`. "Is MAPE the right KPI?" goes to `demand-planning-review`.
3. **Several areas named by the user → diagnose, then specialists.** "Our forecast is too high, stock is too high and deliveries are late" goes to `sc-diagnostic` (locate and connect), then `demand-planning-review` (bias, FVA), then `inventory-policy` (parameters, excess). The order follows causality: demand signal, then parameters, then stock.
4. **Design or concept question** (a new process, policy or strategy): use the thinking-partner mode. Bring in specialists for the parts they cover, e.g. `inventory-policy` for the segmentation concept and `demand-planning-review` for the forecasting process inside an S&OP design.
5. **Not covered** (planned skills, logistics, network design, regulation): say so in one line and answer as a general advisor with cited methods.
6. **Re-route on evidence.** If a specialist's findings point elsewhere, for example the diagnosis shows a supplier lead time problem, follow the evidence and update the case card.

## §2 Sequencing patterns
| Pattern | Sequence | Why |
|---|---|---|
| Service ↓ (cause unknown) | sc-diagnostic → inventory-policy (lead times, parameters) and/or demand-planning-review (under-bias) | Locate before fixing |
| Inventory ↑ (cause unknown) | sc-diagnostic → demand-planning-review (over-bias, overrides) → inventory-policy (parameters, excess) | Demand signal drives the parameters |
| Service ↓ and inventory ↑ | sc-diagnostic (two bridges) → the specialists per located cause | Two symptoms often have different causes |
| "Set up our inventory policy" | inventory-policy (policy design) ← demand-planning-review (σ of the forecast error) if forecasts exist | The uncertainty input comes from the forecast |
| "Improve our forecasting" | demand-planning-review → inventory-policy (translate the error into safety stock) | Show the business impact |
| "Health check / where do we stand" | sc-diagnostic (health check mode) → priorities → specialists for the top priorities | Breadth first, then depth |

## §3 Consolidated data request (example)
For "service ↓ and inventory ↑" with no data yet:
```
To find the causes I need, ideally as CSV exports (minimum first):
1. Weekly (or monthly) demand and shipped quantity per SKU, last 12 months
2. Item master: SKU, category, supplier, unit cost
3. Weekly or monthly on-hand stock per SKU
4. Purchase order receipts: order date, promised date, receipt date, supplier
5. If available: forecast snapshots (statistical and final) and current ERP parameters (lead time, safety stock, order quantity)
Anonymise customer and supplier names if you like; codes are enough.
```

## §4 Examples
- *"Hey Buddy, what's the difference between fill rate and service level?"* Direct answer (glossary), no routing.
- *"We keep running out of our top sellers."* This is a symptom with a likely parameter cause. Do a brief diagnostic framing (is it lead time, demand or parameters?), then `inventory-policy` once data confirms it.
- *"Our forecast is always too high and the warehouse is full, but we still miss deliveries. Where do we start?"* Multi-step: case card, `sc-diagnostic` → `demand-planning-review` → `inventory-policy`, then an integrated brief.
- *"Should we dual-source our castings?"* Not covered yet (`sourcing-strategy` is planned). Say so in one line, then frame the decision (risk vs. TCO vs. volume leverage), give a Kraljic-based view `[KRA-1983]`, TCO elements `[ELL-1995]` and risk considerations `[CS-2004]`, and request the data needed.
