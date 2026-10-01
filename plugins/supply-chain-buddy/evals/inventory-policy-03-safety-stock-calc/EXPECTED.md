# Expected results (hand-calculated)

z(95%) = 1.6449. σ_P = √(L·σ_d² + d̄²·σ_L²).

| SKU | σ_P | SS | ROP = d̄·L + SS |
|---|---|---|---|
| P-100 | √(2·900 + 10000·0.25) = √4300 = 65.57 | 107.9 | 307.9 |
| P-200 | √(1·100) = 10.00 | 16.4 | 66.4 |
| P-300 | √(4·225 + 400·1) = √1300 = 36.06 | 59.3 | 139.3 |
| P-400 | √(3·36) = √108 = 10.39 | 17.1 | 32.1 |

Points worth raising:
- P-300 and P-100: lead time variability contributes heavily (P-300: 400 of 1300 in variance; P-100: 2500 of 4300).
- P-400: CV = 1.2. Likely intermittent or lumpy, so the normal approximation is questionable.
