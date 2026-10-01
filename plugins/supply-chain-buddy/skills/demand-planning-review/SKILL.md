---
name: demand-planning-review
description: >-
  Reviews and improves demand forecasting: measures forecast accuracy and bias correctly,
  evaluates forecast value added (FVA) of statistical models and consensus overrides,
  backtests and selects forecasting methods (incl. intermittent demand), and advises on
  demand planning process and targets. Use when users mention forecast accuracy, MAPE,
  wMAPE, bias, "our forecast is always too high", over-forecasting, FVA, sales overrides,
  consensus forecast, which forecasting method to use, Croston, intermittent demand,
  "Prognosegüte", "Absatzplanung". Do not use for safety stock sizing (inventory-policy)
  or cross-functional KPI root-cause diagnostics (sc-diagnostic).
license: MIT
metadata:
  version: 0.1.0
  domain: plan
  maturity: beta
---

# Demand planning review

Helps demand planners, S&OP managers and supply chain analysts find out **how good their forecast really is, where it goes wrong and what to change**. The skill measures accuracy and bias with defensible metrics and tests whether each step of the forecasting process adds value. It recommends methods per demand pattern and process changes. The user gets clear answers to "is our forecast good enough", "who or what makes it worse" and "what should we do differently".

## Operating contract
Follow `references/_shared/operating-principles.md` at all times. In addition:

1. **Define the metric before judging it.** Pin down the formula (wMAPE, MAPE, MASE), the **lag** (how far ahead the forecast was made), the **aggregation level** (SKU-week vs. family-month) and the weighting (units vs. value). "85% accuracy" means nothing without these.
2. **Bias first, accuracy second.** Persistent bias is the most actionable and most costly error: it drives excess or shortage systematically. Report it separately from the error magnitude.
3. **Always compare against a naive benchmark.** A forecast is only "good" relative to what a naive method achieves on the same data (FVA, MASE). Never judge an accuracy number in isolation or against external "industry benchmarks".
4. **Measure every process step.** If there is a statistical forecast and a final or consensus forecast, compute FVA for the override step. Overrides often make forecasts worse; show it with data, without blame.
5. **Match the method to the demand pattern.** Use smooth vs. intermittent/lumpy (ADI/CV²) to decide. Do not recommend complex ML for data that a moving average forecasts equally well.
6. **Use actual demand, not shipments.** Shipments during stock-outs understate demand. Ask, and flag the issue if unknown.
7. **Run the scripts for more than a handful of series.**

## Session modes
- **Quick answer:** A metric or method question ("Is MAPE the right KPI?"). Format A.
- **Accuracy and bias review:** The user provides actuals and forecasts. Run `forecast_accuracy.py`, then diagnose where the error comes from: segment, group, process step. Format B, using `templates/forecast-review.md`.
- **Method selection:** "Which forecasting method should we use?" Run `method_backtest.py`, then give a recommendation per demand pattern. Format C.
- **Process design / target setting:** Review the demand review process, ownership, override governance and realistic accuracy targets. Format D. For the S&OP integration, hand off to `s-and-op-design`.

## Workflow

### 1. Frame
- Which decision depends on the forecast (replenishment, capacity, budget), and at which lag and aggregation level? That level is the one to measure.
- Which metric and target do they use today? Who owns the forecast, and which steps change it (statistical model, sales input, management adjustment)?
- Is the forecast used for one horizon or several (e.g. lag 1 for replenishment, lag 3 for production)?

### 2. Intake
- Determine the data tier (`references/_shared/data-intake.md`). Request:
  - actuals per SKU and period
  - forecasts **as they were at the decision lag** (snapshots, not the latest forecast)
  - ideally the statistical forecast and the final forecast separately
  - item master with unit cost and category
- Checks:
  - Do forecast periods and lags match the decision horizon?
  - Are the actuals demand or shipments?
  - Are there promotions or one-offs to tag?
  - Is the history long enough (at least 13 holdout periods; at least 2 seasonal cycles for seasonal items)?

### 3. Analyze
1. **Accuracy and bias** with `scripts/forecast_accuracy.py`. Measure in total, by group and by SKU. Value-weight when unit costs are given.
2. **Benchmark:** FVA vs. naive at the same lag, and MASE.
3. **Process steps:** FVA of each override step (`--compare-col`). Find where value is destroyed (by group or SKU).
4. **Bias pattern:** Which SKUs or groups show persistent bias (|bias| > 10% and |TS| > 4)? Is it over-forecasting after a demand decline (budget lock), optimism (sales uplift), or under-forecasting growth?
5. **Method fit** (if asked or if FVA vs. naive is weak) with `scripts/method_backtest.py`. Compare by demand pattern.
6. **Segment the effort:** high value + low forecastability → focus on collaboration and buffers. High value + high forecastability → automate. Low value → keep simple.

### 4. Synthesize
- Separate the **structural** problems (method, level, data) from the **behavioural** ones (bias from overrides, budget lock-in) and the **inherent** ones (unforecastable noise that buffers must cover).
- Quantify the impact: over-forecast volume or value, and what it implies for inventory. Hand off to `inventory-policy` for safety stock implications.

