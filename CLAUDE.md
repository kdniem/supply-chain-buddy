# CLAUDE.md — working on the Supply Chain Buddy repository

This file guides AI agents (and humans) who **develop** this repository. It is not loaded by users of the plugin.

## What this repo is
Supply Chain Buddy is an open-source skillset that turns a general AI assistant into an advisor and sparring partner for supply chain professionals. One orchestrating skill (`sc-buddy`) frames the user's question and routes it to domain skills. Each domain skill applies established methods, asks the user for the data it needs, shows its math and cites sources.

Primary platform: Claude (Claude Code plugin + claude.ai skills). Portable by design: the skills follow the open Agent Skills format (`SKILL.md`), so they can be adapted later for Codex and Microsoft 365 Copilot.

## Layout
```
.claude-plugin/marketplace.json      # repo root is the marketplace
plugins/supply-chain-buddy/          # the plugin (what users install)
  .claude-plugin/plugin.json
  skills/<skill>/SKILL.md            # one folder per skill (+ references/, templates/, scripts/)
  evals/<case>/                      # claude plugin eval cases
shared/                              # SOURCE OF TRUTH for cross-skill content
templates/                           # skeletons for new skills and eval cases
tools/                               # sync + validation scripts
tests/                               # unit tests for skill scripts and tools
docs/                                # ADRs, authoring guide, roadmap
demos/                               # showcase scenarios with fictional data
```

## Rules
1. **Read `docs/skill-authoring-guide.md` before creating or changing a skill.** Every skill follows that anatomy.
2. **Never edit files under `skills/*/references/_shared/`.** They are generated. Edit `shared/` and run `python3 tools/sync_shared.py`.
3. Skills must be **self-contained**: a skill folder copied on its own must still work. Reference only files inside the skill folder.
4. Scripts: Python 3.9+, **standard library only**, CSV in → Markdown/JSON out, deterministic, with unit tests in `tests/`. Every script needs a documented manual fallback in the SKILL.md.
5. Content language is **English**. Use the terms defined in `shared/kpi-glossary.md`.
6. Cite methods using `shared/methods-library.md`. Never invent sources, benchmarks or statistics. If a number is a rule of thumb, label it as one.
7. All demo and eval data is **fictional**. Never add real company data, names or confidential material.
8. Keep `SKILL.md` under 300 lines; move depth into `references/`.

## Commands
```bash
python3 tools/sync_shared.py            # copy shared/ into each skill's references/_shared/
python3 tools/validate_repo.py          # structure, frontmatter, sync and length checks
python3 -m unittest discover tests      # script tests
claude plugin validate .                # marketplace + plugin manifest checks
(cd plugins/supply-chain-buddy && claude plugin eval . --scaffold --allow-tools Bash Write)   # behavioural evals (costs model usage)
```
Run the first four before every commit.

## Definition of done for a skill
- SKILL.md follows the template and passes `validate_repo.py`
- Data requirements table (minimum vs. ideal) present
- At least 3 eval cases: trigger/routing, advisory without data, analysis with data
- Scripts (if any) have unit tests and a manual fallback
- Listed in the routing table of `sc-buddy` and in `README.md`
