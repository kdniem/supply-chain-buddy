# Pitfalls: inventory policy

Common mistakes practitioners make in this domain, and that AI assistants make too. For each pitfall: what it looks like · why it is wrong · how to detect it · what to do instead.

## 1. "Service level" without a definition
- **Looks like:** "We target 95% service level" with no metric specified.
- **Why it is wrong:** 95% CSL and a 95% fill rate imply very different safety stocks. Line fill and unit fill differ too.
- **Detect:** Ask how the KPI is calculated in their reporting.
- **Do instead:** Name the metric explicitly. If the business reports fill rate but parameters are set with z values (CSL), show both: the CSL target and the implied fill rate.

## 2. One rule for all SKUs
- **Looks like:** "Safety stock = 2 weeks of demand for everything" or "99% for all items".
- **Why it is wrong:** Weeks of cover ignore variability and lead time. Stable items get too much, volatile items too little. Uniformly high targets are expensive where they add little value.
- **Detect:** SS divided by mean demand is constant across SKUs.
- **Do instead:** Segment with ABC/XYZ and size safety stock statistically per segment target.

## 3. Shipments used as demand
- **Looks like:** Demand history taken from deliveries or invoices.
- **Why it is wrong:** During stock-outs, shipments understate true demand (censored demand). Safety stock is then sized too low, and the stock-outs keep themselves going.
- **Detect:** Zero or low periods coincide with zero on-hand. Ask the source of the history.
- **Do instead:** Use order intake, including lost and backordered demand. Otherwise flag the affected periods and treat the results as a lower bound.

## 4. Lead time variability ignored
- **Looks like:** σ_L = 0 by default, or the system lead time is taken as truth.
- **Why it is wrong:** The d̄²·σ_L² term often dominates (see the worked example in methods §4). System lead times are often outdated.
- **Detect:** Compare promised and actual receipt dates by supplier. Check whether recent orders arrive later than older ones.
- **Do instead:** Compute the mean and σ of actual lead times from receipts. Update master data first; it is the cheapest service fix.

## 5. Mixed time units
- **Looks like:** Weekly demand std combined with a lead time in days or months.
- **Why it is wrong:** It inflates or deflates SS by √(conversion factor) or worse.
- **Detect:** Check the units of every input explicitly.
- **Do instead:** Convert lead time to demand periods (the scripts have `--period-days`).

## 6. Demand std where forecast error belongs, or the reverse
- **Looks like:** Using the std of demand around its mean for a seasonal item that is replenished from a forecast.
- **Why it is wrong:** Seasonality is predictable, so the demand std overstates uncertainty. Conversely, a bad forecast can make the real uncertainty larger than the demand std.
- **Detect:** Seasonal or trending pattern, and whether a forecast is used.
- **Do instead:** Use the RMSE of the forecast at the replenishment lag when replenishment follows a forecast.

## 7. Normal approximation for lumpy items
- **Looks like:** Applying the z × σ formula to items with demand in 3 out of 10 weeks.
- **Why it is wrong:** The distribution is far from normal. The results can be badly over- or under-sized.
- **Detect:** ADI ≥ 1.32 (abc_xyz.py marks them intermittent or lumpy).
- **Do instead:** Use Croston/TSB for the forecast, min-max with an empirical check, or a decision to hold no stock (make or buy to order).

## 8. Forgetting the review period
- **Looks like:** Periodic ordering (e.g. weekly), but safety stock sized for the lead time only.
- **Why it is wrong:** Protection must cover L + R.
- **Detect:** Ask how often orders are placed.
- **Do instead:** Use P = L + R.

## 9. Stale parameters
- **Looks like:** Parameters set once and never reviewed. Demand or lead times have changed since.
- **Why it is wrong:** Old safety stocks protect against yesterday's uncertainty. Typical symptom: excess on declining items and stock-outs on growing ones or on items with longer lead times.
- **Detect:** Compare parameter base values (mean demand, lead time) against the last 13 weeks.
- **Do instead:** Recalculate on a cadence (e.g. monthly for A items, quarterly for the rest) and alert when lead time or demand drifts.

## 10. MOQ and lot size effects overlooked
- **Looks like:** A debate about safety stock while order quantities are 8 weeks of demand.
- **Why it is wrong:** Cycle stock (Q/2) can dwarf safety stock.
- **Detect:** Compare Q/2 with SS per item.
- **Do instead:** Show cycle stock separately. Evaluate MOQ trade-offs with TCO and hand off to sourcing-strategy.

## 11. "More inventory" as the answer to a misallocation problem
- **Looks like:** Total stock went up, service went down, and the proposed fix is to raise safety stock everywhere.
- **Why it is wrong:** The stock sits on the wrong items. Raising it everywhere increases cost without fixing the items that are short.
- **Detect:** Run the health check. Items with excess and items below SS exist side by side.
- **Do instead:** Rebalance parameters by segment and fix the drivers (lead times, demand shifts, MOQs, speculative buys).

## 12. Single-location formulas for networks
- **Looks like:** Applying the same formula independently at a central DC and regional warehouses.
- **Why it is wrong:** It double-buffers and ignores risk pooling.
- **Detect:** More than one stocking echelon.
- **Do instead:** Flag the issue and recommend a multi-echelon approach `[AXS-2015]`. Treat single-location results as an upper bound.
