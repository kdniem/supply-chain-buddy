---
type: llm
---

Reference: VLV-100, VLV-200 and GSK-300 have smooth demand; SPR-410 and SPR-420 are intermittent and SPR-430 is lumpy (many zero weeks). On a 13-week holdout, smoothing methods (SES/MA) beat naive for the smooth items; for the SPR items rankings are noisy because there are few demand events, and MAE-type metrics can favour near-zero forecasts.

PASS only if ALL of the following hold:
1. The response distinguishes the smooth items (VLV-100, VLV-200, GSK-300) from the intermittent/lumpy SPR items.
2. It recommends an intermittent-demand method (Croston/SBA or TSB) or an explicitly justified alternative for the SPR items, and simple smoothing (SES/moving average/ETS) for the smooth items.
3. The recommendation is backed by an out-of-sample (holdout/backtest) comparison or explicitly compared against a naive benchmark.
4. It gives at least one caveat about evaluating intermittent items (e.g. short holdout/few demand events, MAE favouring zero forecasts, need to consider bias or stock implications).

FAIL if it recommends one method for all six items without differentiation.
