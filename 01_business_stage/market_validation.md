---
cost:
  stage: "00_business_analysis"
  agent: "business-analyst"
  model: "deepseek-v4-pro"
  token:
    input: 0
    output: 0
    total: 0
  cost_usd:
    input: 0
    output: 0
    total: 0
  wall_clock: "0h 0m 0s"
  iterations: 1
  api_calls: 0
  model_pricing_ref: "~/hermes_workspace/config/model_pricing.yaml"
---

# Market Validation — PRJ-001 (Argus) v0

**STATUS: PASS**

## Validation Questions

| Question | Answer | Evidence |
|----------|--------|----------|
| **Gap exists?** | YES | No fully open-source (Apache-2.0/BSD) RISC-V environmental sensor-hub ASIC exists on sky130A with a complete, verified REUSE IP stack (Ibex + EF_UART + EF_SPI + EF_I2C + EF_GPIO8 + EF_TMR32 + OpenRAM). NEORV32 is FPGA-only; OpenTitan is security-focused; Caravel user projects are single-function. ST's $950M NXP sensor acquisition [https://www.embedded.com/stmicroelectronics-950m-mems-deal-a-strategic-reset-in-turbulent-times/] confirms the sensor hub market is strategic, yet open-source silicon has zero reference designs in this category. |
| **Technically feasible?** | YES | All required IP blocks exist as STRONG-tier REUSE candidates in IP-INDEX: lowrisc-ibex (100 MHz on sky130A proven), fossi-ef-uart, fossi-ef-spi, fossi-ef-i2c, fossi-ef-gpio8, fossi-ef-tmr32, vlsida-openram. OpenTitan EarlGrey proves Ibex + sky130A at 100 MHz [https://opentitan.org]. Caravel harness provides validated padframe, power, and clock infrastructure. Estimated area (0.5-2.0 mm²) fits comfortably in Caravel's 4.93 mm² user area. No new technology development required — this is an integration project. |
| **PPA achievable?** | YES | Targets within scaled baselines. Frequency: 50 MHz target with 25 MHz fallback — OpenTitan achieves 100 MHz on same process+core. Area: 0.5-2.0 mm² conservative vs. Caravel 4.93 mm² available. Power: 5-10 mW active aligns with MSP430FR2355 (2.9 mW at 24 MHz, 130nm) scaled for 32-bit vs 16-bit architecture. All values documented in baseline_metrics.json. |
| **IP available?** | YES (STRONG REUSE) | All 6 core peripherals available as STRONG-tier REUSE IP from FOSSi Efabless library (Apache-2.0). Ibex core: STRONG, Apache-2.0, SI=3, DFT=Y. OpenRAM: STRONG, BSD-3-Clause, SI=2. IP-INDEX confirms all blocks have config verification (Y) and low risk (LOW). CREATE items limited to: APB interconnect, APB↔Wishbone bridge, Caravel wrapper, top-level integration — all standard structural logic. |
| **Differentiated?** | YES | First open-source RISC-V environmental sensor-hub ASIC on silicon (sky130A). No prior design combines Ibex + all five EF_ peripherals + OpenRAM in a single tapeout. Provides: (1) silicon-proven baseline for open-source community, (2) audited STRONG-IP integration template, (3) Caravel user-project reference for Efabless MPW workflows, (4) published power measurements on sky130A sensor-hub — no prior open-source data exists in this category. The $950M ST+NXP sensor deal validates market interest; Argus serves the open-source research/education segment they don't address. |

## Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Ibex timing closure at 50 MHz on sky130A | Low | Medium | 25 MHz fallback defined. OpenTitan demonstrates 100 MHz with same core+process. Formal STA signoff. |
| OpenRAM SRAM macro generation for sky130A | Low | High | OpenRAM has documented sky130A support. Fallback: register-file-based SRAM (area penalty but functional). |
| APB↔Wishbone bridge bugs | Medium | Medium | Standalone bridge verification before integration. Caravel precheck catches protocol violations. |
| Multi-IP integration incompatibilities | Medium | Medium | All EF_ IP uses Wishbone B4 convention. Integration testbench with all IP instantiated before tapeout. |
| Power leakage higher than estimated | Low | Low | Power is optimization target, not functional gate. Mature sky130A process. |
| Caravel shuttle slot availability/cost | Low | Medium | Multiple providers (chipIgnite, Efabless, TinyTapeout). $50-$300 budget, $500 contingency. |
| Project scope creep (adding WON'T features) | Medium | Low | MoSCoW classification is contract. WON'T features explicitly excluded with rationale. Change control required to promote COULD→SHOULD. |

## Project Economics

| Item | Estimate | Source |
|------|----------|--------|
| sky130A MPW shuttle slot (Caravel) | $50-$300 | TinyTapeout/ChipIgnite academic pricing; Efabless chipIgnite program |
| PCB breakout board (JLCPCB, 4-layer) | $20-$50 | JLCPCB prototype pricing, 50×50 mm |
| BOM (sensors, passives, connectors) | $15-$30 | I2C sensor module ×3 ($2-5 each), passives, connectors |
| Total estimated prototyping cost | $85-$380 | Per-unit cost for first shuttle run |
| EDA tooling (OpenLane, Yosys, OpenROAD) | $0 | Fully open-source flow on GitHub CI |
| Firmware development (RISC-V GCC, OpenOCD) | $0 | Open-source toolchain |

**Note:** These are manufacturing/BOM costs for the physical chip and prototyping. Token/cost tracking for the design workflow is in the YAML header above.

## Handoff

- **Next stage:** Stage 1 — Specification & Planning (spec-product-engineer)
- **Mandatory inputs for next stage:**
  - `market_validation.md` (this file) — contains verdict, risk matrix, market context
  - `baseline_metrics.json` — PPA targets and feature baselines
  - `market_requirements.md` — MoSCoW classification with acceptance criteria
- **Optional reference inputs:**
  - `domain_report.md` — domain context and technical challenges
  - `competitive_analysis.md` — comparable products and gap analysis

## Verdict Rationale

**PASS — proceed to specification stage.**

Argus is a technically feasible integration project using proven STRONG-tier open-source IP. No new IP development is required. All PPA targets are within demonstrated baselines. The gap is real: no open-source RISC-V environmental sensor-hub ASIC exists on sky130A.

The risk profile is manageable: the primary risks (timing closure, multi-IP integration, bridge bugs) are standard ASIC integration challenges, not fundamental technology risks. All have defined mitigations with fallback paths.

The project serves a clear market need in the open-source silicon community: a reference design for environmental sensing that researchers and startups can fork and extend. Commercial sensor hubs (MSP430, STM32L0, EFM8) dominate the volume market; Argus serves the open-source research and education segment.

**Recommendation:** Proceed to Stage 1 (Specification & Planning). SPEC agent should define the memory map, interrupt routing, register maps for all peripherals, and the APB↔Wishbone bridge specification.
