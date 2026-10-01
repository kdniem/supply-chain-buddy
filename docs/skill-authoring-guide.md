# Skill authoring guide

Every Supply Chain Buddy skill follows this standard. The template in `templates/skill/` implements it. `tools/validate_repo.py` checks the mechanical parts.

## 1. What makes a good Buddy skill
A skill is a **consulting playbook**, not an encyclopedia entry. It tells the model how an experienced practitioner works through one class of problem:

1. Understand the decision behind the question.
2. Get the right data, or proceed transparently without it.
3. Apply the right method, and know when it does not apply.
4. Synthesize options and trade-offs into a recommendation.
5. Hand off to other skills when the problem crosses boundaries.

Depth beats breadth. A skill that handles safety stock really well, including its pitfalls such as lead-time variability, intermittent demand and the difference between cycle service level and fill rate, is worth more than ten shallow ones.

## 2. Folder anatomy
```
skills/<skill-name>/
├── SKILL.md                 # the playbook (≤ 300 lines)
├── references/
│   ├── _shared/             # GENERATED from /shared, do not edit
│   ├── methods.md           # formulas, method selection logic, worked examples
│   └── pitfalls.md          # common mistakes and how to detect them
├── templates/               # output templates specific to this skill
└── scripts/                 # optional deterministic calculations
```
`<skill-name>` is kebab-case and equals the `name` in the frontmatter.

## 3. SKILL.md frontmatter
```yaml
---
name: inventory-policy
description: >-
  <What it does> + <when to use it, with the trigger phrases users actually say>.
  Max ~900 characters. Mention adjacent skills it should NOT be confused with.
license: MIT
metadata:
  version: 0.1.0
  domain: plan | source | make | deliver | return | enable | cross-functional
  maturity: draft | beta | stable
---
```
The `description` decides whether the skill fires. Write it as triggers: the words a planner would type ("safety stock", "reorder point", "we keep running out", "too much stock").

## 4. SKILL.md body (fixed section order)
| # | Section | Content |
|---|---|---|
| 1 | Title + one-paragraph purpose | What problem class, for whom |
| 2 | Operating contract | 5–8 skill-specific rules. Always include: read `references/_shared/operating-principles.md` |
| 3 | Session modes | 2–4 modes (e.g. *Quick answer*, *Guided analysis*, *Concept/design*, *Review of existing setup*). The skill picks the lightest mode that works and tells the user which mode it uses |
| 4 | Workflow | Phases: **Frame → Intake → Analyze → Synthesize → Deliver**, with concrete questions and checks per phase |
| 5 | Data requirements | Table: data object · minimum fields · ideal fields · why needed · what happens without it |
| 6 | Methods | Short decision logic for picking a method, plus links to `references/methods.md`. Each method cites a `shared/methods-library.md` key, e.g. `[SPT-2017]` |
| 7 | Scripts | Invocation, input format, output, and the **manual fallback** |
| 8 | Outputs | Which templates to use (`templates/…` or `_shared/output-standards.md`) |
| 9 | Handoffs | When to involve which other skill, and what to pass along |
| 10 | Guardrails | What the skill must not do, scope limits, typical misinterpretations |

## 5. Writing style inside skills
- Imperative, specific, testable: "Ask for lead time variability; if unknown, assume CV = 0.2 and label it" beats "consider lead time variability".
- State *what to do*. Explain *why* only where the reason changes behaviour.
- Use glossary terms exactly (`shared/kpi-glossary.md`). For example, never use "service level" without saying whether it means cycle service level or fill rate.
- No invented benchmarks. Typical ranges are allowed only with a source key or the label *rule of thumb*.
- English, plain business language, no hype.

## 6. Scripts
- Python ≥ 3.9, **standard library only**, single file, `argparse` CLI, `--help` works.
- Input: CSV with documented columns (header names in snake_case). Output: a Markdown table or report to stdout, and `--json` for machine-readable output.
- Validate the input and fail with a helpful message that names the column and row.
- Deterministic. No network or file writes, except an explicit `--out` path.
- Invocation in SKILL.md:
  ```
  python3 "${CLAUDE_SKILL_DIR}/scripts/<script>.py" <args>
  ```
  If the variable is not substituted, use the path relative to the skill folder.
- Unit tests in `/tests/test_<skill>_<script>.py` include at least one hand-checked numeric example.
- **Fallback** in SKILL.md: the formula, a worked mini example, and the instruction to compute visibly for at most about 20 rows and to say that the full dataset needs the script.

## 7. Evals (per skill, minimum)
Cases live in `plugins/supply-chain-buddy/evals/<skill>-<nn>-<slug>/`. Copy them from `templates/eval-case/`.

| Case type | Prompt style | Graders |
|---|---|---|
| Routing/trigger | Realistic user phrasing that does not name the skill | `tool_used` (Skill fired) + `llm` (asks the right clarifying question / takes the right first step) |
| Advisory, no data | Conceptual or "how should we…" question | `llm` rubric: method correctness, labelled assumptions, actionable output |
| Analysis with data | Prompt plus a fixture CSV in `resources/` (via `case.yaml` `add_dirs`) | `regex` on key numbers + `llm` on interpretation + `tool_used` (script ran) |

Rubrics are concrete PASS/FAIL statements. Grade facts with `regex`, judgement with `llm`.

## 8. Checklist before opening a PR
- [ ] `python3 tools/sync_shared.py` run, no manual edits in `_shared/`
- [ ] `python3 tools/validate_repo.py` passes
- [ ] `python3 -m unittest discover tests` passes
- [ ] `claude plugin validate .` passes
- [ ] 3+ eval cases added; ran `claude plugin eval plugins/supply-chain-buddy --case '<skill>-*'` at least once
- [ ] Skill registered in `sc-buddy` routing table and README
