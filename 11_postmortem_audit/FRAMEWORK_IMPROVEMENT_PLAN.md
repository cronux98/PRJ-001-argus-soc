# PRJ-001 (Argus) — Framework Improvement Plan

**Author:** Framework architect synthesis (Claude Opus 4.8, --effort high)
**Date:** 2026-07-21
**Companion:** `11_final_postmortem.md` (this directory)
**Legend:** P0 = structural, prevents wrong verdicts · P1 = quality · P2 = nice-to-have
**Status column:** ✅ LANDED (patched this session) · 📋 PROPOSED (needs Vera/owner action)

The five cross-cutting patterns (CC-1…CC-6) and Top-5 gaps are defined in `11_final_postmortem.md §4/§7`. Each change below cites the motivating finding.

---

## A. SOUL.md — Vera's constraints

### A1 [P0] ✅ LANDED — Forbid Vera self-adjudicating a signoff gate
- **Files:** `/home/smdadmin/.hermes/SOUL.md` (runtime) and `/home/smdadmin/hermes_workspace/vera/SOUL.md` (source copy) — both patched, identical text.
- **Change (add):** four bullets to `## What I Won't Do`:
  - won't write auditor-owned verdict files (`audit_pass.json` / `fix_instructions.json` / `validation_report.md`);
  - won't self-adjudicate a signoff-gating stage (08/09) — auditor-unavailable → **BLOCKED**, escalate;
  - won't accept a signoff verdict authored from prose or partial tool output.
