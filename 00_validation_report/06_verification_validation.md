# Stage 06: Verification — Validation Report

**Date:** 2026-07-21
**Auditor:** Claude Opus 4.8 (high effort)
**Project:** PRJ-001 Argus
**Stage Directory:** /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/06_verification_stage

## Verdict
**CONDITIONAL PASS** — all 177 functional tests pass and reconcile, but coverage is *estimated* (not measured), GLS is deferred, and two Tier-B modules sit below the testcase minimum on prose-only justification.

## Checklist

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 6.1 | TB dir per module | PASS | 12 `tb-*/` dirs (uart, spi_master, i2c_master, gpio, pwm, sram, sys_ctrl, interrupt_ctrl, apb_interconnect, wb_bridge, ibex_core, argus_soc) |
| 6.2 | results.xml per TB, 0 failures | PASS | 12/12 `results.xml`; grep `<failure` = 0 in all 12 |
| 6.2b | Testcase count by tier | **CONDITIONAL** | Tier B `wb_bridge`=8 & `apb_interconnect`=8 (min 15) — prose waiver only, no formal waiver record. `ibex_core`=8 with ISA-citation waiver (valid). `argus_soc`=40 (Tier C, meets min) |
| 6.3 | Coverage metrics | **CONDITIONAL** | Only `coverage/tier_assignment.json` — "estimated toggle bins from module complexity". No measured toggle%/line%/FSM data |
| 6.4 | GLS testbenches exist | **FAIL (deferred)** | 0 `tb-*-gls`; `verification_summary.json` gls_note: "GLS pending … Deferred to 08_backend_stage" |
| 6.5 | Self-checking tests | PASS | `apb_driver.py` scoreboard/driver; cocotb assertions in `test_*.py` |
| 6.6 | Waveform dumps for failing tests | N/A | 0 failing tests → no dumps required; none present |
| 6.7 | audit_pass.json / fix_instructions.json | PASS | `audit/audit_pass.json` verdict PASS (retry 2, 5/5); `audit/fix_instructions.json` (retry 1) records prior FAIL |

## Key Metrics
- **Total tests:** 177 pass / 0 fail (`results/verification_summary.json`)
- **Per-module reconciliation (±0):** 8+15+15+15+15+15+15+15+8+8+8+40 = 177 ✓ matches headline
- **Modules:** 12 RTL pass / 12; GLS 0 pass / 0 (deferred)
- **Simulator:** icarus (oss-cad-suite 14.0), cocotb 2.1.0.dev0
- **Audit cost:** $0.676 cumulative across retries 0–2

## Issues Found
1. **Coverage is estimated, not measured.** `tier_assignment.json` explicitly says "estimated toggle bins from module complexity." No toggle/line/FSM coverage database exists, so rubric §4.6b–e cannot be verified against real numbers.
2. **Two Tier-B modules below testcase minimum.** `wb_bridge` (8) and `apb_interconnect` (8) fall short of the Tier-B minimum of 15 (§4.2b). The tier file records `testcase_met: false` with a prose note ("simple bridge/interconnect; N directed tests sufficient") — this is not an adjudicated waiver with a negative control or spec citation (§4.8).
3. **GLS entirely absent.** No gate-level sim; deferred to backend pending SDF annotation. Rubric §4.7 (GLS if frontend done) is unsatisfied at this stage.
4. **Known RTL defect carried forward.** `failure_clusters.txt` Cluster 2: "WB bridge write-path limitation — WB reads return 0 regardless of prior write." Flagged MEDIUM, deferred to frontend — a real functional bug that verification did not gate on.
5. **Stage self-audit ran only 5 checks** (`checks_total: 5`), not the full Stage-4 rubric (§G.12 full-rubric-on-retry not met).

## Waivers
- `ibex_core` 8 tests — ISA-compliance citation (lowRISC upstream RV32I suite) per §4.2b. **Valid.**
- `wb_bridge` / `apb_interconnect` 8 tests — prose "sufficient" note. **Not a rubric-conformant waiver** (no negative control / spec citation). Flagged as condition.

## Decision
**CONDITIONAL PASS** — functional correctness is strong (177/177, clean reconciliation, honest cluster analysis) and the stage self-gated PASS, but sign-off is conditioned on: (a) measured coverage replacing estimates, (b) formal §4.8-conformant waivers for the two under-tested Tier-B modules, (c) the deferred GLS being completed in backend, and (d) tracking the WB-bridge write-path RTL bug to closure.
