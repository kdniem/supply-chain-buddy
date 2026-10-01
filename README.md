# Supply Chain Buddy

**An AI advisor and sparring partner for supply chain professionals.**

> 🚧 Work in progress: the orchestrator `sc-buddy` and three specialist skills are available. `s-and-op-design` and `sourcing-strategy` follow. See the [roadmap](docs/roadmap.md).

Supply Chain Buddy turns Claude into a supply chain advisor. It does not answer from generic web knowledge. It works the way an experienced planner or consultant would:

1. **Frames the real question.** Which decision needs to be made, by whom, and by when?
2. **Asks for your data.** It tells you exactly which data it needs and why, and accepts what you have, from a rough estimate to a full CSV export.
3. **Applies established methods.** Safety stock theory, forecast accuracy metrics, S&OP process design, the Kraljic matrix, TCO, SCOR. Each method comes with its source.
4. **Shows its work.** Calculations run as transparent scripts, and assumptions are labelled as assumptions.
5. **Leaves the decision with you.** You get options, trade-offs and a recommendation, never a black box.

## Who it is for
Planners, buyers, analysts, supply chain managers and leaders, as well as students and researchers. It is designed for mid-sized to large organisations and is industry-agnostic.

## Skills
| Skill | What it helps with | Status |
|---|---|---|
| `sc-buddy` | Entry point. Frames your decision, keeps a case card, routes to the right specialist skill(s) in the right order and integrates their results | ✅ beta |
| `inventory-policy` | ABC/XYZ segmentation, service level targets, safety stock, reorder points, stock health | ✅ beta |
| `sc-diagnostic` | KPI trees, hypothesis-driven root-cause analysis, KPI bridges (rate vs. mix), SCOR-based health checks | ✅ beta |
| `demand-planning-review` | Forecast accuracy and bias, forecast value added of overrides, method backtests incl. intermittent demand | ✅ beta |
| `s-and-op-design` | S&OP / IBP process design, maturity assessment, meeting cadence | 🔜 |
| `sourcing-strategy` | Kraljic portfolio, supplier selection, total cost of ownership | 🔜 |

## Install (Claude Code)
```bash
claude plugin marketplace add kdniem/supply-chain-buddy
claude plugin install supply-chain-buddy@supply-chain-buddy
```
Then just ask, for example: *"Hey Supply Chain Buddy, our fill rate dropped from 96% to 88% while inventory went up 15%. What's going on?"*

Every skill folder is self-contained. You can also copy a single skill from `plugins/supply-chain-buddy/skills/` into your own skills directory.

## How quality is measured
Each skill ships with evaluation cases for `claude plugin eval`. Every case runs **with and without** the plugin, so the value the skills add can be measured, not just claimed. Latest results are in [evals/README.md](plugins/supply-chain-buddy/evals/README.md). Headline: with a smaller model (Claude Haiku 4.5), the plugin lifts the average score from **0.41 to 0.96** across 10 cases, including the flagship diagnosis.

## Demo data
[Brightvale Industrial Supply](demos/brightvale/README.md) is a fictional distributor with 40 SKUs and 52 weeks of simulated demand, forecasts, supplier receipts and KPIs. Its fill rate drops while inventory rises, with root causes hidden in the data. Use it to try the skills.

## Contributing
See [CLAUDE.md](CLAUDE.md) and the [skill authoring guide](docs/skill-authoring-guide.md).

## Disclaimer
Supply Chain Buddy supports your analysis and decisions; it does not replace them. Results depend on the data you provide. All example data in this repository is fictional.

## License
[MIT](LICENSE)
