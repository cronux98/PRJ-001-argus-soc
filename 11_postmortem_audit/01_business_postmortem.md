# Postmortem Report — 01_business_stage

**Project:** PRJ-001 (Argus)
**Stage:** 01_business_stage
**Auditor:** Claude Code Opus 4.8 (Final: Claude Code Fable 5)
**Date:** 2026-07-20
**Status:** FINAL

---

## 1. Executive Summary

> The business-analysis stage for PRJ-001 (Argus, an open-source RISC-V environmental sensor-hub ASIC on sky130A) produced all five required artifacts, and every mandatory gate check (0.1–0.8) passed on the first audit with zero fixes. The single most important takeaway: the stage demonstrated clean prose↔metrics reconciliation and per-table source citation, which is exactly the discipline IP-010 v2 flagged as historically missing — this is the pattern to replicate downstream.

---

## 2. Stage Context

| Field | Value |
|-------|-------|
| Stage name | 01_business_stage (Business Analysis) |
| Input artifact(s) | IP-INDEX (REUSE catalog), market research |
| Output artifact(s) | market_validation.md, competitive_analysis.md, market_requirements.md, domain_report.md, baseline_metrics.json |
| Agent(s) involved | business-analyst (stage); Claude Code Opus 4.8 (auditor) |
| Skills dispatched | asic-workflow/evidence-assertions |
| Wall-clock duration | ~4 min (audit) |
| API cost (USD) | Pro subscription OAuth billing |
| Iterations / retries | retry 0 |
| Final verdict | PASS |

---

## 3. Timeline of Key Events

| Timestamp (UTC) | Event | Impact |
|-----------------|-------|--------|
| 2026-07-20 01:59 | Stage artifacts written (5 files) | Audit input ready |
| 2026-07-20 (audit) | Sourced evidence-assertions library; ran 0.1–0.8 + G-rules | All checks PASS |
| 2026-07-20 (audit) | `jq` absent → reconciliation done via python3 `json.load` | JSON validated, metrics reconciled |
| 2026-07-20 (audit) | audit_pass.json + validation report + postmortem + stage_metrics.json written | §G.18 atomic output satisfied |

---

## 4. What Went Well

### 4.1 Metrics ↔ Prose Reconciliation (Check 0.7)

- **Finding:** `baseline_metrics.json` values (freq 50/25 MHz, active power 10/5 mW, sleep 50/10 µW, comparables=5) matched the prose in `market_requirements.md`/`competitive_analysis.md` within ±0.
- **Why it mattered:** Prose/metric drift is the exact IP-010 v2 failure class that §8.4 and the Anti-Hallucination narrative-match rule exist to catch. Clean reconciliation here means no fabricated or stale numbers propagate to Stage 2.
- **Preserve:** Keep the single-source-of-truth pattern — quantitative claims live in `baseline_metrics.json` and prose quotes them verbatim.

### 4.2 Per-Table Source Citation (Check 0.6)

- **Finding:** Every quantitative claim table carries ≥1 source (http URL / IP-INDEX). Comparables each cite a vendor datasheet URL.
- **Why it mattered:** Satisfies IP-010 v2 Postmortem integrity rule 0.6 directly; downstream stages inherit traceable baselines.
- **Preserve:** Require a `Source` column/line in every numeric table.

---

## 5. What Went Wrong

### 5.1 Index links point to legacy (non-v6a) filenames

| Field | Value |
|-------|-------|
| Severity | LOW |
| First observed | 2026-07-20 (audit) |
| Duration | Open (cosmetic) |
| Impact | Stale links in `00_business_index.md`; no gate impact |

