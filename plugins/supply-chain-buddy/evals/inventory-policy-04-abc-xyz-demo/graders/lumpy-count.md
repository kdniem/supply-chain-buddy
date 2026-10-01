---
# The fixture contains 10 SKUs with lumpy demand (ADI >= 1.32 and CV² >= 0.49).
type: regex
target: last_message
pattern: '\b10\b[^.\n]{0,30}lumpy|lumpy[^.\n]{0,30}\b10\b'
flags: i
---
