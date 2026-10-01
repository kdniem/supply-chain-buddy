---
type: llm
---

Reference root causes (fictional Brightvale data): (1) supplier SUP-03's actual lead time roughly doubled (≈13-16 → ≈32-34 days) while the ERP still plans with 14 days; SUP-03 items (bearings, shaft seal, proximity sensor) explain essentially all of the fill-rate drop (SUP-03 fill rate ≈99% → ≈63%). (2) Inventory increase comes mainly from hydraulics/HYDR (safety stock raised for a customer project that did not materialise; sales forecast uplift), fasteners/FAST (supplier SUP-05 tripled minimum order quantities) and pneumatics/PNEU (demand fell by about a third, forecast/parameters not adjusted), partly offset by lower bearing (SUP-03) stock. (3) Safety stock is a flat ~0.5 weeks of demand for most items.

PASS only if ALL of the following hold:
1. Identifies SUP-03's lead time increase (actual lead times well above the 14 days in the ERP) as the main driver of the fill-rate drop, with supporting numbers.
2. Explains the inventory increase with at least TWO of: HYDR project/safety stock or forecast uplift; SUP-05/fastener MOQ or order-quantity increase; PNEU demand decline without parameter/forecast adjustment.
3. Treats service and inventory as (largely) separate problems / misallocation, and does NOT recommend raising safety stock across the board.
4. Recommends concrete actions including updating lead time master data (or addressing SUP-03), and at least one structural fix (e.g. statistical/segmented safety stock, parameter or lead-time review process, override/forecast governance).

FAIL if SUP-03 is not identified as the main service driver.
