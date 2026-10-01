# Pitfalls: supply chain diagnostic

## 1. Jumping to the solution
- **Looks like:** "Service is down, so we need more safety stock" or "we need a new planning system".
- **Why it is wrong:** It treats an unlocated symptom with a generic fix, often an expensive one.
- **Detect:** No KPI tree, no attribution of the change.
- **Do instead:** Locate the change first (bridges by supplier, category or segment), then test hypotheses.

## 2. Treating two symptoms as one
- **Looks like:** One story for "service down and inventory up".
- **Why it is wrong:** The two often have different drivers. A single explanation misses half of the problem.
- **Detect:** The inventory and service bridges point to different groups.
- **Do instead:** Diagnose each symptom separately, then look for shared systemic causes (e.g. no parameter review process).

## 3. Mix effects mistaken for performance changes
- **Looks like:** "Our fill rate fell, so operations got worse," when volume simply shifted toward hard-to-serve items.
- **Detect:** Mix effect is large in the bridge, and rate effects are small.
- **Do instead:** Report rate and mix separately and discuss the business mix change with commercial teams.

## 4. KPI definition drift
- **Looks like:** A sudden KPI step after a system migration or report change.
- **Detect:** Ask whether the definition, data source or scope changed, and check the denominator.
- **Do instead:** Re-baseline before diagnosing.

## 5. Correlation as cause
- **Looks like:** "The drop started when the new planner joined."
- **Why it is wrong:** Coinciding events are candidates, not proof.
- **Do instead:** Require a mechanism plus confirming evidence in the data (e.g. actual lead times rising for exactly the affected items).

## 6. Stopping at the proximate cause
- **Looks like:** "Supplier X was late," and the analysis ends there.
- **Why it is wrong:** It will happen again with the next supplier.
- **Do instead:** Ask why the organisation did not notice or adapt, for example missing lead time monitoring, no parameter review, or no supplier performance reviews.

## 7. Analysis without a decision
- **Looks like:** A 40-page deep dive with no recommendation.
- **Do instead:** Answer first, rank causes by impact, and assign actions to roles.

## 8. Averages hiding the problem
- **Looks like:** Company-level averages ("inventory turns are fine").
- **Detect:** The skew is large; a few SKUs or suppliers dominate.
- **Do instead:** Cut by segment and value. Use Pareto views.
