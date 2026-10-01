---
type: llm
---

PASS only if ALL of the following hold:
1. Explains that MAPE is distorted (inflated/undefined) for low-volume and zero-demand items, and recommends a more robust metric such as wMAPE (MAD/Mean) and/or MASE.
2. Recommends measuring bias separately from accuracy.
3. Recommends comparing against a naive benchmark (forecast value added or MASE) rather than an external "best in class" number.
4. States that the measurement level and lag (how far ahead the forecast was made) must be defined, because accuracy figures are not comparable otherwise.

FAIL if the response accepts the external 85% target as a meaningful benchmark without qualification.
FAIL if it states specific industry accuracy figures as facts without labelling them as unverified or rules of thumb.
