# Methods: demand planning review

## §1 Measuring forecast quality

### Fix the measurement frame first
| Choice | Recommendation |
|---|---|
| **Lag** | The lag of the decision the forecast feeds: replenishment lead time, production frozen zone, budget. Store forecast snapshots; never measure the latest forecast against actuals |
| **Level** | The level where the decision is taken (e.g. SKU-location-week for replenishment, family-month for capacity). Errors shrink with aggregation, so compare like with like |
| **Weighting** | Value (unit cost or price) for business relevance; units only within comparable items |
| **Window** | ≥ 13 periods; separate windows before and after known structural changes |

### Metrics (formulas in `_shared/kpi-glossary.md`)
- **Bias %** = Σ(F − A) ÷ ΣA. This is the first number to look at. Systematic over-forecasting builds excess stock, and systematic under-forecasting creates shortages.
- **wMAPE (MAD/Mean)** = Σ|F − A| ÷ ΣA. It is robust to zeros at the aggregate and value-weightable. Accuracy = 1 − wMAPE. `[KS-2007]`
- **MAPE:** mean of |F − A| ÷ A. It is undefined for A = 0, explodes for small A and is asymmetric. Report it only if the business insists, excluding zeros, and say so. `[HK-2006]`
- **MASE** = MAE ÷ in-sample MAE of the naive method. It is scale-free and handles zeros. Below 1 means better than naive. `[HK-2006]`
- **Tracking signal** = Σe ÷ MAD. If |TS| > 4 (rule of thumb), the bias is persistent rather than random.

### Forecast value added (FVA) `[GIL-2010]`
FVA = error of the previous step − error of this step, for example:
naive → statistical → sales override → management adjustment → final.

- Compute FVA per step with the same metric (wMAPE), on the same periods and at the same lag.
- **Negative FVA** means the step makes the forecast worse. Typical causes are optimism bias, budget lock-in and sandbagging.
- Report FVA by group (category, region, planner), because aggregates hide offsetting effects.
- **Worked example:**

| Step | wMAPE |
|---|---|
| Naive (lag 4) | 51.6% |
| Statistical | 39.3% |
| Final (consensus) | 45.3% |

The statistical model adds ≈ +12 pts, the consensus step destroys ≈ 6 pts, and the net FVA vs. naive is ≈ +6 pts (rounded). The fix is in the override process, not in the model.

## §2 Method selection by demand pattern `[SB-2005]` `[HA-2021]`
| Pattern (ADI / CV²) | Start with | Consider | Avoid |
|---|---|---|---|
| Smooth (< 1.32 / < 0.49) | SES or moving average; ETS if trend or seasonality | ARIMA, regression with drivers | Over-complex models without FVA evidence |
| Erratic (< 1.32 / ≥ 0.49) | SES with low α, ETS | Causal drivers (promotions, prices) | Naive |
| Intermittent (≥ 1.32 / < 0.49) | Croston-SBA `[CRO-1972]` `[SBA-2005]` | TSB if items may become obsolete `[TSB-2011]` | MAPE as a metric; SES (biased after zeros) |
| Lumpy (≥ 1.32 / ≥ 0.49) | Croston-SBA or TSB, aggregate in time or level | Not forecasting at SKU level: make-to-order, or min-max with an empirical buffer | Precise normal-based safety stock |

Practical rules:
- Every method must beat naive (FVA > 0 or MASE < 1) on a holdout before it is adopted.
- Choose parameters on the training window only, and evaluate on the holdout (rolling origin).
- For intermittent items, MAE-type metrics favour forecasts near zero, so a naive method can "win" on a short holdout with few demand events. Also check bias and the cumulative error over the lead time, which matters for stock, before adopting such a winner.
- Seasonality needs at least 2 full cycles of history. Without that, use seasonal indices from the product family.
- New products: analogue items or family profiles plus judgement; measure FVA once actuals exist.

## §3 Recursions used in `method_backtest.py`
- **SES** `[GAR-1985]`: ℓ_t = α·y_t + (1 − α)·ℓ_(t−1); forecast = ℓ_t
- **Croston-SBA:** on demand occurrences, update size z and interval p: z ← α·y + (1 − α)·z and p ← α·q + (1 − α)·p; forecast = (1 − α/2)·z/p
- **TSB:** every period, probability π ← π + β·(1[y>0] − π); on demand, z ← z + α·(y − z); forecast = π·z

## §4 Targets and segmentation of effort
- Set targets as **improvement vs. naive and vs. last year at the same level and lag**, not as absolute "industry" numbers.
- Forecastability segmentation: value (ABC) × forecastability (CV of the forecast error, or MASE of the naive).
  - High value / forecastable: automate, review exceptions.
  - High value / hard to forecast: collaborate with customers, buffer, shorten lead times.
  - Low value: keep it simple and automated.
- **Bullwhip** `[LPW-1997]`: order batching, price promotions, shortage gaming and forecast updating at each stage amplify variability upstream. Use POS or sell-out data where available.

## §5 Bias diagnostics checklist
| Pattern | Likely cause | Check |
|---|---|---|
| Over-forecast after a demand drop, persisting for months | Budget lock-in; plan not re-baselined | Final vs. statistical forecast after the change point |
| Over-forecast on growth or project items | Optimism; unconfirmed deals counted as demand | Override log; share of uplift without confirmed orders |
| Under-forecast on growing items | Model too slow (low α), censored demand | Stock-out periods; α choice |
| Bias alternating by period | Timing errors (shipment slips) | Compare at an aggregated time level |
