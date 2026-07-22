# Stage 08: Backend (Physical Design) — Postmortem

**Date:** 2026-07-21
**Project:** PRJ-001 Argus
**Stage Directory:** /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/08_backend_stage
**Verdict:** CONDITIONAL PASS (v0-run9) — 7 P&R iterations. Setup +4.264 ns, hold +0.107 ns.

## What Went Well
- **The 169K-FF regression was found and fixed.** v0-run3 synthesized behavioral `sram.v` as 169,566 flip-flops; replacing it with a `(* blackbox *)` macro + wrapper LEF/GDS/LIB dropped synthesis to 14,123 cells (−91.7%). Post-P&R proof: `sequential_cell` = 3,498, `class:macro` = 1 (SRAM placed as macro, not FFs).
- **Timing genuinely closed at 25 MHz.** `timing__setup__ws` = +4.264, `timing__hold__ws` = +0.107, both vio counts 0 across all 9 corners — the 90 I/O hold violations from run7 (−0.846 ns) were fully closed.
- **Exemplary iteration log.** `PD_ITERATION_LOG.md` records all 7 runs and tags every number "FROM metrics.json"; the prose matches the metrics (slew 2,023; cap 17; LVS 66; route DRC 0). No §8.4 narrative-vs-metric violation — a model for other stages.
- **Root-caused the SDC/config mismatch.** v0-run5 abort was correctly diagnosed (PNR_SDC_FILE overrides config CLOCK_PERIOD; SDC still said `period 20.0`) and fixed in run6/7.

## What Went Wrong
- **Magic DRC (4,764,805) never addressed.** `magic__drc_error__count` = 4.76M is absent from `audit_pass.json`, which cites only route DRC (0) and KLayout (12). The `61-magic-drc` report shows met3.2/licon.1 violations near the SRAM-macro region — consistent with the abstract SRAM view, but undocumented and unwaived.
- **Self-audit (§G.16).** `auditor: "physical-design-agent (deepseek-v4-pro)"` — the stage graded itself; Vera-accepted, not independent.
- **Two expensive dead-end runs.** v0-run5 ABORTED (SDC mismatch) and v0-run8 TIMED OUT at stage 44 (14,403 s > 14,400 s session limit) produced no deliverable.
- **CONDITIONAL_PASS vocabulary** in the stage-owned JSON (§G.8), permitted only by explicit Vera acceptance.

## Root Causes
- **5 Whys (Magic DRC ignored):** audit reported DRC clean → it only read route+KLayout metrics → Magic DRC on an abstract-view macro produces millions of geometry errors that are "expected noise" → the auditor treated KLayout as the sole authoritative signoff → the rubric §7.7 magic-drc requirement was not mechanically enforced. Root cause: no gate that either evaluates or explicitly waives the magic-drc count against the blackbox abstract view.
- **v0-run8 timeout:** detailed routing wall-clock exceeded the session limit; no checkpoint/resume, so the whole run was lost.
- **v0-run5 abort:** SDC and config CLOCK_PERIOD were edited independently with no consistency check.

## Fixes Applied
- **SRAM blackbox** (run3→run4-r2): 169,566 → 14,123 synth cells (−91.7%); enabled P&R.
- **Clock relax** (run5→run6): CLOCK_PERIOD 20→40 ns (50→25 MHz) in *both* config.yaml and SDC; setup slack −4.66 → +3.27 ns.
- **I/O hold closure** (run7→run9): SDC min I/O delay 1.5→3.0 ns, hold uncertainty 0.15→0.30 ns; 90 hold vios → 0, hold WS −0.846 → +0.107 ns.
- **Slew/cap reduction** (run9): max_transition 1.5→1.0 ns; cap 147→17, slew 2,133→2,023, fanout 2→0.

## Iterations
- 7 runs: run3 FAIL (169K FF) → run4-r2 CONDITIONAL (blackbox, timing WIP) → run5 ABORT (SDC mismatch) → run6 WIP → run7 FAIL (hold −0.846) → run8 TIMEOUT → run9 CONDITIONAL PASS.

## Framework Improvements Recommended
- **Add a §7.7 magic-DRC gate** that requires the magic-drc count to be evaluated and, for blackbox/abstract macros, explicitly waived with the macro named — so a 4.76M count can never be silently omitted.
- **Enforce SDC↔config CLOCK_PERIOD consistency** with a pre-flight lint (would have prevented the run5 abort).
- **Checkpoint/resume long P&R runs** so a session-limit timeout (run8) doesn't discard hours of routing.
- **Independent re-gate (§G.16)** before tapeout; do not accept stage-agent self-audit as final.

## Metrics
- Duration: 2026-07-19 → 2026-07-21 across 7 runs · Wasted runs: 2 (run5 abort, run8 timeout)
- Final: setup +4.264 ns, hold +0.107 ns, route DRC 0, KLayout DRC 12, LVS 66 (waiver), slew 2,023 / cap 17 (ss-corner waivers), antenna 0
- Cells: 231,540 total (stdcell 32,838, fill 198,701, macro 1) · Util 45.9% · GDS 42.5 MB
