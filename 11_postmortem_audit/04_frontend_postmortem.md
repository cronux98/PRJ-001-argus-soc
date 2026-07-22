# Postmortem Report — 04_frontend_stage (RTL/Frontend)

**Project:** PRJ-001 (Argus)
**Stage:** 04_frontend_stage
**Auditor:** Claude Code Opus 4.8 (Final: Claude Code Fable 5)
**Date:** 2026-07-20
**Status:** FINAL

---

## 1. Executive Summary

> The Stage-3 frontend audit for Argus returned **FAIL** (11/13 checks). The stage is a scaffold-only delivery: the RTL→Lint→Sim→Formal→Synth→Equiv→GLS pipeline halted after Lint, so `logs/formal`, `logs/equiv_check`, and `logs/synth` are empty for all 12 modules, no verify gate exists, and two modules (pwm, i2c_master) carry fatal `%Error` lint failures. The single most important takeaway: the audit also uncovered a **cross-stage tooling defect (INT-1)** — `assert_clean` uses `grep -ci` instead of `grep -Eci`, so any `A|B` clean-check silently false-PASSes. That bug initially masked the lint failures and must be patched before any clean-check verdict in this project can be trusted.

---

## 2. Stage Context

| Field | Value |
|-------|-------|
| Stage name | 04_frontend_stage |
| Input artifact(s) | 03_architecture_stage (audit_pass.json = PASS) |
| Output artifact(s) | rtl-*/rtl/*.v (12), 11 lint logs, 10 netlists — no formal/equiv/synth logs |
| Agent(s) involved | Frontend/RTL stage agent |
| Skills dispatched | asic-workflow frontend pipeline (partial) |
| Wall-clock duration | Unknown (no cost/telemetry artifact in stage) |
| API cost (USD) | Unknown (not recorded) |
| Iterations / retries | Audit retry 0 |
| Final verdict | **FAIL** |

---

## 3. Timeline of Key Events

| Timestamp (UTC) | Event | Impact |
|-----------------|-------|--------|
| 2026-07-20 01:55 | Index scaffolds written (`00_frontend_index.md`, `00_rtl_index.md`) with empty tables / [TBD] | Stage started but never populated indexes |
| 2026-07-20 (lint) | Verilator run on 11/12 modules; pwm + i2c_master exit with `%Error` | Lint stage incomplete + failing |
| 2026-07-20 (synth) | Yosys produced 10/12 netlists (incl. failing pwm/i2c; not ibex/spi) | Synth ran on inconsistent filelist; no logs captured |
| — | Formal, Equivalence, Sim, verify gate never executed | Pipeline halted; empty scaffolds |
| 2026-07-20 06:33 | Audit invoked; empty `audit/claude_run_vera.log` present | Audit run |

---

## 4. What Went Well

### 4.1 Upstream gating held
- **Finding:** `03_architecture_stage/audit/audit_pass.json` exists with `verdict: PASS`; the frontend stage was legitimately dispatched (§G.1).
- **Why it mattered:** No MISSING_STAGE escalation needed for the input side.
- **Preserve:** Dispatch-gate check is cheap and correctly ordered.

### 4.2 RTL sources are complete and organized
- **Finding:** All 12 modules have `rtl/*.v`; hierarchical peripherals (EF_* IP) present.
- **Why it mattered:** Rework needs only pipeline execution, not RTL authoring, for 10/12 modules.
- **Preserve:** `rtl-<module>/{rtl,logs/<step>,synth}` layout is clean and auditable.

### 4.3 Honest scaffold, no minted verdict
- **Finding:** Indexes left as empty tables / `[TBD]`; no PASS claimed without evidence (3.17 PASS, §G.6 honest-stub norm respected).
- **Preserve:** Not fabricating a verdict is the correct failure mode.

---

## 5. What Went Wrong

### 5.1 Pipeline halted after Lint — formal/equiv/synth-logs empty (umbrella)

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| First observed | Audit, 2026-07-20 |
| Duration | Open — requires rework |
| Impact | Stage cannot gate; 3.4, 3.5, 3.6, 3.7, 3.8, 3.15 all FAIL |

- **Symptom:** `find rtl-*/logs/{formal,equiv_check,synth} -type f` = 0 for all three, across all 12 modules. No results.xml, no equiv.log, no synth transcript.
- **Root Cause (5 Whys):**
  1. Why? → The formal, equivalence, and synth-logging steps never ran.
  2. Why? → The stage agent stopped after lint (and a partial, un-logged synth).
  3. Why? → No gate (`verify_frontend_artifacts.sh`) forced completion before hand-off.
  4. Why? → The stage lacked a completion interlock tying scaffold-population to exit.
  5. Why? → Frontend flow treats scaffold creation as progress; there is no "empty-glob = FAIL" self-check inside the stage.
- **Fix Applied:** None (read-only audit). Fixes 3.4/3.6/3.8/3.9/3.15 in `fix_instructions.json`.
- **Was this fix propagated?** Proposed as a stage-internal verify gate (Preventive Measure P-1).

### 5.2 Two fatal lint errors reached the audit undetected

| Field | Value |
|-------|-------|
| Severity | HIGH |
| First observed | Audit |
| Duration | Open |
| Impact | 3.3 FAIL; pwm + i2c_master not lint-clean |

- **Symptom:** `pwm_verilator.log:38` `%Error-PINNOTFOUND: pwm_wrapper.v:76:10: Pin not found: 'WDT_RESET'`; `i2c_master_verilator.log:355` `%Error-MODMISSING: EF_I2C_APB.v:106:3: Cannot find module 'i2c_master_wbs_16'` (the file exists in `rtl/` but was off the filelist). Both `%Error: Exiting due to 1 error(s)`.
- **Root Cause (5 Whys):**
  1. Why not caught? → The stage had no working clean-check; the auditor's first `assert_clean` returned false PASS.
  2. Why false PASS? → `assert_clean` greps with `grep -ci` (BRE), so `Error|ERROR` matched the literal string, not the alternation.
  3. Why did the errors exist? → pwm has a real port-name mismatch; i2c had an incomplete compile filelist.
  4. Why inconsistent? → Lint and synth used different filelists (netlists were produced for both failing modules).
  5. Why? → No single source-of-truth filelist per module shared across lint/synth/formal/equiv.
- **Fix Applied:** None (audit). Fix 3.3 (RTL_FIX) + INT-1 (SKILL_FIX).
- **Was this fix propagated?** INT-1 escalated to Vera for shared-library patch.

### 5.3 Missing artifacts: argus_soc lint, ibex_core/spi_master netlists, all provenance banners

| Field | Value |
|-------|-------|
| Severity | HIGH |
| First observed | Audit |
| Impact | 3.2, 3.6, 3.14 FAIL |

- **Symptom:** `rtl-argus_soc/logs/lint/` empty (11/12 lint); no `ibex_core_netlist.v` / `spi_master_netlist.v` (10/12 synth); 0/11 lint logs carry `GENERATED-FROM:`.
- **Root Cause:** Top-level and two leaf modules were skipped by their respective steps; provenance banners were never part of the generator templates.
- **Fix Applied:** None (audit). Fixes 3.2, 3.6, 3.14.

---

## 6. Where We Got Lucky

- **Near-miss:** The `assert_clean` false-PASS almost certified pwm/i2c lint as clean.
  - **Why it didn't escalate:** The auditor cross-checked with a raw `grep -c 'error'` per file, saw non-zero counts, and inspected context (`%Error`).
  - **What would have happened if it did:** A failing-lint design would have been graded lint-clean; combined with the missing formal/equiv, a broken RTL set could have advanced.
  - **Preventive action:** Patch `assert_clean` to `grep -Eci` (INT-1) and never rely on a single assert without a raw-count sanity cross-check.

---

## 7. Metrics & Data

| Metric | This Stage | Source |
|--------|-----------|--------|
| Modules | 12 | task spec + `rtl-*/` dirs |
| RTL present | 12/12 | `find rtl-*/rtl/*.v` |
| Lint logs | 11/12 | `find */logs/lint/*.log` |
| Lint fatal errors | 2 modules (pwm, i2c_master), 2 `%Error` each | `grep -E 'Error' *.log` |
| Formal results.xml | 0/12 | `find -name results.xml` |
| Equiv logs | 0/12 | `find -name equiv.log` |
| Synth logs | 0/12 | `find */logs/synth/*` |
| Netlists | 10/12 (no ibex_core, spi_master) | `find -name '*_netlist.v'` |
| Provenance banners | 0/11 logs | `grep -L 'GENERATED-FROM:'` |
| verify gate | absent | `find -name 'verify*artifacts.sh'` |
| Checks failed | 11/13 | this audit |

---

## 8. Agent Performance Review

| Agent | Role | Autonomy Score (1-5) | Hallucinations | Escalations | Notes |
|-------|------|---------------------|----------------|-------------|-------|
| Frontend/RTL stage agent | Run RTL pipeline | 2 | 0 (no fabricated evidence) | 0 (should have self-blocked) | Delivered RTL + partial lint + bare netlists; stopped before formal/equiv/synth-logging; produced netlists for lint-failing modules |

---

## 9. Hallucination Incidents

| Incident | Agent | Category | Sub-Category | Diagnostic Code | Resolution |
|----------|-------|----------|--------------|-----------------|------------|
| None from stage agent — it did not fabricate evidence; it under-delivered honestly | — | — | — | — | N/A |
| INT-1 auditor-tooling false-PASS (not an agent hallucination but an evidence-integrity risk) | assert_clean | Tooling / evidence-integrity | Regex-alternation false negative | INT-1 | Escalated SKILL_FIX to Vera |

---

## 10. Lessons Learned

| # | Lesson | Category | Applies To | Priority |
|---|--------|----------|------------|----------|
| 1 | `assert_clean` must use `grep -Eci`; `A|B` patterns silently false-PASS under BRE | SCRIPT / TOOL | ALL stages (3.3, 3.7, DRC, LVS) | P0 |
| 2 | Empty scaffold dirs are not evidence — every count-check needs `assert_files min_count=1` first | SKILL / FLOW | ALL stages | P0 |
| 3 | Lint and synth (and formal/equiv) must share one per-module filelist | FLOW | Stage 3 | P1 |
| 4 | Stage must run its own verify gate before hand-off, not rely on the auditor | FLOW | Stage 3 | P1 |
| 5 | Provenance banners must be baked into log/netlist generators, not added later | SCRIPT | ALL stages | P2 |

---

## 11. Action Items

| # | Action | Owner | Verification | Status |
|---|--------|-------|--------------|--------|
| 1 | Patch `assert_clean` to `grep -Eci` | Vera | `assert_clean` FAILs on a file containing `%Error` | OPEN |
| 2 | Run formal BMC (depth ≥20) for 12 modules → results.xml | Frontend agent | `find -name results.xml | wc -l` = 12 | OPEN |
| 3 | Run RTL↔netlist equivalence for 12 modules | Frontend agent | 12 equiv logs contain "Equivalence successfully proven!" | OPEN |
| 4 | Capture synth logs; synth ibex_core + spi_master | Frontend agent | 12 synth logs + 12 netlists | OPEN |
| 5 | Fix pwm `WDT_RESET` pin + i2c filelist; re-lint clean | RTL agent | 0 `%Error` across 12 lint logs | OPEN |
| 6 | Lint argus_soc top | Frontend agent | argus_soc lint log present | OPEN |
| 7 | Author + run `verify_frontend_artifacts.sh` | Frontend agent | exit 0 recorded | OPEN |
| 8 | Add GENERATED-FROM banners to all logs/netlists | Frontend agent | `grep -L 'GENERATED-FROM:'` empty | OPEN |

---

## 12. Preventive Measures

| # | Measure | Type | Affected Skill/Script | Implementation Scope |
|---|---------|------|----------------------|---------------------|
| 1 | Stage-internal verify gate that fails on any empty `logs/<step>/` before hand-off | FLOW_CHANGE | frontend skill | All Stage-3 runs |
| 2 | `assert_clean` extended-regex fix | SCRIPT_UPDATE | evidence-assertions.sh | ALL stages, all projects |
| 3 | Single per-module filelist consumed by lint/formal/synth/equiv | SCRIPT_UPDATE | frontend skill | Stage 3 |
| 4 | Generator emits `GENERATED-FROM:` banner as line 1 of every log | SCRIPT_UPDATE | all tool wrappers | ALL stages |

---

## 13. Flow Improvement Proposals

| Proposal | Current Behavior | Proposed Behavior | Rationale | Risk |
|----------|-----------------|-------------------|-----------|------|
| Stage self-gate | Auditor is first entity to notice empty scaffolds | Stage refuses to hand off if any `logs/<step>/` is empty or lint has `%Error` | Fail fast, save an audit round-trip | Low |
| assert_clean hardening | BRE `grep -ci`, silent false-PASS on `A|B` | ERE `grep -Eci` + unit self-test on load | Evidence integrity across all clean-checks | Low |

---

## 14. Sign-off

| Role | Name / Agent | Date | Signature |
|------|-------------|------|-----------|
| Auditor | Claude Code Opus 4.8 | 2026-07-20 | ✅ |
| Reviewed by | Vera (Orchestrator) | — | PENDING |
| Accepted by | [User] | — | PENDING |

---

*Template version: 2.0 | Postmortem for PRJ-001 v0 Stage 04 Frontend | Vera ASIC Workflow Framework*
