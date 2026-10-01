---
name: inventory-policy
description: >-
  Designs and reviews inventory policies: ABC/XYZ segmentation, service level targets,
  safety stock, reorder points, order-up-to levels and stock health (excess vs. shortage).
  Use when users ask how much stock to hold, how to set or check safety stock or reorder
  points, which service level to target, why they have stock-outs and excess at the same
  time, or say things like "we keep running out", "too much inventory", "weeks of cover",
  "min/max", "ABC analysis", "Sicherheitsbestand", "Meldebestand". Do not use for
  forecast method or accuracy questions (demand-planning-review) or broad KPI root-cause
  diagnostics (sc-diagnostic); hand off when those are the real issue.
license: MIT
metadata:
  version: 0.1.0
  domain: plan
  maturity: beta
---

# Inventory policy

Helps planners, inventory managers and supply chain leads decide **how much stock to hold, where, and why**. The skill segments the assortment, sets differentiated service targets, and sizes safety stock and reorder or order-up-to levels with established inventory theory. It also checks current stock against those targets. The user gets parameters they can defend, the trade-offs behind them, and a list of what to change first.

## Operating contract
Follow `references/_shared/operating-principles.md` at all times. In addition:

1. **Pin down the service metric first.** "Service level" can mean cycle service level (CSL) or fill rate (unit, line or order). Ask, or state your assumption. Never mix them in one table.
2. **Segment before you parameterise.** Never recommend a single service target or a single "weeks of cover" rule for the whole assortment. Use ABC (value) × XYZ (variability) and the demand pattern at minimum.
3. **Safety stock covers uncertainty, not average demand.** Size it for the protection interval: lead time plus review period. A "weeks of cover" rule is a heuristic and must be called one.
4. **Use the right uncertainty measure.** If a forecast drives replenishment, the forecast error (RMSE at the replenishment lag) is the right σ. If not, use the demand standard deviation. Say which one you use.
5. **Check the demand pattern before trusting the normal approximation.** Flag intermittent and lumpy items (ADI ≥ 1.32) and treat their numbers as indicative.
6. **Run the scripts for more than ~20 SKUs.** Never compute large tables in your head.
7. **Show the service–inventory trade-off.** Make visible what each extra point of service costs in stock. It rises steeply: going from 95% to 99% CSL raises safety stock by about 41%.
8. **When stock is high and service is low at the same time, suspect misallocation before a total shortage of stock.** Check parameters per segment, lead time changes and demand shifts before recommending "more inventory".

## Session modes
Pick the lightest mode that works and tell the user which one you are in.

- **Quick answer:** A conceptual question ("what service level should C items get?"). Give a direct answer, the method and its source, and what it depends on. Format A.
- **Parameter calculation:** The user wants safety stock, reorder points or order-up-to levels for specific SKUs. Run the intake, the scripts and a parameter table with interpretation. Use `templates/parameter-review.md`.
- **Policy design:** The user wants a segmentation and target-setting concept for the assortment. Deliver an ABC/XYZ matrix, a service target matrix, a policy type per segment and governance. Use `templates/service-target-matrix.md` and Format D.
- **Inventory health review:** "We have too much and still run out." Compare current stock and parameters against statistically sized targets, find misallocation and quantify excess and shortfall. Use Format B, then C.

## Workflow

### 1. Frame
Ask at most three questions per turn, in this order of importance:
- Which decision is this for? For example: new parameters, a target-setting concept, explaining a KPI, or reducing working capital.
- What is the scope? Number of SKUs, locations (single echelon or network), and whether replenishment is from a supplier or from production.
- Which service metric is in use (CSL or fill rate, line or unit), and what is the current target?
Restate the decision in one sentence before analysing.

### 2. Intake
- Determine the data tier (T0–T3, see `references/_shared/data-intake.md`) and state it.
- Request the data in the table below, minimum first, with a CSV template.
- Run the intake quality checks. For inventory work, check especially:
  - **Censored demand:** were stock-outs recorded as lost demand, or are these shipments?
  - **Units:** do demand periods and lead time units match?
  - **Lead time realism:** compare system lead times against actual receipts with `scripts/lead_time_stats.py`. Judge drift at supplier level first, because single SKUs have few receipts.
  - **Sample size:** at least 26 periods, and at least 2 seasonal cycles for seasonal items.

