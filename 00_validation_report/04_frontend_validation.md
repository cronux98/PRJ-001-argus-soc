# Validation Report — PRJ-001 (Argus) · Stage 04 Frontend / RTL

## 1. Run Summary

| Field | Value |
|-------|-------|
| Stage | 04_frontend_stage |
| Project | PRJ-001 (Argus) |
| Modules | 12 (uart, spi_master, i2c_master, gpio, pwm, sys_ctrl, interrupt_ctrl, apb_interconnect, wb_bridge, ibex_core, sram, argus_soc) |
| Auditor | Claude Code Opus 4.8 (--effort high) |
| Date | 2026-07-20 |
| Retry | 0 |
| Checks evaluated | 13 (11 mandatory Stage-3 + 1 provenance + 1 tooling-integrity) |
| Checks passed | 2 (3.1, 3.17) |
| Checks failed | 11 |
| **Verdict** | **FAIL** |
| Fixes generated | 12 |

## 2. Audit Checks

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 3.1 | RTL files exist for all modules | ✅ PASS | 12/12 have `rtl/*.v` |
| 3.2 | Lint log exists for every module | ❌ FAIL | 11/12; `rtl-argus_soc/logs/lint/` has no log |
| 3.3 | Lint is clean (0 errors) | ❌ FAIL | `pwm` PINNOTFOUND `WDT_RESET` (pwm_wrapper.v:76); `i2c_master` MODMISSING `i2c_master_wbs_16` (EF_I2C_APB.v:106); both `%Error: Exiting due to 1 error(s)` |
| 3.4 | Formal results exist for every module | ❌ FAIL | 0/12; all `logs/formal/` empty; no results.xml |
| 3.5 | Formal BMC depth ≥ 20 | ❌ FAIL | No formal data to parse |
| 3.6 | Synthesis log exists for every module | ❌ FAIL | 0 synth logs; netlists only 10/12 (ibex_core, spi_master missing) |
| 3.7 | Synthesis completed without error | ❌ FAIL | Unverifiable — empty glob (no synth logs) |
| 3.8 | Equivalence check PASS for every module | ❌ FAIL | 0/12; all `logs/equiv_check/` empty; no equiv.log |
| 3.9 / 3.16 | verify_frontend_artifacts.sh exists + exits 0 | ❌ FAIL | No verify script exists under the stage |
| 3.14 / G.5 | GENERATED-FROM banner on every log | ❌ FAIL | 0/11 lint logs carry banner |
| 3.15 | Evidence scaffold populated (lint/formal/synth/equiv) | ❌ FAIL | formal=0, equiv_check=0, synth-logs=0 files across all 12 |
| 3.17 | No PASS claim without tool output | ✅ PASS | Index tables empty / `[TBD]`; no verdict minted |
| INT-1 | assert_clean regex correctness (§G.3 tooling) | ❌ FAIL | `grep -ci "Error|ERROR"` = literal BRE → false PASS; masked 3.3 |
| 3.10/3.12 | AXI channel/crossbar (IP-011) | N/A | Argus is APB + Wishbone; no AXI fabric |
| 3.13 | SRAM blackbox in top (IP-011) | ✅ INFO | `argus_soc.v` references sram/blackbox 11× |
| G.1 | Upstream dispatch gate | ✅ PASS | `03_architecture_stage/audit/audit_pass.json` verdict PASS |

## 3. Findings

- **Scaffold-only delivery.** The declared pipeline (RTL → Lint → Sim → Formal → Synth → Equiv → GLS) halted after Lint. `logs/formal`, `logs/equiv_check`, and `logs/synth` are empty for all 12 modules. Only RTL, partial lint (11/12), and bare Yosys netlists (10/12) exist.
- **Lint is not clean.** `pwm` and `i2c_master` both terminate with fatal `%Error`. i2c's missing-module error is a filelist bug (`i2c_master_wbs_16.v` exists in `rtl/` but was not compiled); pwm's is a real port-name mismatch (`WDT_RESET`).
- **Inconsistent flow.** i2c_master and pwm produced netlists (12.8k / 13.7k lines) even though their lint failed — lint and synth ran on different filelists.
- **Top-level gaps.** `argus_soc` has no lint log; `ibex_core` and `spi_master` have no netlist.
- **No provenance.** Zero `GENERATED-FROM:` banners on any log/netlist.
- **No gate.** `verify_frontend_artifacts.sh` was never created or run.
- **Tooling integrity (INT-1).** Shared `assert_clean` uses `grep -ci` (basic regex) not `grep -Eci`; the rubric-specified `Error|ERROR` alternation matches nothing and silently PASSes. Cross-stage defect — escalate to Vera.
- Upstream architecture gate is valid (§G.1 satisfied).

## 4. Fixes Generated

See `audit/fix_instructions.json` for full executable detail. Summary:

| # | Check | Fix type | Description |
|---|-------|----------|-------------|
| 1 | 3.2 | STAGE_FIX | Lint argus_soc, capture log |
| 2 | 3.3 | RTL_FIX | Fix pwm `WDT_RESET` pin + add i2c filelist; re-lint clean |
| 3 | 3.4 | STAGE_FIX | Run formal BMC for 12 modules → results.xml |
| 4 | 3.5 | STAGE_FIX | Set BMC depth ≥ 20 in each harness |
| 5 | 3.6 | STAGE_FIX | Capture synth logs; synth ibex_core + spi_master |
| 6 | 3.7 | STAGE_FIX | assert_clean on new synth logs |
| 7 | 3.8 | STAGE_FIX | Run RTL↔netlist equivalence for 12 modules |
| 8 | 3.9/3.16 | SCRIPT_FIX | Author + run verify_frontend_artifacts.sh |
| 9 | 3.14 | STAGE_FIX | Add GENERATED-FROM banners to all logs |
| 10 | 3.15 | STAGE_FIX | Execute remaining pipeline to populate scaffold |
| 11 | INT-1 | SKILL_FIX | Patch assert_clean to `grep -Eci` — escalate to Vera |

## 5. Conditional Pass Items

None. `CONDITIONAL`/`PARTIAL` grades are prohibited (§G.8). Verdict is FAIL.

## 6. Cross-Validation

- §G.1 dispatch gating: upstream `03_architecture_stage/audit/audit_pass.json` = PASS ✅
- INT-1 is a cross-stage tooling defect affecting any prior stage that used pipe-alternation `assert_clean` clean-checks; flagged for Vera to re-verify Stages 01–03 clean-checks.

## 7. Final Verdict

**FAIL** — 11/13 checks failed. The frontend stage is incomplete (formal, equivalence, synthesis logging, and the verify gate are entirely absent) and contains two fatal lint errors. This is a structural incompleteness, not a tuning gap: the stage must re-run the Lint→Formal→Synth→Equiv pipeline to completion before it can gate.

## 8. Handoff to Next Stage

**BLOCKED.** Stage 05/06 (verification/integration) must not dispatch — no `audit_pass.json` was written. Rework required per `audit/fix_instructions.json`. On retry, the full rubric re-runs (§G.12), and INT-1 must be resolved so 3.3/3.7 clean-checks are trustworthy.
