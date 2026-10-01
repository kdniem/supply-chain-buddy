---
# Use for analysis cases: checks a hand-calculated key result appears in the answer.
# Delete for routing/advisory cases.
type: regex
target: last_message
pattern: 'TODO e.g. 1[,.]?2\d\d\s*units'
flags: i
---