### 3. Analyze
1. **Segment.** Run `scripts/abc_xyz.py` (value-based ABC if costs are given, XYZ by CV, SBC demand pattern). Show the 3×3 matrix with counts and value share.
2. **Choose the policy type per segment** (see `references/methods.md` §2):
   - Continuous review (s, Q) for A items and critical items.
   - Periodic review (R, S) where orders are placed on fixed days or bundled by supplier.
   - (s, S) or min/max for slow movers with lumpy demand.
3. **Set service targets by segment.** Use the target matrix logic in `references/methods.md` §3. Mark default numbers as rules of thumb and invite the user to adjust them by margin, criticality and substitutability.
4. **Size the parameters.** Run `scripts/safety_stock.py`:
   - CSL method by default. Use the fill-rate method when the business steers on fill rate and Q is known.
   - Include lead time variability. If σ_L is unknown, assume CV_L = 0.2 and label it as an assumption.
5. **Check health** (if on-hand is given). Classify each SKU as below SS, ok or excess. Quantify excess value and shortfall, and compare current parameters with the calculated ones.
6. **Sensitivity.** For the main segments, show safety stock at ±1 service level step and at a lead time +50%.

### 4. Synthesize
- Translate the numbers into findings. Where is stock missing, where is it surplus, and which parameter or assumption drives each?
- Quantify the net effect: safety stock value before vs. after, expected service change, and excess to work down.
- Rank the actions by impact and effort. Typical order: fix wrong master data (lead times, MOQs), then re-segment and resize parameters, then work down excess, then set up a review cadence.

### 5. Deliver
- Use the template for the mode. Put the conclusion first.
- Label [Data], [Assumption], [Method] and [Judgement].
- Close with **"What would change this answer"**, for example the true lead time variability, forecast error instead of demand std, or a different service metric.
- Offer the full parameter table as CSV (`--out`).

## Data requirements
| Data object | Minimum | Ideal | Why it matters | Without it |
|---|---|---|---|---|
| Demand history | `sku_id, period, demand_qty`, ≥ 26 periods | 52–104 weeks of **demand (orders)**, incl. unfilled demand; per location | σ of demand, segmentation, pattern | Use the user's mean and std estimates; tier T1, indicative |
| Item master | `sku_id, unit_cost` | + category, supplier, lifecycle status, criticality | Value-based ABC; SS value | ABC by volume only. Say this misranks expensive slow movers |
| Lead times | System lead time per SKU or supplier | Actual receipts (order date, receipt date) → mean and σ_L | Protection interval; lead time variability often dominates | Assume CV_L = 0.2 and label it; flag as the top data gap |
| Replenishment settings | Order quantity / MOQ | + review period, current SS, ROP, order multiples | Cycle stock, fill-rate method, comparison with current state | Treat as continuous review; skip the fill-rate method |
| Stock position | — | On-hand, open POs, backorders per SKU | Health check: excess vs. shortfall | Skip the health check |
| Forecast | — | Forecast at replenishment lag, with history | σ = forecast error (better than demand std when a forecast exists) | Use demand std; say SS may be overstated for seasonal or trending items |
| Service targets | Current target and metric | Margin, criticality, substitution, customer SLAs | Differentiated targets | Use the default target matrix (rule of thumb) |

## Methods
Decision logic. Formulas, derivations and worked examples are in `references/methods.md`.

| Situation | Method | Source |
|---|---|---|
| Rank items by importance | ABC (Pareto on consumption value) | `[SPT-2017]` |
| Rank items by predictability | XYZ by coefficient of variation | `[SPT-2017]` |
| Detect intermittent or lumpy demand | ADI / CV² classification | `[SB-2005]` |
| Safety stock for a CSL target | SS = z · √(P·σ_d² + d̄²·σ_L²), P = L + R | `[SPT-2017]` |
| Safety stock for a fill rate target | σ_P · G(k) = (1 − β) · Q | `[SPT-2017]` |
| Lot size | EOQ as a starting point, adjusted for MOQ and order multiples | `[HAR-1913]`, `[SPT-2017]` |
| Intermittent or lumpy items | Croston/TSB forecasting, (s, S) or min/max with an empirical or Poisson check | `[CRO-1972]`, `[TSB-2011]`, `[SPT-2017]` |
| Decoupling and buffer positioning (network, BOM) | DDMRP buffer logic as an alternative view | `[PS-2016]` |

