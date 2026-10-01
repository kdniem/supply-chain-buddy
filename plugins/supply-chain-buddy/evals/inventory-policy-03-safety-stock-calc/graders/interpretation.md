---
type: llm
---

Reference values (95% CSL, z ≈ 1.645): P-100 SS ≈ 108 / ROP ≈ 308; P-200 SS ≈ 16 / ROP ≈ 66; P-300 SS ≈ 59 / ROP ≈ 139; P-400 SS ≈ 17 / ROP ≈ 32 (±1 unit rounding is fine).

PASS only if ALL of the following hold:
1. The safety stock formula used includes lead time variability (a term like d̄²·σ_L²), and the results are consistent with the reference values above.
2. The answer points out at least one of: (a) lead time variability is a major driver for P-100 and/or P-300, or (b) P-400 has a coefficient of variation above 1 and the normal approximation may be unreliable (intermittent/lumpy demand).
3. It states or implies which service metric was used (cycle service level) and the units (weeks / units).

FAIL if safety stocks ignore lead time variability (e.g. P-100 SS ≈ 70), or if more than one SKU's numbers deviate materially from the reference.
