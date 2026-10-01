# Evals

Behavioural test cases for `claude plugin eval`. Each case runs **with** the plugin and **without** it (baseline), so the reported Δ shows what the skills add.

## Run
From `plugins/supply-chain-buddy/`:
```bash
claude plugin eval . --scaffold --allow-tools Bash Write --trust-plugin --no-publish
# one skill only:
claude plugin eval . --case 'inventory-policy-*' --scaffold --allow-tools Bash Write
# cheap iteration on graders (no baseline arm):
claude plugin eval . --ablation none --runs 1 ...
```
- `--scaffold` copies fixture files into the run workspace (only for cases with `case.yaml` → `scaffold_script`).
- `--allow-tools Bash Write` lets the skills run their calculation scripts. Bash runs sandboxed; on Linux this needs `bubblewrap` and `socat`.
- Results land in `results/` (git-ignored).

## Case naming
`<skill>-<nn>-<slug>`, with at least 3 per skill: routing/trigger, advisory without data, analysis with data. See `docs/skill-authoring-guide.md` §7.

## Latest results
| Date | Claude Code | Cases | Runs/arm | With plugin | Without | Mean Δ |
|---|---|---|---|---|---|---|
| 2026-10-01 | 2.1.286 (default model and judge) | inventory-policy 01–04 | 3 | 1.00 (4/4 cases) | 0.83 | +0.17 |

Per case (2026-10-01):

| Case | With | Without | What made the difference |
|---|---|---|---|
| inventory-policy-01 (flat cover, routing) | 1.00 | 1.00 | Strong base model handles the concept |
| inventory-policy-02 (99% service advice) | 1.00 | 1.00 | Strong base model handles the concept |
| inventory-policy-03 (SS/ROP calculation) | 1.00 | 0.83 | Baseline occasionally wrong on the lead-time-variability item |
| inventory-policy-04 (ABC/XYZ on demo data) | 1.00 | 0.50 | Baseline never classified demand patterns (lumpy/intermittent) |

Takeaway: on conceptual questions the base model is already good. The skill adds the most where **methods must be applied to data correctly and completely**. New cases should target exactly that.
