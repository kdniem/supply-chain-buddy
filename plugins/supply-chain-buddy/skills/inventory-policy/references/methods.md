# Methods: inventory policy

Formulas, decision logic and worked examples. Sources by key, see `_shared/methods-library.md`.

## §1 Segmentation

### ABC (importance)
- **When:** Always the first step. Use **consumption value** (annual quantity × unit cost), not volume. Volume-based ABC over-rates cheap fast movers and under-rates expensive slow movers. `[SPT-2017]`
- **Procedure:** Sort by value in descending order and compute cumulative shares. Typical cuts: A < 80%, B < 95%, C rest (rule of thumb; adjust). The script assigns the item that crosses a threshold to the higher class.
- **Extensions:** Multi-criteria ABC (criticality, margin, customer importance) when value alone misleads, for example for spare parts with low value but high criticality.

### XYZ (predictability)
- **When:** Together with ABC, to distinguish stable from volatile items.
- **Formula:** CV = σ ÷ μ of per-period demand. Typical cuts: X ≤ 0.5, Y ≤ 1.0, Z > 1.0 (rule of thumb). The cuts depend on the period length: weekly CVs are higher than monthly CVs. State the period.
- **Caveat:** CV mixes predictable variation (trend, seasonality) with noise. If a good forecast exists, the CV of the **forecast error** is the better predictability measure.

### Demand pattern (Syntetos–Boylan–Croston) `[SB-2005]`
- ADI = periods ÷ periods with demand. CV² = squared CV of the **non-zero** demand sizes.
- Classes: smooth (ADI < 1.32, CV² < 0.49), erratic (ADI < 1.32, CV² ≥ 0.49), intermittent (ADI ≥ 1.32, CV² < 0.49), lumpy (both ≥).
- **Consequence:** The normal approximation for safety stock works reasonably for smooth items. It is shaky for erratic items and unreliable for intermittent and lumpy ones. For those, use Croston/TSB forecasts `[CRO-1972]` `[TSB-2011]` and check stock levels empirically, for example with a bootstrap over the lead time demand or a Poisson or negative binomial fit `[SPT-2017]`.

## §2 Policy type per segment `[SPT-2017]`
| Policy | Logic | Fits |
|---|---|---|
| (s, Q) continuous review | Order Q when the inventory position ≤ s (reorder point) | A items, critical items, items with real-time stock visibility |
| (R, S) periodic review | Every R periods, order up to S | Fixed ordering days, supplier consolidation, many C items |
| (s, S) / min-max | When the position ≤ s, order up to S | Slow, lumpy items; spare parts |
| (R, s, S) | Periodic check, order up to S only if ≤ s | C items with ordering cost; most general, hardest to tune |

**Inventory position** = on-hand + on-order − backorders. Trigger decisions on the position, not on on-hand alone.

## §3 Service targets by segment (default matrix, rule of thumb)
A starting point to discuss with the user. It is not a benchmark.

| | X | Y | Z |
|---|---|---|---|
| **A** | 97–98% | 95–97% | 93–95%, check whether make-to-order fits |
| **B** | 95–97% | 93–95% | 90–93% |
| **C** | 93–95% | 90–93% | 85–90%, or make-to-order / no stock |

The values are cycle service levels. Adjust them for:
- **Margin and criticality:** high margin or a line-stopping item → higher target.
- **Substitutability:** a substitute is available → lower target.
- **Customer contracts:** SLA-bound → set the target from the contract.
- **Lifecycle:** phase-out → lower target, run down stock.

Logic: A-item safety stock is expensive in absolute terms, but A items drive most of the revenue and service perception. Lowering C targets frees inventory at little service cost, because C items are a small share of demand. Calculate the aggregate fill rate across segments and check it against the business target.

## §4 Safety stock and reorder points `[SPT-2017]`

### Notation
d̄ = mean demand per period, σ_d = std of demand (or of forecast error) per period, L = lead time in periods, σ_L = std of lead time in periods, R = review period, P = L + R = protection interval, Q = order quantity.

### Combined demand and lead time uncertainty
σ_P = √( P · σ_d² + d̄² · σ_L² )