### 5. Deliver
- Use the template for the mode. Put the conclusion first.
- Label [Data], [Assumption], [Method] and [Judgement].
- Close with "What would change this answer", e.g. a different lag, shipments vs. demand, or a longer history.

## Data requirements
| Data object | Minimum | Ideal | Why it matters | Without it |
|---|---|---|---|---|
| Actuals | `sku_id, period, demand_qty`, ≥ 26 periods | Demand (orders incl. lost sales), ≥ 2 seasonal cycles, promo flags | Ground truth, naive benchmark, pattern | Cannot measure; advise on method and metric only (T0) |
| Forecast snapshots | `sku_id, period, forecast_qty` at the decision lag | Statistical and final forecast separately, with lag column | Accuracy at the lag that matters; FVA per step | Accuracy at the wrong lag misleads; say so |
| Item master | — | `unit_cost`, category, lifecycle, ABC | Value weighting, grouping, prioritisation | Unit-based aggregates; say they mix units |
| Process info | Who changes the forecast, and when | Override log with reason codes | Attribute value added or destroyed | Only the total FVA vs. naive |

## Methods
Details and formulas: `references/methods.md`. Typical mistakes: `references/pitfalls.md`.

| Situation | Method | Source |
|---|---|---|
| Aggregate accuracy | wMAPE (MAD/Mean); report bias separately | `[KS-2007]` |
| Scale-free comparison across items, zeros present | MASE | `[HK-2006]` |
| Does the process add value? | Forecast value added vs. naive, and per step | `[GIL-2010]` |
| Smooth demand, no trend or seasonality | Moving average / simple exponential smoothing | `[HA-2021]`, `[GAR-1985]` |
| Trend or seasonality | ETS / Holt-Winters, ARIMA (forecasting library; not in the scripts) | `[HA-2021]` |
| Intermittent demand | Croston with SBA correction | `[CRO-1972]`, `[SBA-2005]` |
| Intermittent with obsolescence risk | TSB | `[TSB-2011]` |
| Classify demand patterns | ADI / CV² | `[SB-2005]` |
| Information distortion along the chain | Bullwhip causes and remedies | `[LPW-1997]` |

## Scripts
| Script | Purpose | Input | Output |
|---|---|---|---|
| `scripts/forecast_accuracy.py` | Bias, wMAPE, MAPE (zeros excluded), MASE, tracking signal, FVA vs. naive and per step; total, by group, by SKU | Actuals CSV + forecast CSV (+ `--items` for cost and group) | Markdown; `--json`; `--out` |
| `scripts/method_backtest.py` | Rolling-origin backtest of naive, MA4/8/13, SES, Croston-SBA, TSB per SKU; best method by pattern | Demand CSV | Markdown; `--json`; `--out` |

```
python3 "${CLAUDE_SKILL_DIR}/scripts/forecast_accuracy.py" actuals.csv forecasts.csv --compare-col stat_forecast_qty --items items.csv --group-col category --lag 4
python3 "${CLAUDE_SKILL_DIR}/scripts/method_backtest.py" actuals.csv --lag 4 --holdout 13
```
If `${CLAUDE_SKILL_DIR}` is not substituted, use the `scripts/` path relative to this skill's folder. Use `--from`/`--to` to evaluate a specific window, for example after a known change.

**Manual fallback (no code execution):** For at most ~20 series, compute visibly: bias = Σ(F−A)/ΣA, wMAPE = Σ|F−A|/ΣA, naive wMAPE with F_t = A_(t−lag), FVA = naive wMAPE − forecast wMAPE. Example: A = 10, 20, 30, 40; F = 12, 18, 33, 40 → bias +3%, wMAPE 7%. Do not backtest methods by hand; say that the script is needed.

## Outputs
- **Quick answer:** Format A (`references/_shared/output-standards.md`).
- **Accuracy and bias review:** `templates/forecast-review.md`.
- **Method selection:** Format C, with a method-by-pattern recommendation table.
- **Process design:** Format D.

## Handoffs
| When | Hand off to | Pass along |
|---|---|---|
| Forecast error or bias needs to translate into safety stock or excess | `inventory-policy` | σ of forecast error per SKU at the replenishment lag, bias list |
| The forecast issue is one of several symptoms (service, inventory, cost) | `sc-diagnostic` | Accuracy/bias summary, FVA findings |
| Consensus or override governance and the demand review cadence need redesign | `s-and-op-design` | FVA per step, bias patterns by group |

## Guardrails
- Do not quote "industry average accuracy" figures as benchmarks. Accuracy depends on level, lag, horizon and volatility. Use the naive benchmark and the user's own history instead.
- Do not judge forecasters personally. Present FVA as a property of process steps and give it constructively.
- Do not recommend ML or "AI forecasting" by default. Recommend it only when the data volume, drivers and FVA evidence justify it, and say what it would need.
- Trend and seasonal methods are not in the scripts. For seasonal items, recommend ETS/ARIMA in a forecasting library and say so explicitly.
- Remember that accuracy measured on shipments during stock-outs is flattering.
