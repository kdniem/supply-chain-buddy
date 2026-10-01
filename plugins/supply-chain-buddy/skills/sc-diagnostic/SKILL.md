---
name: sc-diagnostic
description: >-
  Diagnoses supply chain performance problems: turns a symptom (falling service or OTIF,
  rising inventory, cost overruns, stock-outs and excess at the same time) into a KPI tree
  and testable hypotheses, requests the right data, quantifies which suppliers, categories
  or segments drive a KPI change (rate vs. mix), and finds root causes. Also runs
  SCOR-based supply chain health checks and maturity assessments. Use when users ask
  "what's going on", "why did our fill rate / OTIF drop", "why is inventory up",
  "root cause", "KPI deep dive", "health check", "assess our supply chain",
  "Ursachenanalyse". Hands off to inventory-policy, demand-planning-review and other
  specialist skills once the causes are located.
license: MIT
metadata:
  version: 0.1.0
  domain: cross-functional
  maturity: beta
---

# Supply chain diagnostic

Helps supply chain managers, analysts and consultants get **from a symptom to evidenced root causes and a prioritised action list**. It works hypothesis-driven, with a KPI tree first, then targeted data, then quantified attribution and root-cause analysis. It does not boil the ocean. It also offers a structured SCOR-based health check for a broader assessment.

## Operating contract
Follow `references/_shared/operating-principles.md` at all times. In addition:

1. **Pin down the symptom precisely.** Get the KPI definition, the magnitude, when it started, the scope and the trend vs. one-off. "Service is bad" is not a symptom yet.
2. **Hypotheses before data.** Build the KPI tree and a MECE hypothesis list, then request only the data that tests them. Rank hypotheses by likelihood × impact × ease of testing.
3. **Separate the symptoms.** When several KPIs move (e.g. service ↓ and inventory ↑), test whether they share a cause or have different ones. Stock-outs and excess at the same time usually means misallocation, not too little stock.
4. **Quantify attribution.** Use KPI bridges (rate vs. mix by supplier, category or segment) to show where a change comes from before naming causes.
5. **Distinguish proximate from systemic causes.** "SUP-03 lead time doubled" is proximate. "Lead times in the ERP are never reviewed" is systemic. Recommend fixes for both.
6. **State confidence per finding** (high/medium/low) and what evidence would confirm or refute it.
7. **Hand off the deep dives.** Locate the cause here and let the specialist skill size the fix (safety stocks, forecast process, sourcing).

## Session modes
- **Quick triage:** A symptom without data. Give a KPI tree, the top 3–5 hypotheses, the 3 fastest checks, and the data to send. Format B (hypothesis version).
- **Data-driven diagnosis:** A symptom with data. Run bridges and tests, and deliver ranked root causes with evidence and actions. Format B, then C or E. Use `templates/diagnostic-report.md`.
- **Health check:** A broad assessment without a single symptom. Use the SCOR-based maturity questionnaire, KPI snapshot, heatmap and priorities from `references/health-check.md`. Format D or E. In the first reply, show the structure (areas, scale, how priorities are derived), then ask the first block of questions (scope plus the first process area, at most 5) and request the KPI snapshot with definitions.

## Workflow

### 1. Frame
- **No data provided:** give the KPI tree, the top hypotheses and a concrete data request in the first reply, then ask at most three framing questions.
- **Data provided:** do not stop after framing. State assumptions for open framing points and run the full workflow (hypotheses → bridges → tests → root causes → actions) in the same reply.
- Framing questions:
- Which KPI, which definition, which value now vs. before, and since when? Which scope (sites, categories, customers)?
- What has changed in the period? Ask about suppliers, assortment, customers, systems, policies, organisation, volumes and prices.
- Which decision is pending: a quick fix, a management explanation, or a structural programme?

### 2. Hypotheses
- Build the KPI tree for the symptom from `references/methods.md` §1: service, inventory or cost.
- List hypotheses across **demand**, **supply**, **policy/parameters**, **process/execution** and **data/measurement**. Rank them.
- Translate each hypothesis into a test: which data, which cut, what result would confirm or refute it.

### 3. Intake
- Request the data that tests the top hypotheses, minimum first (see *Data requirements*). Name the tier (T0–T3).
- Run data quality checks. **Definition drift** (a KPI calculated differently over time) is itself a hypothesis.

### 4. Analyze
1. **Locate.** Run `scripts/kpi_bridge.py` for each moving KPI, cut by the dimensions in the hypotheses (supplier, category, segment, site, customer). Rate vs. mix tells you whether a group got worse or just grew in weight.
2. **Time.** Find the change point in the weekly series, and match it to events in the change log.
3. **Test** the top-ranked hypotheses with the specialist scripts if available. Inside the plugin they sit under `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/`:
   - lead time drift: `inventory-policy/scripts/lead_time_stats.py`
   - forecast bias and FVA: `demand-planning-review/scripts/forecast_accuracy.py`
   - parameter health: `inventory-policy/scripts/safety_stock.py`
   If those skills are not installed, request their analysis or do a simplified test and say so.
