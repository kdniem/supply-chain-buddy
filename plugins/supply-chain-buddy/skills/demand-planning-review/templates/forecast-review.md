# Forecast review: <scope>

*Data tier: <T0–T3> · Basis: <n SKUs, periods from–to, level (e.g. SKU-week), lag> · Metric: wMAPE (value-weighted / units), bias = Σ(F−A)/ΣA*

## Bottom line
*2–4 sentences: how good the forecast is vs. naive, where the bias sits, which step or group destroys value, and the top action.*

## Scorecard
| Step | wMAPE | Bias | FVA vs. previous step |
|---|---|---|---|
| Naive (lag *h*) | | | – |
| Statistical | | | |
| Final / consensus | | | |

## Where the error comes from
| Group / segment | wMAPE | Bias | FVA of the override step | Comment |
|---|---|---|---|---|
| | | | | |

*Persistent bias list (|bias| > 10%, |TS| > 4) with value impact.*

## Method fit (if assessed)
*Demand patterns and best method by pattern from the backtest; recommendation.*

## Recommendations
1. *Process (e.g. re-baseline after a structural change, override governance with reason codes and FVA tracking)*
2. *Method (e.g. Croston-SBA for intermittent items, ETS for seasonal items)*
3. *Measurement (lag snapshots, value weighting, monthly FVA report)*

## Assumptions
- [Assumption] *…*

## What would change this answer
*1–3 inputs with the largest influence.*