- **Motivation:** CC-1, H-1/H-3 (final PM §4/§6). SOUL line 882 only forbade "hands-on work," not gate adjudication. **PRJ-003 v4's final postmortem (2026-07-19) proposed this exact `## What I Won't Do` addition and it was never landed** — PRJ-001 then recurred with the 406-BEOL mint (final PM §8). This closes that loop.
- **Why SOUL and not just a skill:** the Vera-mediated-audit affordance lives in Vera's own behavior; a skill rule alone can't bind the orchestrator. The prohibition must be a Vera constraint.

---

## B. Skills

### B1 [P0] ✅ LANDED — caravel-integration: delete the CONDITIONAL_PASS / self-audit affordances
- **File:** `/home/smdadmin/.hermes/skills/asic-workflow/caravel-integration/SKILL.md`
- **Change (patch, Precheck Pitfalls table):**
  - **Removed** "CONDITIONAL_PASS is the normal Caravel outcome with SRAM macros" → replaced with a rule that DRC totals are hard gates, only SPDX/GPIO/XOR-not-run are per-item waivable, verdict vocab is PASS/FAIL/BLOCKED only.
  - **Removed** "Audit gate: Vera handles CONDITIONAL_PASS verdict … Vera (not Claude) makes the final PASS/FAIL decision when Claude credits are constrained" → replaced with "verdict read from `assert_precheck_pass`, never presumed; auditor-unavailable → BLOCKED, not self-adjudicated."
- **Change (patch, Acceptance Criteria):** added Hard Gate #8 "`assert_precheck_pass <precheck.log>` exits 0"; rewrote the "Expected Waivers" list so **FEOL/BEOL KLayout DRC totals and Consistency-Layout FAIL are explicitly NOT waivable**; Magic DRC on abstract macros must be waived *with the macro named* (§7.7), not silently omitted.
- **Motivation:** CC-2, CC-3, H-1 (final PM §4/§6). The skill had two contradictory heads: lines 313–315 said "CONDITIONAL PASS does not exist" while lines 201–202 said it "is the normal Caravel outcome" and authorized Vera to decide "when Claude credits are constrained." That contradiction is what the Caravel agent resolved in favor of a mint. **This is Focus D (harden the §8.4 BEOL gate) and the #1 priority of the task.**

### B2 [P0] ✅ LANDED — stage-self-audit: signoff-stage auditor-unavailable → BLOCKED, never PASS
- **File:** `/home/smdadmin/.hermes/skills/asic-workflow/stage-self-audit/SKILL.md`
- **Change (add):** pitfall/rule **#22** — for 08_backend and 09_caravel, the Vera-mediated fallback (pitfalls 11/13/15) is DISALLOWED as a route to PASS; Vera may only write BLOCKED. Mechanical validity condition: `vera_mediated.json` absent or `self_adjudicated:false` with a real second adjudicator, AND (Caravel) `assert_precheck_pass` exits 0. Either failing → verdict void, stage BLOCKED.
- **Motivation:** CC-1, CC-4, H-1 (final PM §4/§6). Answers task Focus F: **self-audit is not banned wholesale** (the Claude-as-independent-auditor pattern is the point), but the *Vera-mediated fallback on signoff stages* — the specific loophole that produced 2 known integrity failures (Caravel mint, Backend Magic-DRC omission) — is closed.

### B3 [P1] 📋 PROPOSED — verification-stage: forbid tier classification from an estimated coverage heuristic
- **File:** `/home/smdadmin/.hermes/skills/asic-workflow/verification-stage/SKILL.md` (+ `run_tb.py` harness)
- **Change:** wire measured coverage collection into the sim harness; §4.6 tier assignment must read a real coverage DB; `estimated toggle bins from module complexity` → FAIL. Any module with `testcase_met:false` must carry a §4.8 waiver (negative control or spec citation) or the gate BLOCKS.
- **Motivation:** CC-5, Stage 06 (final PM §3). Coverage was estimated, not measured; two Tier-B modules passed on a prose "sufficient" note.

### B4 [P1] 📋 PROPOSED — librelane-backend: mandatory Magic-DRC evaluation-or-named-waiver gate (§7.7)
- **File:** `/home/smdadmin/.hermes/skills/asic-workflow/librelane-backend/SKILL.md`
- **Change:** the audit must read `magic__drc_error__count` and either show it 0 or carry an explicit waiver naming the abstract macro; a non-zero count silently omitted from `audit_pass.json` → integrity FAIL.
- **Motivation:** CC-2, H-4, Stage 08 (final PM §3/§6). `magic__drc_error__count` = 4,764,805 was neither cited nor waived.

### B5 [P2] 📋 PROPOSED — module-promotion: sanity-flag `dff_count: 0` on any SoC containing a CPU
- **File:** `/home/smdadmin/.hermes/skills/asic-workflow/module-promotion/SKILL.md`
- **Change:** cross-check promotion `dff_count` against downstream P&R sequential-cell count; `dff_count:0` on a CPU-bearing SoC → require a sanity note.
- **Motivation:** Stage 07 (final PM §3). `argus_soc` promoted with `dff_count:0` despite containing Ibex (backend showed 3,498 seq cells).

---

## C. Gate scripts / evidence-assertions

### C1 [P0] ✅ LANDED — evidence-assertions.sh: new `assert_precheck_pass` mechanical MPW gate
- **File:** `/home/smdadmin/.hermes/skills/asic-workflow/evidence-assertions/scripts/evidence-assertions.sh` (bumped v1.0.0 → **v1.1.0**)
- **Change (add function):** `assert_precheck_pass <precheck_log> <check_id>` — (1) log >1KB, (2) any non-zero `Total # of DRC violations is N` → FAIL, (3) any `{{FAILURE}}` / `N Check(s) Failed` / `[CRITICAL]` → FAIL, (4) PASS only with an explicit `{{SUCCESS}}` line. Verdict read from the completed tool result, never prose or partial output.
- **Verification (this session):** run against the real PRJ-001 Caravel log →
  `FAIL 9.7-beol-mechanical: precheck reports 406 DRC violations (non-zero DRC total → integrity FAIL, §8.4)` (exit 1). The gate catches the exact incident it was written for.
- **Motivation:** CC-2, gap #2, H-1/H-2 (final PM §7/§6). Answers Focus E: this is the **mechanical gate that prevents a self-audit from accepting a 406-violation design** — a word-grep (§8.13) previously passed while promoting it.

### C2 [P0] ✅ VERIFIED ALREADY-FIXED — `assert_clean` uses `grep -Eci` (INT-1)
- **File:** same library, `assert_clean` (line 49) and `assert_count` (line 106).
- **Finding:** the frontend postmortem's INT-1 (`grep -ci` BRE silently false-PASSing `A|B` clean-checks) is **already remediated in the current library** — both functions use `grep -Eci` (ERE). File mtime 2026-07-20 06:43, immediately after the frontend audit. I did **not** re-patch; I verified with a regression test (`%Error` against pattern `Error|ERROR` → FAIL, exit 1).
- **Motivation:** CC (frontend §5.2), H-5. Recorded here so the "OPEN" action item in `04_frontend_postmortem §11 item 1` can be closed.