4. **Root cause.** For each confirmed driver, ask "why" until you reach a process or policy cause (5 Whys `[OHN-1988]`). Use a fishbone diagram `[ISH-1986]` when causes are many and interacting.

### 5. Synthesize and deliver
- Rank the root causes by quantified impact on the KPI, with confidence and evidence.
- Separate quick wins (master data, expediting, parameter corrections) from structural fixes (policy, process, governance) and say who should own each (as roles).
- Give a "what we ruled out" list. It builds trust and avoids repeated debates.
- Close with "What would change this answer".

## Data requirements
| Data object | Minimum | Ideal | Why it matters | Without it |
|---|---|---|---|---|
| KPI history | Monthly KPI values with definition | Weekly, at SKU or order line level (`period, sku_id, demand_qty, shipped_qty`) | Size the symptom, find the change point, enable bridges | Hypotheses only (T0/T1) |
| Item master | `sku_id`, category, supplier | + unit cost, ABC class, lifecycle | Group cuts, value weighting | Unit-based cuts; say they mix items |
| Inventory history | Monthly inventory value | Weekly on-hand (and on-order) per SKU | Inventory bridge by group | Total inventory trend only |
| Supply data | Supplier OTD summary | PO receipts (order, promised, received dates) | Test lead time and reliability hypotheses | Rely on the user's description |
| Demand and forecast | Demand history | Forecast snapshots (statistical and final) | Test demand shift and bias hypotheses | Demand-only tests |
| Change log | What changed and when | Dated list of supplier, assortment, policy and system changes | Match change points to events | Ask targeted questions |

## Methods
Details: `references/methods.md`. Health check: `references/health-check.md`. Typical mistakes: `references/pitfalls.md`.

| Situation | Method | Source |
|---|---|---|
| Structure a symptom | KPI tree; MECE issue tree; answer-first synthesis | `[MIN-1987]` |
| Locate a ratio KPI change | Shift-share bridge (rate vs. mix effect) | – (standard variance analysis) |
| Find root causes | 5 Whys; cause-and-effect (fishbone) diagram | `[OHN-1988]`, `[ISH-1986]` |
| Broad assessment | SCOR-based process and KPI health check | `[SCOR-DS]` |
| Strategic fit questions | Efficient vs. responsive supply chain | `[FIS-1997]` |
| Volatility amplification upstream | Bullwhip effect | `[LPW-1997]` |
| Resilience and risk findings | Resilience principles, risk categories | `[CP-2004]`, `[CS-2004]` |

## Scripts
| Script | Purpose | Input | Output |
|---|---|---|---|
| `scripts/kpi_bridge.py` | Compare a KPI between two windows and attribute Δ to groups. Ratio KPIs: rate and mix effect. Additive KPIs: contribution and share | Long CSV with a period column; optional `--join` item master; `--multiply-by unit_cost` for value | Markdown; `--json` |

```
python3 "${CLAUDE_SKILL_DIR}/scripts/kpi_bridge.py" fulfillment.csv --ratio shipped_qty demand_qty \
  --base 2025-W41:2026-W01 --compare 2026-W28:2026-W40 --by supplier_id --join items.csv --on sku_id --multiply-by unit_cost
python3 "${CLAUDE_SKILL_DIR}/scripts/kpi_bridge.py" snapshots.csv --value on_hand_qty --agg mean \
  --base ... --compare ... --by category --join items.csv --on sku_id --multiply-by unit_cost
```
If `${CLAUDE_SKILL_DIR}` is not substituted, use the `scripts/` path relative to this skill's folder. Choose windows of equal length that avoid a known one-off, and say which ones you used.

**Manual fallback (no code execution):** For a handful of groups, compute per window w_g = DEN_g/ΣDEN and r_g = NUM_g/DEN_g. Then rate effect = (r2 − r1)·w̄ and mix effect = (w2 − w1)·(r̄_g − R̄). Check that the effects sum to Δ.

## Outputs
- **Quick triage:** Format B as a hypothesis list (`references/_shared/output-standards.md`), plus a data request block.
- **Data-driven diagnosis:** `templates/diagnostic-report.md`; Format E for management.
- **Health check:** maturity heatmap and priorities (`references/health-check.md`), Format D.

## Handoffs
| When | Hand off to | Pass along |
|---|---|---|
| Causes involve safety stock, parameters, lead times or excess | `inventory-policy` | Affected SKUs and suppliers, bridge results, lead time stats |
| Causes involve forecast bias, overrides or method fit | `demand-planning-review` | Affected groups, window, bias evidence |
| Causes involve planning governance, cross-functional alignment or cadence | `s-and-op-design` | Systemic causes, decision rights gaps |
| Causes involve supplier performance, MOQs or sourcing strategy | `sourcing-strategy` | Supplier evidence, TCO-relevant facts |

## Guardrails
- Do not declare a root cause on correlation alone. Show the mechanism and the evidence, and state the confidence.
- Do not recommend "more inventory" or "a new system" as a default fix for a diagnosis that has not located the cause.
- Do not blame individuals or functions. Frame causes as process, policy, data or design issues.
- If the KPI definition changed over the period, stop and re-baseline before diagnosing.
- In a health check, do not present maturity scores as precise. They are a structured judgement based on the answers given.
