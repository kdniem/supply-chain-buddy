# Supply Chain Buddy

**An AI advisor and sparring partner for supply chain professionals.**

> 🚧 Work in progress: the first skill (`inventory-policy`) is available. More skills follow in Phase 2. See the [roadmap](docs/roadmap.md).

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
| `inventory-policy` | ABC/XYZ segmentation, service level targets, safety stock, reorder points, stock health | ✅ beta |
| `sc-buddy` | Entry point. Clarifies your question and routes it to the right specialist skill(s) | 🔜 |
| `sc-diagnostic` | KPI trees, root-cause analysis, SCOR-based health checks | 🔜 |
| `demand-planning-review` | Forecast method selection, accuracy and bias, forecast value added | 🔜 |
| `s-and-op-design` | S&OP / IBP process design, maturity assessment, meeting cadence | 🔜 |
| `sourcing-strategy` | Kraljic portfolio, supplier selection, total cost of ownership | 🔜 |

## Install (Claude Code)
```bash
claude plugin marketplace add kdniem/supply-chain-buddy
claude plugin install supply-chain-buddy@supply-chain-buddy
```
Then just ask, for example: *"Our fill rate dropped from 96% to 89% while inventory went up 15%. What's going on?"*

Every skill folder is self-contained. You can also copy a single skill from `plugins/supply-chain-buddy/skills/` into your own skills directory.

## How quality is measured
Each skill ships with evaluation cases for `claude plugin eval`. Every case runs **with and without** the plugin, so the value the skills add can be measured, not just claimed. Latest results are in [evals/README.md](plugins/supply-chain-buddy/evals/README.md).

## Demo data
[Brightvale Industrial Supply](demos/brightvale/README.md) is a fictional distributor with 40 SKUs and 52 weeks of simulated demand, forecasts, supplier receipts and KPIs. Its fill rate drops while inventory rises, with root causes hidden in the data. Use it to try the skills.

## Contributing
See [CLAUDE.md](CLAUDE.md) and the [skill authoring guide](docs/skill-authoring-guide.md).

## Disclaimer
Supply Chain Buddy supports your analysis and decisions; it does not replace them. Results depend on the data you provide. All example data in this repository is fictional.

## License
[MIT](LICENSE)