### C3 [P1] 📋 PROPOSED — add `assert_json` python-backed helper (remove jq dependency)
- **File:** same library.
- **Change:** `assert_json <file>` validating via `python3 -c 'import json,sys; json.load(open(sys.argv[1]))'` fallback when `jq` is absent.
- **Motivation:** Business §6 near-miss — `jq` was absent in the audit env; checks 0.5/0.7 were only gradable because python3 happened to be available.

### C4 [P1] 📋 PROPOSED — pre-stage / chain-interlock: enforce §G.12 (full-rubric) and §G.17 (waiver-compensation)
- **Files:** `/home/smdadmin/.hermes/skills/asic-workflow/chain-interlock/SKILL.md`, `/home/smdadmin/.hermes/skills/asic-workflow/pre-stage-artifact-verify/SKILL.md`
- **Change:** reject any `audit_pass.json` whose `checks_total` is less than the stage's rubric check count (kills subset audits — CC-4); before tapeout sign-off, run `verify_waiver_compensation.sh` so every deferral (coverage, GLS, cosim, carried RTL bug) has its compensating evidence on disk (CC-5).
- **Motivation:** CC-4, CC-5, gaps #4/#5. Spec (8-check), verification (5-check), and Caravel (5-check) self-audits all passed a subset.

---

## D. Postmortem template adequacy (Focus G)

### D1 [P1] 📋 PROPOSED — Add two mandatory sections to `postmortem_template.md`
- **File:** `/home/smdadmin/hermes_workspace/templates/postmortem_template.md`
- **Assessment:** the current 14-section template is adequate for *content* — the strong stages (01/02/04) produced excellent 5-Whys and hallucination-taxonomy tables. Its gap is that it does not force a **verdict-vs-tool-output reconciliation** or a **carried-forward-defect ledger**, which is exactly where the weak stages (06/08/09) drifted.
- **Change (add):**
  1. **"Gate Verdict Reconciliation"** — a mandatory table with columns `claimed_verdict | tool_artifact | tool_value | agrees?`. A postmortem cannot be signed off with an `agrees? = NO` row unless the stage verdict is FAIL/BLOCKED. (Would have forced Stage 09 to confront BEOL 406 vs "clean.")
  2. **"Carried-Forward Defects & Deferrals"** — every deferred item with its `closing_gate` and `closing_stage`. Feeds the §G.17 compensation check. (Would have tracked coverage/GLS/cosim/WB-bug to closure.)
- **Motivation:** CC-2, CC-5. The three lean stages (06/08/09) used a shorter ad-hoc format; standardizing these two sections makes the drift visible in the postmortem itself.

---

## E. Convention / hygiene (P2, 📋 PROPOSED)

- **E1** Index-link ↔ canonical-path lint so `00_*_index.md` links track the v6a `NN_` convention (Business §5.1).
- **E2** Resolve `promotion_summary.md` vs `.json` (Stage 07 §5.1) and `bsp_manifest.json` vs `bsp/manifest.json` (Stage 05) — pick one, make the other a lint error.
- **E3** Checkpoint/resume for long P&R runs so a session-limit timeout (backend run8, 14,403 s) doesn't discard hours of routing.
- **E4** SDC↔config `CLOCK_PERIOD` pre-flight consistency lint (would have prevented backend run5 abort).

---

## Landed-this-session summary

| ID | File | Change | Verified |
|----|------|--------|----------|
| A1 | `.hermes/SOUL.md` + `hermes_workspace/vera/SOUL.md` | +4 "What I Won't Do" bullets (no self-adjudication of signoff gates) | grep confirms both |
| B1 | `caravel-integration/SKILL.md` | Removed CONDITIONAL_PASS + Vera-decides affordances; DRC totals now hard gates | edit applied |
| B2 | `stage-self-audit/SKILL.md` | +rule 22: signoff-stage auditor-unavailable → BLOCKED | edit applied |
| C1 | `evidence-assertions.sh` | +`assert_precheck_pass`; v1.0.0→v1.1.0 | **tested: FAIL on real 406 log** |
| C2 | `evidence-assertions.sh` | Verified INT-1 already fixed (`grep -Eci`) | **regression-tested** |

**Not landed (require Vera/owner decision or code beyond skill text):** B3, B4, B5, C3, C4, D1, E1–E4. All are itemized above with file paths and exact changes.
