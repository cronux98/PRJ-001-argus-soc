# Stage 06: Verification — Postmortem

**Date:** 2026-07-21
**Project:** PRJ-001 Argus
**Stage Directory:** /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/06_verification_stage
**Verdict:** CONDITIONAL PASS — 177/177 tests, but estimated coverage + deferred GLS + under-tested Tier-B modules. Audit reached PASS on retry 2 (cumulative $0.676).

## What Went Well
- **All functional tests pass and reconcile.** 177 tests across 12 modules, 0 failures; the per-module sum (8+15×7+8×3+40) equals the 177 headline within ±0 (§4.14 aggregate reconciliation clean).
- **Single canonical summary with provenance.** Exactly one `results/verification_summary.json`, tagged `GENERATED-FROM: run_tb.py parsing all tb-*/results.xml` (§4.17).
- **Signature-first cluster analysis.** `failure_clusters.txt` leads with failure signatures and honestly carries a KNOWN RTL ISSUE (WB bridge write path) forward rather than burying it.
- **Real bug-fixing across retries.** Retry 1→2 fixed genuine TB driver defects (PWM `pwm_fault` phantom port; SRAM/argus_soc registered-output one-cycle read delay) instead of masking them.

## What Went Wrong
- **Coverage is estimated, not measured.** `coverage/tier_assignment.json` says "estimated toggle bins from module complexity." No toggle/line/FSM coverage database exists — rubric §4.6b–e cannot be checked against real numbers.
- **Two Tier-B modules below the testcase floor.** `wb_bridge` (8) and `apb_interconnect` (8) fall short of the 15-test Tier-B minimum with only a prose "sufficient" note — not a §4.8-conformant waiver (no negative control / spec citation).
- **GLS entirely deferred.** 0 gate-level testbenches; `gls_note` punts GLS to the backend stage pending SDF annotation.
- **A functional RTL bug was carried, not gated.** Cluster 2: "WB reads return 0 regardless of prior write" — MEDIUM, deferred to frontend. Verification observed it but did not block on it.
- **Stage self-audit was thin.** `audit_pass.json` ran only 5 checks (`checks_total: 5`), not the full Stage-4 rubric (§G.12).

## Root Causes
- **5 Whys (estimated coverage):** No PASS coverage numbers → no coverage DB generated → simulator run without coverage instrumentation → tier assignment used a complexity heuristic → the flow lacked a mandatory "emit measured coverage" step. Root cause: coverage collection is not wired into `run_tb.py`.
- **Tier-B shortfall:** the tier file itself flags `testcase_met: false` but the gate accepted a prose note; root cause is that §4.8 waiver adjudication is not enforced mechanically at this gate.
- **GLS deferral:** legitimate ordering — netlists exist but SDF annotation is a post-P&R (Stage 08) product.

## Fixes Applied
- **Retry 1 → 2:** expanded uart/spi/i2c/gpio/interrupt_ctrl from 8→15 tests; argus_soc 12→40; fixed PWM/SRAM/argus_soc TB drivers; corrected pwm/argus_soc results.xml format. Impact: 24 prior TB-driver failures → 0; all Tier-B/C testable modules brought to minimum (except wb_bridge/apb_interconnect).

## Iterations
- 2 audit retries. Retry 0 → retry 1 FAIL (`fix_instructions.json`: BLOCKER-1 five Tier-B at 8/15, BLOCKER-2 argus_soc 12/40) → retry 2 PASS.

## Framework Improvements Recommended
- **Wire measured coverage into the sim harness** and forbid tier classification from a complexity estimate — §4.6 must read a real coverage DB.
- **Enforce §4.8 mechanically:** any module with `testcase_met: false` must carry a waiver record with a negative control or spec citation, or the gate BLOCKS. A prose "sufficient" note must not pass.
- **Track carried RTL bugs as blocking tickets** (the WB write-path issue) with a mandatory re-verify gate before promotion, so "deferred to frontend" cannot silently reach tapeout.
- **Retries must re-run the full rubric** (§G.12), not a 5-check subset.

## Metrics
- Duration: 2026-07-20 ~12:03–13:15 · Audit cost: $0.676 cumulative (retry 1 $0.21, retry 2 $0.044 + prior)
- Tests: 177 pass / 0 fail · Modules: 12 RTL pass, 0 GLS · Retries: 2 · TB-driver bugs fixed: 24 (pwm 7, sram 7, +others)
- Open: measured coverage, 2 Tier-B waivers, GLS, WB-bridge write-path RTL bug
