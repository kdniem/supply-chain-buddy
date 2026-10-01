# Methods: supply chain diagnostic

## §1 KPI trees (starting points; adapt to the case)

### Service down (fill rate, OTIF, backorders)
```
Service ↓
├─ Product not available (stock-out)
│  ├─ Supply side: lead time ↑ or more variable · supplier OTD ↓ · capacity/allocation · MOQ/batching delays
│  ├─ Demand side: volume ↑ · volatility ↑ · mix shift toward weaker items · new customers/products
│  ├─ Planning: forecast under-bias · stale parameters (lead time, SS, ROP) · flat rules ignoring variability
│  └─ Inventory placement: stock at wrong location · allocation rules
├─ Available but not shipped on time/in full
│  ├─ Order management: credit holds, order entry errors, cut-off times
│  ├─ Warehouse execution: picking capacity, errors, backlog
│  └─ Transport: carrier capacity, delays
└─ Measurement: KPI definition changed · data errors · denominator effects (more lines/orders)
```

### Inventory up
```
Inventory ↑ (value)
├─ Cycle stock: order quantities ↑ · MOQ ↑ · forward/volume buys
├─ Safety stock: targets ↑ · parameters ↑ (incl. manual overrides, project buffers)
├─ Excess/slow/obsolete: demand ↓ without re-planning · forecast over-bias · lifecycle end · cancelled projects
├─ Pipeline/in-transit: lead times ↑ (on-order up, on-hand may fall)
├─ Price/mix: higher unit costs · mix shift to expensive items
└─ Measurement: valuation changes · consignment/ownership changes
```

### Cost up (cost-to-serve)
Transport (expedites, premium freight, lower fill per shipment) · warehousing (handling, space) · inventory carrying cost · lost sales and penalties · purchase price variance.

### Two symptoms at once
**Service ↓ and inventory ↑** is the classic misallocation pattern. Run both trees and both bridges. The drivers are usually different: supply-side issues on some items, demand or policy issues on others. The fix is rebalancing and repairing parameters, not adding stock.

## §2 Hypothesis-driven approach
1. **Issue tree (MECE):** split the question into non-overlapping, collectively exhaustive branches. Use the KPI trees above.
2. **Prioritise:** score each hypothesis by likelihood (from what the user said), impact (share of the KPI it could explain) and ease of testing.
3. **Test design:** for each hypothesis, write down the data, the cut and the confirming result. Example: "If SUP-03 lead time drives the drop, then SUP-03's fill rate falls (rate effect) and its actual lead times rise after the change point."
4. **Answer first:** synthesise as ranked findings with evidence, not as an analysis diary `[MIN-1987]`.

## §3 KPI bridges (shift-share)
For a ratio KPI R = ΣN/ΣD across groups g:
- weights w_g = D_g/ΣD, group rates r_g = N_g/D_g
- **Rate effect** = (r2 − r1)·w̄: the group itself got better or worse.
- **Mix effect** = (w2 − w1)·(r̄_g − R̄): volume moved toward groups with below- or above-average KPI.
- Σ(rate + mix) = R2 − R1 (exact).

**Interpretation:** a large negative rate effect concentrated in one group points to a local cause (that supplier or category). A large mix effect means the KPI fell because the business mix changed, not because performance did. Weight by value where business impact matters.

**Window choice:** use equal lengths, exclude known one-offs (holidays, stock-takes) and compare like seasons where seasonality matters. Test the sensitivity of the conclusion to the window.

## §4 Root-cause tools
- **5 Whys** `[OHN-1988]`: ask "why" repeatedly until you reach a cause the organisation controls (process, policy, rule, incentive). Stop at causes, not at people.
  - Example: fill rate ↓ → SUP-03 items out of stock → reorders arrive too late → actual lead time 34 days vs. 14 in the ERP → nobody reviews lead time master data → **no lead time monitoring process or owner**.
- **Fishbone / cause-and-effect** `[ISH-1986]`: categories for supply chains are Demand, Supply, Planning, Process/Execution, Data/Systems, Organisation. Use it in workshops to gather and structure causes, then test them with data.
- **Change-point matching:** align the KPI series with a dated change log. Coinciding changes are candidates, not proof.

## §5 Synthesis rules
- Rank causes by quantified contribution to the symptom (from the bridges). Unquantified causes go in a separate list with a confidence level.
- For each cause, give the proximate cause, the systemic cause, a quick fix and a structural fix, with an owner role.
- Include "what we ruled out" with the evidence.
