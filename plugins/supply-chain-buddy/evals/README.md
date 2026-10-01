# Evals

Behavioural test cases for `claude plugin eval`. Each case runs **with** the plugin and **without** it (baseline), so the reported Δ shows what the skills add.

## Run
From `plugins/supply-chain-buddy/`:
```bash
claude plugin eval . --scaffold --allow-tools Bash Write --trust-plugin --no-publish
# one skill only:
claude plugin eval . --case 'inventory-policy-*' --scaffold --allow-tools Bash Write
# a smaller model:
claude plugin eval . --model claude-haiku-4-5 --scaffold --allow-tools Bash Write
# cheap iteration on graders (no baseline arm):
claude plugin eval . --ablation none --runs 1 ...
# tables for this README:
claude plugin eval . ... --json results.json && python3 ../../tools/eval_table.py "Label=results.json"
```
- `--scaffold` copies fixture files into the run workspace (only for cases with `case.yaml` → `scaffold_script`).
- `--allow-tools Bash Write` lets the skills run their calculation scripts. Bash runs sandboxed; on Linux this needs `bubblewrap` and `socat`.
- Results land in `results/` (git-ignored).

## Case naming
`<skill>-<nn>-<slug>`, with at least 3 per skill: routing/trigger, advisory without data, analysis with data. See `docs/skill-authoring-guide.md` §7.

## Latest results (2026-10-01, Claude Code 2.1.286, default judge, 3 runs per arm)

### Smaller model: Claude Haiku 4.5
| Cases | With plugin | Without | Mean Δ |
|---|---|---|---|
| 10 | **0.96** | 0.41 | **+0.55** |

| Case | With | Without |
|---|---|---|
| demand-planning-review-01-mape-target | 1.00 | 1.00 |
| demand-planning-review-02-fva-brightvale | 1.00 | 0.67 |
| demand-planning-review-03-method-selection | 1.00 | 1.00 |
| inventory-policy-01-flat-cover-routing | 1.00 | 0.00 |
| inventory-policy-02-service-target-advice | 1.00 | 0.00 |
| inventory-policy-03-safety-stock-calc | 1.00 | 0.83 |
| inventory-policy-04-abc-xyz-demo | 0.83 | 0.17 |
| sc-diagnostic-01-triage | 1.00 | 0.33 |
| sc-diagnostic-02-flagship-brightvale | 0.78 | 0.11 |
| sc-diagnostic-03-health-check | 1.00 | 0.00 |

### Default model (frontier)
Run on the final version, with the same result as the earlier run on the previous version.

| Cases | With plugin | Without | Mean Δ |
|---|---|---|---|
| 10 | **1.00** | 0.93 | +0.07 |

Only two cases separate the arms: `inventory-policy-03` (1.00 vs. 0.83; the baseline is occasionally wrong on the lead-time-variability item) and `inventory-policy-04` (1.00 vs. 0.50; the baseline never classifies demand patterns). All other cases score 1.00 in both arms, including the flagship diagnosis.

### What this means
- **Frontier models with code execution already solve most of these tasks.** With the plugin, their answers are more structured (confidence levels, ruled-out hypotheses, systemic causes, data tier). The current rubrics do not score that difference.
- **Smaller, cheaper models gain a lot.** Haiku solves the flagship diagnosis in most runs with the plugin and almost never without it. Across the suite, the plugin lifts it from 0.41 to 0.96.
- Next steps: add rubric criteria for consulting-grade structure, and add harder cases (multi-step, conflicting data) where frontier models also differ.

## Lessons from eval-driven iteration
- Small models tended to reply with questions only. Fix: *"lead with substance, then at most three questions"* in `shared/operating-principles.md`.
- When data was already provided, a "frame first" instruction made small models stop after framing. Fix: *"if the user has provided data, do not stop to ask framing questions"*.
- A small model called line fill rate a "proxy" for CSL. Fix: an explicit rule in `inventory-policy`.
