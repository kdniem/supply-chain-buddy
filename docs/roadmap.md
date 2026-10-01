# Roadmap

| Phase | Scope | Status |
|---|---|---|
| 0 Discovery | Goals, audience, scope, architecture direction | ✅ Done |
| 1 Foundation | Repo skeleton, marketplace/plugin manifests, shared layer (principles, data intake, output standards, KPI glossary, methods library), skill and eval templates, tooling, CI | ✅ Done |
| 2 MVP | `sc-buddy` orchestrator + 5 domain skills, their scripts and evals, 2–3 demo scenarios | 🔄 In progress (3/6 skills: inventory-policy, demand-planning-review, sc-diagnostic) |
| 3 Showcase | Demo walkthroughs, eval results (with vs. without plugin), polished README, launch material | ⏳ |
| 4 Expansion | Additional skills (see below), community feedback | ⏳ |
| 5 Portability | Adapters for Codex and Microsoft 365 Copilot | ⏳ |

## MVP skills (Phase 2)
1. `sc-buddy`: orchestrator and routing
2. `sc-diagnostic`: KPI tree, root-cause analysis, SCOR-based health check ✅
3. `inventory-policy`: ABC/XYZ, safety stock, reorder point, service level ✅
4. `demand-planning-review`: method selection, accuracy, bias, FVA ✅
5. `s-and-op-design`: process design, maturity, meeting cadence
6. `sourcing-strategy`: Kraljic, supplier selection, TCO

**Flagship demo:** *"Our fill rate dropped from 96% to 89% while inventory went up 15%. What's going on?"* The demo runs sc-buddy → sc-diagnostic → data request → demand-planning-review and inventory-policy → executive brief.

## Expansion backlog (Phase 4, unprioritised)
Capacity planning / RCCP · supply planning and MRP parameters · network and location strategy · transport modes and Incoterms · warehouse KPIs and layout · supplier risk and resilience · negotiation preparation · RFQ/tender design · supply chain strategy and segmentation · business case · planning software selection (APS/IBP) · regulation (CSDDD, CBAM, EUDR) · Scope 3 basics · scenario analysis · change and stakeholder communication · decision-to-AI delegation
