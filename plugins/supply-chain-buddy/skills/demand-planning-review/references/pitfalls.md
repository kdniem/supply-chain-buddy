# Pitfalls: demand planning review

## 1. Accuracy without lag, level and formula
- **Looks like:** "Our forecast accuracy is 82%."
- **Why it is wrong:** The figure can be computed at many levels and lags with different formulas, and the results differ by tens of points.
- **Detect:** Ask how it is computed. Look for monthly-family figures used to judge SKU-week decisions.
- **Do instead:** Fix lag, level, formula and weighting. Re-measure at the decision level.

## 2. MAPE on low-volume or intermittent items
- **Looks like:** MAPE of 300% dominated by a few tiny items, or items with zero actuals silently dropped.
- **Why it is wrong:** MAPE explodes as A → 0 and is undefined at 0.
- **Detect:** Many low or zero actuals. The averaged MAPE is far above wMAPE.
- **Do instead:** Use wMAPE for aggregates and MASE for item comparisons.

## 3. Ignoring bias because accuracy "looks fine"
- **Looks like:** wMAPE of 30% reported, with no bias metric.
- **Why it is wrong:** A 30% error with +25% bias is a systematic overstock driver. The same error with ~0% bias is noise.
- **Detect:** Bias % and tracking signal per group.
- **Do instead:** Report bias next to accuracy, always.

## 4. No naive benchmark
- **Looks like:** An expensive forecasting tool evaluated only against targets.
- **Why it is wrong:** If naive is as good, the tool adds nothing.
- **Detect:** No naive or seasonal-naive comparison exists.
- **Do instead:** Measure FVA vs. naive and MASE.

## 5. Measuring the latest forecast instead of the snapshot at the decision lag
- **Looks like:** Accuracy computed from the forecast as it stands today for past periods.
- **Why it is wrong:** Short-term corrections make it look much better than what decisions were actually based on.
- **Detect:** No snapshot or lag information in the data.
- **Do instead:** Store and measure snapshots per lag.

## 6. Overrides assumed to help
- **Looks like:** Sales and management adjustments accepted without measurement.
- **Why it is wrong:** Overrides are often biased (optimism, budget lock-in) and add negative FVA.
- **Detect:** FVA per step is negative. Overridden items show higher bias.
- **Do instead:** Measure FVA per step and require reason codes. Allow overrides only above a materiality threshold and review their FVA monthly.

## 7. Shipments as "demand"
- **Looks like:** Accuracy and models built on deliveries.
- **Why it is wrong:** Stock-outs censor demand. Forecasts then learn the shortage and keep it going.
- **Detect:** Zero-stock periods coincide with low actuals.
- **Do instead:** Use order intake including lost sales, or flag censored periods.

## 8. Complex methods for simple patterns, or the reverse
- **Looks like:** ML for 3,000 lumpy spare parts, or SES for strongly seasonal items.
- **Why it is wrong:** Complexity without FVA adds cost and opacity. Wrong model families leave error unexplained.
- **Detect:** Check the demand pattern classification against the method in use.
- **Do instead:** Match method to pattern and require holdout evidence.

## 9. Accuracy targets copied from elsewhere
- **Looks like:** "Best in class is 85%, so our target is 85%."
- **Why it is wrong:** The number was measured at a different level, lag and volatility, so it is not comparable.
- **Detect:** The target has no stated definition.
- **Do instead:** Set targets relative to naive and to your own trend, at your own level and lag.

## 10. One structural break, many conclusions
- **Looks like:** Annual accuracy blended over a period with a major demand shift.
- **Why it is wrong:** The pre-break and post-break behaviour is averaged, which hides the current problem.
- **Detect:** Look for step changes in the actuals.
- **Do instead:** Evaluate windows before and after the break (`--from`/`--to`).
