# Stage 08: Backend (Physical Design) — Validation Report

**Date:** 2026-07-21
**Auditor:** Claude Opus 4.8 (high effort)
**Project:** PRJ-001 Argus
**Stage Directory:** /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/08_backend_stage
**Run tag:** v0-run9

## Verdict
**CONDITIONAL PASS** — timing closed at 25 MHz with positive setup/hold margin; documented corner/blackbox waivers; one unaddressed signoff metric (Magic DRC) flagged.

## Checklist

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 8.1 | GDS exists (>40MB) | PASS | `results/gds/argus_soc.klayout.gds` 42.5 MB; `argus_soc.gds` 42.4 MB |
| 8.2 | LEF exists | PASS | `results/librelane/lef/argus_soc.lef` |
| 8.3 | metrics.json exists | PASS | `results/librelane/metrics.json` (= v0-run9/final/metrics.json) |
| 8.4a | Setup WNS ≥ 0 | PASS | `timing__setup__ws` = +4.264 ns; `timing__setup_vio__count` = 0 (all 9 corners) |
| 8.4b | Hold WNS ≥ 0 | PASS | `timing__hold__ws` = +0.107 ns; `timing__hold_vio__count` = 0 (fixed from −0.846/90 vios) |
| 8.5a | Routing DRC = 0 | PASS | `route__drc_errors` = 0 |
| 8.5b | KLayout DRC minor only | PASS (waiver) | `klayout__drc_error__count` = 12 (m4.2 dominant) |
| 8.5c | Magic DRC | **FLAG** | `magic__drc_error__count` = 4,764,805 — not cited or waived in audit_pass.json |
| 8.6 | LVS errors documented as blackbox waivers | PASS (waiver) | `design__lvs_error__count` = 66; report "Top level cell failed pin matching," device classes equivalent → SRAM blackbox pin mismatch |
| 8.7 | PD_ITERATION_LOG records all runs | PASS | 7 runs logged: v0-run3, run4-r2, run5, run6, run7, run8, run9 |
| 8.8 | SRAM blackbox (~cells, NOT 169K) | PASS | `sequential_cell` = 3,498; `class:macro` = 1; stdcell = 32,838 (behavioral SRAM would be ~169K FF — run3 bug fixed) |
| 8.9 | Final frequency achieved | PASS | 40 ns / 25 MHz clock; setup closed at ss_100C_1v60 |
| 8.10 | audit_pass.json exists | PASS | `audit/audit_pass.json` verdict CONDITIONAL_PASS, 14 pass / 4 conditional / 1 fail |

## Key Metrics
- **Setup WS:** +4.264 ns · **Hold WS:** +0.107 ns · setup/hold vios: 0 / 0
- **Antenna:** 0 violating nets/pins · **Fanout:** 0 · **Slew:** 2,023 (ss corner) · **Cap:** 17 (ss corner)
- **Instances:** 231,540 total (fill_cell 198,701; stdcell 32,838; macro 1) → non-fill ≈ 32.8K
- **Utilization:** 45.9% (`design__instance__utilization`) — within 30–80%
- **DRC:** route 0 · KLayout 12 · Magic 4,764,805 · **LVS:** 66 errors

## Prose ↔ Metrics Integrity (§8.4 / narrative-match)
`PD_ITERATION_LOG.md` is **compliant**: every numeric claim is tagged "FROM metrics.json" and matches (slew 2,023; cap 17; fanout 0; LVS 66; route DRC 0; setup +4.264; hold +0.107). No "clean/NONE/zero" prose contradicts a non-zero metric. Narrative integrity **PASS**.

## Issues Found
1. **Magic DRC not addressed (primary finding).** `magic__drc_error__count` = **4,764,805**. The audit cites only route DRC (0) and KLayout (12) and does not mention Magic DRC. The report (`61-magic-drc`) shows met3.2 spacing + licon.1 width violations concentrated near the SRAM-macro/die region (coords ~850–1099 µm) — consistent with the abstract SRAM view, but this is not documented or waived. Rubric §7.7 requires the magic-drc report be evaluated.
2. **Auditor independence (§G.16).** `auditor: "physical-design-agent (deepseek-v4-pro)"` — the stage agent audited itself. Vera-accepted, but not an independent gate.
3. **CONDITIONAL_PASS vocabulary.** The stage-owned JSON uses `CONDITIONAL_PASS`, which §G.8 restricts to PASS/FAIL/BLOCKED; permitted here only because Vera explicitly accepted it.

## Waivers (all `waiver_expiry: tapeout`)
- **LVS 66** — SRAM blackbox macro, 41 unmatched pins (abstract LEF). BLACKBOX_MACRO. Real OpenRAM GDS integrated at tapeout.
- **KLayout DRC 12** — minor metal spacing (m4.2), < 100-minor MPW acceptance. MINOR_DRC.
- **Slew 2,023** — ss_100C_1v60 corner only (other corners 31–44). CORNER_SPECIFIC.
- **Cap 17** — ss_100C_1v60 only; reduced from 147 by max_transition 1.5→1.0 ns. CORNER_SPECIFIC.

## Decision
**CONDITIONAL PASS** — setup/hold timing is closed at 25 MHz with genuine positive margin, the 169K-FF behavioral-SRAM regression is fixed and proven (3,498 seq cells / 1 macro), and the iteration log's prose is honestly sourced. Sign-off is conditioned on (a) explicitly evaluating/waiving the 4.76M Magic DRC count against the SRAM abstract view and (b) an independent re-gate to satisfy §G.16.