This assumes independent per-period demand and lead time independent of demand. If demand is autocorrelated (e.g. promotions, trends), σ_P is understated.

### CSL-based (k = z)
SS = z · σ_P, with z = Φ⁻¹(CSL)

| CSL | 85% | 90% | 95% | 97% | 98% | 99% | 99.5% | 99.9% |
|---|---|---|---|---|---|---|---|---|
| z | 1.036 | 1.282 | 1.645 | 1.881 | 2.054 | 2.326 | 2.576 | 3.090 |

Going from 95% to 99% raises SS by 2.326 ÷ 1.645 − 1 ≈ **41%**. Going from 99% to 99.9% adds another 33%.

### Reorder point and order-up-to
- (s, Q): ROP = d̄ · L + SS
- (R, S): S = d̄ · (L + R) + SS

### Fill-rate-based (β)
The expected shortage per replenishment cycle is σ_P · G(k), where G(k) = φ(k) − k·(1 − Φ(k)) is the standard normal loss function. For a target fill rate β, solve:

σ_P · G(k) = (1 − β) · Q   (Q = order quantity; d̄·R for periodic review)

A large Q reduces the safety stock needed for a given fill rate, because there are fewer cycles per year. For the same nominal percentage, CSL and fill rate give very different SS. 95% CSL usually implies a fill rate well above 95%.

### Worked example
d̄ = 100 units/week, σ_d = 30, L = 2 weeks, σ_L = 0.5 weeks, Q = 400, continuous review.
- σ_P = √(2·30² + 100²·0.5²) = √(1800 + 2500) = √4300 = **65.6**. Lead time variability contributes more than demand variability here.
- 95% CSL: SS = 1.645 × 65.6 = **108**; ROP = 200 + 108 = **308**. Implied fill rate = 1 − 65.6·G(1.645)/400 = 1 − 65.6 × 0.0209 / 400 ≈ **99.7%**.
- 98% fill rate: G(k) = 0.02 × 400 / 65.6 = 0.122 → k ≈ 0.79 → SS ≈ **52**.
- Without lead time variability (σ_L = 0): σ_P = 42.4 → SS (95% CSL) = 70. Ignoring σ_L understates SS by 35%.

### Forecast error instead of demand std
If replenishment follows a forecast, use σ_e = RMSE of the forecast at the replenishment lag, scaled to the protection interval: σ_e · √P if errors are independent. Seasonal or trending items: demand std overstates the uncertainty, so σ_e is lower and correct. Badly forecast items: σ_e can exceed demand std. That is a forecasting problem; hand off to `demand-planning-review`.

## §5 Lot sizing
- **EOQ** `[HAR-1913]`: Q* = √(2·D·S ÷ H), with D = annual demand, S = cost per order, H = holding cost per unit per year (= unit cost × holding rate). The total cost curve is flat near the optimum, so ±20% around Q* barely changes cost.
- **Practical constraints:** MOQ, order multiples, pallet or container quantities, supplier ordering days. Round Q up to feasible quantities and show the extra cycle stock (ΔQ ÷ 2 × unit cost).
- **Cycle stock** ≈ Q ÷ 2. MOQ increases often raise inventory more than safety stock changes do.

## §6 Stock health and misallocation
- Target average stock ≈ SS + Q/2. A reasonable maximum ≈ SS + Q (continuous review).
- **Below SS:** high stock-out risk, unless an inbound PO is due soon (check open orders).
- **Excess:** on-hand above SS + Q. Quantify it in value and in weeks of current demand. Typical causes: a demand decline, parameters not updated, project or speculative buys, MOQ increases, forecast bias.
- **"High inventory + low service" pattern:** compare the excess value on some items with the shortfall on others. Often total stock is sufficient but sits on the wrong items. Fix parameters and master data before adding stock.

## §7 Sensitivity and trade-off curve
For a segment, compute SS value at CSL 90/95/97/98/99%. Plot or tabulate SS value against the aggregate fill rate. Use this to discuss targets with management: "each extra point of service costs X in inventory".
