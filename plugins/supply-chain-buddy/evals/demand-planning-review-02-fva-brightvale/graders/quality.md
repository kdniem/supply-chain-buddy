---
type: llm
---

Reference (value-weighted, 2026-W14 onwards, lag 4): statistical forecast wMAPE ≈ 39%, bias ≈ +2%; final/consensus forecast wMAPE ≈ 45%, bias ≈ +15%; i.e. the consensus step makes the forecast WORSE (negative forecast value added of roughly 6 points). The damage is concentrated in PNEU (pneumatics; over-forecast ≈ +40%, final forecast stuck at the old level after a demand decline) and HYDR (hydraulics; over-forecast ≈ +35%, uplift added by sales). Other categories show near-zero difference between statistical and final forecast.

PASS only if ALL of the following hold:
1. The response compares the final/consensus forecast with the statistical forecast and concludes that the consensus/override step reduces accuracy (negative FVA or equivalent wording), with numbers broadly consistent with the reference.
2. It identifies over-forecasting (positive bias) concentrated in pneumatics/PNEU and hydraulics/HYDR.
3. It recommends process changes addressing the overrides (e.g. re-baselining after the demand decline, removing unconfirmed uplifts, override governance / FVA tracking), not only a different statistical model.

FAIL if the answer only reports one overall accuracy number without bias or step comparison.