Common mistakes to avoid: `references/pitfalls.md`.

## Scripts
| Script | Purpose | Input | Output |
|---|---|---|---|
| `scripts/abc_xyz.py` | ABC (value or volume), XYZ (CV), demand pattern (ADI/CV²), 3×3 matrix | Demand CSV `sku_id, period, demand_qty`; optional `--costs` CSV `sku_id, unit_cost` | Markdown report; `--json`; `--out stats.csv` |
| `scripts/lead_time_stats.py` | Actual lead time mean and σ per SKU and supplier, promised vs. actual, drift detection | Receipts CSV `sku_id, order_date, received_date` [+ `supplier_id, promised_date`] | Markdown; `--json`; `--out lead_times.csv` |
| `scripts/safety_stock.py` | SS, ROP or order-up-to, implied fill rate, cycle stock, stock health | Parameter CSV (see `--help`); optional `--history`, `--patterns stats.csv` | Markdown table; `--json`; `--out results.csv` |

Typical chain:
```
python3 "${CLAUDE_SKILL_DIR}/scripts/abc_xyz.py" demand.csv --costs items.csv --out stats.csv
python3 "${CLAUDE_SKILL_DIR}/scripts/lead_time_stats.py" receipts.csv --out lead_times.csv   # merge into params.csv
python3 "${CLAUDE_SKILL_DIR}/scripts/safety_stock.py" params.csv --history demand.csv --patterns stats.csv --period-days 7 --target 0.95
```
If `${CLAUDE_SKILL_DIR}` is not substituted, use the `scripts/` path relative to this skill's folder. Run `--help` for all options, including per-SKU `service_level`, `forecast_error_std` and `*_days` columns.

To set targets by segment, add a `service_level` column to the parameter CSV based on the ABC/XYZ class before running `safety_stock.py`.

**Manual fallback (no code execution):** Compute visibly for at most ~20 SKUs and state that the full assortment needs the script.
- **Safety stock:** SS = z · √(P·σ_d² + d̄²·σ_L²). Use the z table in `references/methods.md` §4. Worked example: d̄ = 100/week, σ_d = 30, L = 2 weeks, σ_L = 0.5 weeks, 95% CSL → σ_P = √4300 = 65.6, SS = 1.645 × 65.6 ≈ 108, ROP = 200 + 108 = 308.
- **ABC:** sort by value and use cumulative shares.
- **XYZ:** CV = std ÷ mean.

## Outputs
- **Quick answer:** Format A from `references/_shared/output-standards.md`.
- **Parameter calculation:** `templates/parameter-review.md`.
- **Policy design:** `templates/service-target-matrix.md` plus Format D.
- **Inventory health review:** Format B (diagnosis), then Format C (options), or Format E (executive brief) if the audience is management.

## Handoffs
| When | Hand off to | Pass along |
|---|---|---|
| Forecast error or bias drives the safety stock, or forecasts are clearly off | `demand-planning-review` | SKU list with σ used, suspected bias, segment |
| Symptom is broader than parameters (service and cost KPIs across functions) | `sc-diagnostic` | Health check results, data quality note |
| Parameters need governance: review cadence, ownership, S&OP linkage | `s-and-op-design` | Target matrix, proposed review cycle |
| Supplier lead time, reliability or MOQ is the binding constraint | `sourcing-strategy` | Affected SKUs and suppliers, lead time stats, MOQ impact on stock |

## Guardrails
- Do not present normal-approximation results for intermittent or lumpy items as precise. Flag them and suggest an empirical or simulation check.
- Do not recommend 99%+ service across the board, and do not accept "100% service" as a target. Explain the stock cost.
- Do not invent holding cost rates, stock-out costs or industry benchmarks. Ask for them, or use an explicit assumption (e.g. "holding cost 20%/year, rule of thumb") and show its effect.
- Multi-echelon networks (central and regional warehouses) need more than single-location formulas. Say so, give the single-echelon view as a first approximation, and recommend a multi-echelon approach `[AXS-2015]`.
- Perishables, shelf-life and regulated items (pharma, food) need extra constraints. Flag them and do not ignore expiry.
- The stock health check uses on-hand only. Say that open orders and backorders can change the picture.
