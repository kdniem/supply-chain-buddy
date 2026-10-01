# Supply chain health check (SCOR-based)

A structured assessment for when there is no single symptom ("where do we stand, where should we start?"). The structure follows the process areas of the SCOR Digital Standard `[SCOR-DS]`: Plan, Order, Source, Transform, Fulfill, Return, Orchestrate. For an analysis in depth, use the official SCOR DS metric and practice definitions.

## How to run it
1. **Scope:** business unit, sites, product groups. Who answers: one person, or a cross-functional workshop (better)?
2. **Questionnaire:** go area by area. Ask at most about 5 questions per turn and accept short answers. Score maturity 1–5 using the anchors below, and record the evidence behind each score.
3. **KPI snapshot:** request the KPIs listed per area (last 12 months, with definitions). Missing KPIs are a finding in themselves.
4. **Heatmap and priorities:** show the scores per area, then pick the 3 priorities by impact on strategy and KPIs × feasibility. Use strategic fit (efficient vs. responsive, `[FIS-1997]`) to weigh the areas.
5. **Deliver** a one-page summary: heatmap, top 3 priorities, quick wins, and the next step per priority (often a handoff to a specialist skill).

## Maturity anchors (generic)
| Level | Description |
|---|---|
| 1 Ad hoc | Person-dependent, reactive, spreadsheets without standards, KPIs missing or undefined |
| 2 Defined | Documented processes and owners exist; basic KPIs measured; limited integration |
| 3 Integrated | Cross-functional process (e.g. monthly S&OP) works; parameters reviewed on a cadence; consistent data |
| 4 Optimised | Decisions use scenarios and segmentation; exception-based management; continuous improvement |
| 5 Orchestrated | End-to-end and partner collaboration; real-time visibility; measured value added of each planning step |

## Questions and KPIs per area
### Plan
- How is demand forecast, at what level and lag, and how is accuracy and bias measured? Is forecast value added tracked?
- Is there a monthly S&OP/IBP cycle with executive decisions? Are supply constraints and financials integrated?
- How are inventory targets set: segmented and statistical, or flat rules? How often are they reviewed?
- **KPIs:** forecast accuracy and bias at the decision lag, inventory turns / days of inventory, plan adherence.

### Order
- How are orders captured and promised? Is available-to-promise used? Are customer requested and confirmed dates both recorded?
- **KPIs:** order fulfillment cycle time, order entry accuracy, share of orders confirmed on the requested date.

### Source
- Is there a category strategy (e.g. a portfolio matrix) and supplier segmentation? Are lead times and supplier OTD measured against confirmed dates?
- Are master data (lead times, MOQs, prices) reviewed on a cadence? Is supplier risk assessed?
- **KPIs:** supplier OTD, lead time and its variability, spend under management, PPV and TCO.

### Transform (make / assemble / pack)
- How is production scheduled? How stable is the plan (frozen zones)? How is capacity planned against demand?
- **KPIs:** schedule adherence, capacity utilisation, OEE (if relevant), yield.

### Fulfill (warehouse, transport)
- How are stock and orders managed in the warehouse? Are pick accuracy and on-time dispatch measured? How are carriers managed?
- **KPIs:** fill rate, OTIF, perfect order, cost per order or line, transport cost per unit.

### Return
- Is there a defined returns process (customer returns, supplier returns, repairs), and are returns analysed for root causes?
- **KPIs:** return rate, return cycle time, recovery value.

### Orchestrate (enable: strategy, data, organisation, risk, sustainability)
- Is there a written supply chain strategy aligned with the business strategy? Clear decision rights?
- Data quality and system landscape: single source of truth, master data governance?
- Risk management and resilience (multi-sourcing, scenario planning) `[CP-2004]` `[CS-2004]`? Sustainability and regulatory readiness?
- **KPIs:** total supply chain cost, cash-to-cash cycle time, data quality indicators.

## Output skeleton
| Area | Score (1–5) | Key evidence | Biggest gap | Priority |
|---|---|---|---|---|
| Plan | | | | |
| … | | | | |

Mark scores as structured judgement based on the information given, not as a benchmark.
