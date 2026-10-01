# ADR 0001: Architecture of Supply Chain Buddy

- Status: Accepted
- Date: 2026-10-01

## Context
We are building an open-source showcase: an AI advisor for supply chain roles. Requirements:

- **Advisor and sparring partner**, not an execution tool. No system access. The user provides data, and the advisor asks for it actively.
- **One entry point** that routes questions to domain skills.
- **Methods grounded** in academic literature and practitioner standards.
- **English** content. Industry-agnostic, mid-size to enterprise context.
- **Lead platform is Claude.** Codex and Microsoft 365 Copilot follow later.
- Distribution as a GitHub repo and plugin marketplace. **Individual skills must be shareable on their own.**
- Success is measured by convincing use-case demonstrations.

Reference point: `kishorkukreja/awesome-supply-chain` has 133 broad, monolithic skills with no orchestration, no data-intake protocol, no evals and no citations. Its `supply-chain-decision-to-delegation` skill shows the anatomy we want: an operating contract, session modes, `references/` and output templates.

## Decisions

### D1: Repository is a marketplace, and the plugin lives in a subfolder
The root `.claude-plugin/marketplace.json` lists one plugin at `plugins/supply-chain-buddy/`.
*Why:* Development files (CLAUDE.md, tools, tests, docs) stay out of what users install. `claude plugin validate` warns about a CLAUDE.md at the plugin root. The setup also leaves room for further plugins later, such as a vertical pack.

### D2: The orchestrator is a skill, not a subagent
`sc-buddy` is implemented as a skill that runs in the main conversation.
*Why:* An advisor has to hold a dialogue: clarify, request data, iterate. In Claude Code, subagents run in isolation and return one result, so they cannot ask the user questions mid-task. Skills also work in claude.ai, Claude Desktop and Codex, while subagents are specific to Claude Code.
*Consequence:* Domain skills hand off to each other through explicit "handoff" sections. `sc-buddy` keeps a lightweight case summary in the conversation (question, decision, data received, assumptions) so the case stays coherent across skills. A Claude Code subagent may be added later for well-bounded, non-interactive jobs, for example a "data quality check" that runs over a provided file.

### D3: Shared content has a single source and is synced into each skill
Cross-cutting content lives in `/shared` and is copied into `skills/<skill>/references/_shared/` by `tools/sync_shared.py`. CI fails if the copies drift.
Shared content covers operating principles, data intake, output standards, the KPI glossary and the methods library.
*Why:* Skills must be self-contained to be shareable one by one. At the same time, one source of truth prevents contradictions between skills.
*Trade-off:* The repository contains duplicated text. This is accepted, because the copies are generated and never edited by hand.

### D4: Deterministic calculations run in Python scripts, with a manual fallback
Quantitative steps such as safety stock, ABC/XYZ classification and forecast error metrics run in scripts under `skills/<skill>/scripts/`. The scripts use only the Python 3.9+ standard library, take CSV input and print Markdown and JSON.
*Why:* Language models should not do arithmetic over many rows in their head. Scripts make results reproducible and auditable, which matters for a showcase. Using only the standard library means nothing has to be installed in any sandbox.
*Fallback:* Every SKILL.md documents the formula and a manual procedure for environments without code execution, such as some Copilot surfaces. In that case the advisor shows the step-by-step calculation for a small sample and states its limits.

### D5: Evals use Claude Code's native plugin eval format
Cases live in `plugins/supply-chain-buddy/evals/<case>/` with `prompt.md` and `graders/*.md`. They run with `claude plugin eval`.
*Why:* The runner compares results **with and without** the plugin (Δ). This is exactly the evidence a showcase needs. It also gives regression protection when skills or models change.
*Minimum:* three cases per skill (routing/trigger, advisory without data, analysis with data).

### D6: Portability through the open skill format and thin adapters
The skills follow the Agent Skills `SKILL.md` format and avoid platform-specific syntax in their bodies. The only exception is the documented `${CLAUDE_SKILL_DIR}` path hint for scripts, which comes with a relative-path fallback. Adapters for Codex and M365 Copilot will live under `adapters/` (Phase 5) once platform support has been verified.

### D7: Fictional data only
All demos and eval fixtures use fictional companies and synthetic data. This avoids any employer or client IP and keeps the repo safe to share publicly.

## Consequences
- Adding a skill means: copy `templates/skill/`, fill it in, sync shared content, add 3+ eval cases, and register the skill in the `sc-buddy` routing table.
- The quality bar is enforced by `tools/validate_repo.py` and CI, and behavioural quality by evals.
