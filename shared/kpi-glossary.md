# KPI glossary

Canonical definitions used by all skills. When a user's term is ambiguous ("service level", "forecast accuracy"), map it to one of these definitions and say which one you use. Formulas use a period *t* and a set of items *i*. SCOR performance attributes follow the SCOR Digital Standard `[SCOR-DS]`: Reliability, Responsiveness, Agility, Cost, Profit, Assets, Environmental, Social.

## Customer service
| KPI | Definition / formula | Notes | SCOR attribute |
|---|---|---|---|
| **Cycle service level (CSL, α service level)** | Probability of no stock-out during a replenishment cycle | Drives the safety factor *z* in classic safety stock formulas `[SPT-2017]`. Not the same as fill rate | Reliability |
| **Fill rate (β service level)** | Share of demand quantity delivered immediately from stock = units shipped from stock ÷ units demanded | Variants: *unit*, *line* (order lines filled complete ÷ order lines), *order* (orders filled complete ÷ orders). Always state the variant. A given CSL usually yields a *higher* unit fill rate | Reliability |
| **OTIF (on time in full)** | Orders (or lines) delivered on the agreed date and in full quantity ÷ orders (or lines) | Definitions of "on time" vary (requested vs. confirmed date, tolerance window). Clarify before comparing | Reliability |
| **Perfect order fulfillment** | Orders delivered complete, on time, with correct documentation and without damage ÷ total orders | Strictest service KPI | Reliability |
| **Backorder rate** | Demand not fulfilled at request time and carried over ÷ total demand | | Reliability |
| **Order fulfillment cycle time** | Average time from order receipt to customer delivery | | Responsiveness |

## Inventory
| KPI | Definition / formula | Notes | SCOR attribute |
|---|---|---|---|
| **Inventory turns** | Cost of goods sold (period, annualised) ÷ average inventory value at cost | Use cost, not sales value, on both sides | Assets |
| **Days of inventory (DOI/DIO), days of supply** | Average inventory value ÷ COGS per day; or per SKU: on-hand ÷ average daily (forecast) demand | State whether backward- or forward-looking | Assets |
| **Safety stock** | Stock held to buffer demand and supply uncertainty during the risk period (lead time + review period) | See inventory-policy skill | Assets |
| **Cycle stock** | Stock resulting from batch ordering ≈ order quantity ÷ 2 on average | | Assets |
| **Excess stock** | Stock above target maximum (e.g. above safety stock + order quantity), valued at cost | Define the threshold explicitly | Assets |
| **Obsolete / slow-moving stock** | Stock with no demand in *X* months (state *X*) or past shelf life | | Assets |
| **Cash-to-cash cycle time** | DIO + days sales outstanding − days payables outstanding | | Assets |

## Forecasting
Let *A* = actual demand and *F* = forecast at a defined **lag** (e.g. the forecast made 1 month before the period). Always state the lag and the aggregation level (SKU-location-week, family-month, …).

| KPI | Formula | Notes |
|---|---|---|
| **Forecast error** | *e = F − A* (Buddy convention: positive = over-forecast) | Sign conventions differ. State the convention |
| **Bias (mean error)** | Σ(F − A) ÷ Σ A, in % | Persistent bias is the most actionable forecasting issue |
| **MAE / MAD** | mean(\|F − A\|) | Scale-dependent |
| **MAPE** | mean(\|F − A\| ÷ A) | Undefined for A = 0, explodes at low volumes, penalises over- and under-forecasts asymmetrically. Avoid for intermittent items `[HK-2006]` |
| **wMAPE (MAD/Mean)** | Σ\|F − A\| ÷ Σ A | Preferred aggregate error metric in practice `[KS-2007]`. *Forecast accuracy* = 1 − wMAPE (floored at 0) |
| **MASE** | MAE ÷ in-sample MAE of the naive (or seasonal naive) method | Scale-free and works with zeros. Below 1 means better than naive `[HK-2006]` |
| **Tracking signal** | Cumulative error ÷ MAD | Flags bias. \|TS\| > 4 is a common warning threshold (rule of thumb) |
| **Forecast value added (FVA)** | Error of the naive or statistical forecast minus error of the step being evaluated (e.g. after consensus override) | Positive = the step improves the forecast `[GIL-2010]` |

## Demand characterisation
| KPI | Formula | Notes |
|---|---|---|
| **Coefficient of variation (CV)** | σ(demand) ÷ μ(demand) per period | Basis for XYZ classification. Thresholds are a design choice; state them |
| **ADI (average demand interval)** | Number of periods ÷ number of periods with demand > 0 | With CV², classifies smooth / erratic / intermittent / lumpy demand `[SB-2005]` |
| **CV²** | (σ ÷ μ)² of **non-zero** demand sizes | Cut-offs ADI = 1.32, CV² = 0.49 `[SB-2005]` |

## Procurement and supply
| KPI | Definition | Notes |
|---|---|---|
| **Supplier on-time delivery (OTD)** | Receipts on or before the confirmed date (± tolerance) ÷ receipts | Specify the reference date |
| **Supplier lead time / lead time variability** | Mean and standard deviation of (receipt date − order date) | Feeds safety stock |
| **Purchase price variance (PPV)** | (Actual price − standard price) × quantity | Can conflict with TCO |
| **Total cost of ownership (TCO)** | Acquisition + ownership + post-ownership costs over the life cycle `[ELL-1995]` | |
| **Spend under management** | Spend covered by managed contracts or strategies ÷ total addressable spend | |

## Planning process
| KPI | Definition | Notes |
|---|---|---|
| **Schedule adherence** | Planned production/orders executed as planned in the period ÷ planned | |
| **Plan stability / nervousness** | Share of plan changes within the frozen horizon | |
| **Capacity utilisation** | Used capacity ÷ available capacity | Define available: theoretical or planned |

## Terminology map (common ambiguous phrases)
| User says | Ask or assume |
|---|---|
| "service level" | Cycle service level or fill rate? Line or unit? |
| "forecast accuracy" | Which formula (1 − wMAPE?), which lag, which level? |
| "lead time" | Supplier lead time, total replenishment lead time (incl. internal processing and transport), or customer lead time? |
| "stock" / "inventory" | Units or value? On-hand only, or incl. in-transit? |
| "Lieferbereitschaftsgrad" (DE) | Usually fill rate (often line level) |