- **Symptom:** `00_business_index.md` links to `../00_validation_report/business_validation.md` and `../11_postmortem_audit/business_postmortem.md`, but the v6a convention (and this audit's output) uses `01_business_validation.md` / `01_business_postmortem.md`.
- **Root Cause (5 Whys):**
  1. Why? → Index template predates the v6a `NN_`-prefix rename.
  2. Why? → The stage index scaffold was copied from an older template revision.
  3. Why? → No lint enforces index-link ↔ canonical-path consistency.
  4. Why? → v6a path convention was introduced after the index scaffold was authored.
  5. Why? → Root cause: template versioning is not gated against the current path convention.
- **Fix Applied:** None (out of auditor write-scope for stage index; recorded as non-blocking). Auditor wrote to canonical `01_` paths.
- **Was this fix propagated?** Noted here + in validation report §3/§8 for the stage-index maintainer.

---

## 6. Where We Got Lucky

- **Near-miss:** `jq` was not installed in the audit environment.
  - **Why it didn't escalate:** python3 `json.load` was available as a fallback to validate JSON and reconcile metrics.
  - **What would have happened if it did:** Without a JSON parser, check 0.5/0.7 would have been ungradable → forced FAIL/BLOCKED.
  - **Preventive action:** Auditor scripts should not assume `jq`; prefer a python fallback or declare `jq` a hard dependency in the evidence-assertions library.

---

## 7. Metrics & Data

| Metric | This Stage | Previous Iteration | Delta | Source |
|--------|-----------|-------------------|-------|--------|
| Mandatory checks | 8/8 PASS | — (first audit) | — | audit_pass.json |
| Fix iterations | 0 | — | — | audit_pass.json |
| Artifacts produced | 5 | — | — | stage dir listing |
| Comparables analyzed | 5 | — | — | baseline_metrics.json `comparables_count` |
| Citation lines (mv/ca/dr) | 2 / 5 / 1+ | — | — | grep count |
| Verdict-vocab violations | 0 | — | — | grep -ci CONDITIONAL/PARTIAL |

---

## 8. Agent Performance Review

| Agent | Role | Autonomy Score (1-5) | Hallucinations | Escalations | Notes |
|-------|------|---------------------|----------------|-------------|-------|
| business-analyst | Stage author | 5 | 0 | 0 | Complete, sourced, self-consistent artifacts on first pass |
| Claude Code Opus 4.8 | Auditor | 5 | 0 | 0 | 8/8 pass; used assert_* + python JSON fallback |

**Autonomy Scale:** 5 = fully autonomous, zero intervention, proactive quality checks.

---

## 9. Hallucination Incidents

| Incident | Agent | Category | Sub-Category | Diagnostic Code | Resolution |
|----------|-------|----------|--------------|-----------------|------------|
| None | — | — | — | — | No fabricated evidence, no unsourced numeric claims, no minted verdicts detected |

---

## 10. Lessons Learned

| # | Lesson | Category | Applies To | Priority |
|---|--------|----------|------------|----------|
| 1 | Single-source-of-truth for numbers (JSON) with prose quoting it verbatim yields clean 0.7 reconciliation | FLOW | All BA/spec stages | P2 |
| 2 | Every numeric table needs a Source line to satisfy 0.6 | TEMPLATE | Business/spec stages | P2 |
| 3 | Do not assume `jq` in audit env; keep a python3 JSON fallback | SCRIPT | All auditors | P1 |
| 4 | Stage index templates must track the v6a `NN_` path convention | TEMPLATE | All stages | P3 |

---

## 11. Action Items

| # | Action | Owner | Deadline | Verification | Status |
|---|--------|-------|----------|--------------|--------|
| 1 | Update `00_business_index.md` links to `01_business_validation.md`/`01_business_postmortem.md` | Stage-index maintainer | Before Stage 2 sign-off | grep index for `01_business_*` | OPEN |
| 2 | Add python3 JSON fallback (or declare `jq` dependency) in evidence-assertions library | Vera / tooling | Next audit cycle | assertion lib parses JSON without jq | OPEN |

---

## 12. Preventive Measures

| # | Measure | Type | Affected Skill/Script | Implementation Scope |
|---|---------|------|----------------------|---------------------|
| 1 | JSON validation helper with python fallback | SCRIPT_UPDATE | evidence-assertions.sh | All stage audits |
| 2 | Index-link ↔ canonical-path lint | NEW_TEMPLATE | stage index scaffold | All stages |

---

## 13. Flow Improvement Proposals

| Proposal | Current Behavior | Proposed Behavior | Rationale | Risk |
|----------|-----------------|-------------------|-----------|------|
| Add a `assert_json` helper to evidence-assertions | Auditor ad-hoc uses jq/python | Library exposes `assert_json <file>` (python-backed) | Removes `jq`-absent failure mode | Low |

---

## 14. Sign-off

| Role | Name / Agent | Date | Signature |
|------|-------------|------|-----------|
| Auditor | Claude Code Opus 4.8 | 2026-07-20 | /s/ Opus 4.8 |
| Reviewed by | Vera (Orchestrator) | — | — |
| Accepted by | [User] | — | — |

---

*Template version: 2.0 | For Vera ASIC Workflow Framework*
