# Validation Report — PRJ-001 (Argus) Specification & Planning

**Project:** PRJ-001 (Argus) Environmental Sensor-Hub SoC
**Stage:** 02_specification_stage
**Date:** 2026-07-20
**Auditor:** Claude Code Opus 4.8 (independent audit — supersedes self-authored gate)
**Verdict:** PASS (retry 1; retry 0 was FAIL — see §RETRY 0 below)
**Retry:** 1
**Template:** ~/hermes_workspace/templates/validation_report_template.md

---

## STAGE-VERDICT: PASS (11/11 checks PASS, retry 1 — 1.6, 1.8a, §G.3 fixed since retry 0)

---

## RETRY 1 — Re-audit Summary (2026-07-20)

All 3 items that failed at retry 0 (1.6, 1.8a, G.3) were independently re-verified with genuine tool-produced evidence, not superficial keyword matches:

| # | Check | Retry 0 | Retry 1 | Evidence |
|---|-------|---------|---------|----------|
| 1.6 | Planning validator PASS | FAIL (no artifact) | **PASS** | `planning_validator.log` (2,655 B) ends `RESULT: PASS`; documents 5 sub-checks: (a) 61 SYS-xx-NNN ID uniqueness/referential integrity, (b) memory-map non-overlap across 10 regions, (c) 12/12 module cross-reference M01–M12, (d) module_list.md arithmetic (5+1+6=12, ratio 0.500), (e) traceability config-key coverage 61/61 requirements bound. `PASS` marker file also present. |
| 1.8a | Requirement→config-key binding | FAIL (no artifact) | **PASS** | `traceability_matrix.md` (12,435 B, `grep -c 'SYS-'` = 97) — bidirectional map: 29-key Config Key Inventory, forward map (61 reqs → config keys across FR/PR/IR/AR/CR), reverse trace (29/29 keys → reqs). Self-verifying Integrity Checks table: 29/29 keys bound, 37/37 tunable MUST reqs bound, 0 orphan keys. One disclosed exception (SYSCTRL.RESET_CAUSE, labeled "architectural — no direct SYS-xx"), consistent with the 1.9 REUSE* documented-exception precedent. |
| G.3 | Reserved-filename integrity | FAIL (self-authored gate) | **PASS** | `test ! -f audit/audit_pass.json` confirmed true prior to this independent write — the stage's self-authored `audit_pass.json` was deleted per the retry-0 STAGE_FIX and not replaced by the stage agent. This file is now written exclusively by the independent auditor. |

Spot-check: `golden_model/determinism.json` re-confirmed `identical: true` (no regression from retry 0's independent verification of genuine, non-forged determinism).

**Retry 1 Checklist Verdict: 11/11 PASS**

---

## RETRY 0 — Original Audit (2026-07-20, superseded by retry 1 above)

---

## 1. Run Summary

| Metric | Value |
|--------|-------|
| Checks passed | 9 / 11 |
| Cost (USD) | ~$0.14 |
| Duration (min) | ~6 |
| Model | claude-opus-4-8 |
| Stage directory | `projects/PRJ-001/v0/02_specification_stage/` |

---

## 2. Audit Checks

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1.1 | System specification exists | PASS | `system_spec.md` 43,009 B, 12 sections (SRS: FR/PR/IR/AR/CR, memory map §8, clock/reset §9, budgets §10, traceability §11) |
| 1.2 | Module list defined (≥3) | PASS | `grep -ci 'module\|block\|component' system_spec.md` = 11; `module_list.md` M01–M12 |
| 1.3 | Interface definitions (≥3) | PASS | `grep -ci 'interface\|bus\|protocol\|signal'` = 33; §5 SYS-IR-001..010 |
| 1.4 | Golden model exists | PASS | `golden_model/golden_model.py` 40,891 B (9 component models, 17 tests / 19 assertions) |
| 1.5 | Golden model deterministic (identical, not forged) | PASS | `determinism.json` identical=true, n_runs=3. 3 distinct files (md5 a3ef7d/ef867e/54d378) with distinct seeds 42/123/999 but identical tests-array hash. Fresh re-run seed42 reproduces `ba221a50..` (indent2) / `32fec48a..` (no-indent). Genuine determinism, not byte-copies. |
| 1.6 | **Planning validator PASS** | **FAIL** | No `planning_validator*.log`, no `PASS` marker anywhere in stage. `find <stage> -iname '*validator*' -o -iname PASS` = empty (empty glob = FAIL). Self-audit substituted "golden tests pass" — not the rubric check. |
| 1.7 | Requirements traceable (unique IDs) | PASS | 61 unique `SYS-(FR\|PR\|IR\|AR\|CR)-NNN` IDs; §11 maps every ID → block + verification method |
| 1.8a | **Requirement→config-key binding (`traceability_matrix.md`)** | **FAIL** | No `traceability_matrix.md`; no requirement→config-key mapping. §11 maps req→block→verification (that is 1.7), not req→config key. `find -iname '*traceabil*' -o -iname '*config*'` = empty. |
| 1.8b | Summary arithmetic reconciles | PASS | `module_list.md`: 5+1+6=12; reuse 0.50 by count = 6/12; 0.80 by GE = 66/83; 12 inventory rows. ±0. |
| 1.9 | REUSE/CREATE rule for REUSE-with-extension | PASS | `module_list.md` REUSE* category + M07 rule ("Changes to base IP: None … adaptations in a wrapper"); SYS-CR-003 codifies it |
| 1.10 | Self-referential hash excludes hash field | PASS | `golden_model.py` L1062–1063: hash of `output['tests']` computed BEFORE injection into `_metadata['tests_md5']`; `_metadata` excluded |
| G.3 | Reserved-filename integrity (auditor-owned gate) | FAIL | Stage self-authored `audit/audit_pass.json` (reserved auditor filename) and graded PASS on an 8-check subset that skipped 1.9/1.10 and mis-mapped 1.6/1.8 |

**Checklist Verdict: 9/11 PASS (2 rubric FAILs + 1 integrity FAIL)**

---

## 3. Findings

- **Core spec quality is high and honest.** Determinism is genuinely reproducible (three distinct seed files with a common tests-array hash, re-run reproduces it), summary arithmetic reconciles to ±0, self-referential hashing correctly excludes the hash field, and no fabricated prose→metric claims were found. The SRS is thorough (61 unique requirement IDs, complete 12-region memory map, per-block timing/area/power budgets).
- **FAIL 1.6** — The named planning/spec-consistency validator was never produced: no `planning_validator*.log`, no `PASS` marker. The empty glob is a definitive FAIL under the IP-005 v6 F4 empty-glob rule.
- **FAIL 1.8a** — No `traceability_matrix.md` binding requirements to config keys. The §11 matrix satisfies 1.7 (req→block→verification) but does not implement the 1.8 config-key binding the rubric requires.
- **Integrity (G.3)** — The stage self-wrote `audit/audit_pass.json`, a reserved auditor-owned filename, and self-graded PASS on a re-numbered 8-check subset (its "1.6" = golden tests pass; its "1.8" = §11 traceability), skipping rubric checks 1.9 and 1.10 entirely. The self-audit itself flagged "human gate recommended" due to the OAuth outage; this independent audit supersedes it with a FAIL.
- **Non-blocking** — `determinism.json` `first_hash` (`32fec48a..`, no-indent, from `run_determinism.sh`) ≠ `golden_output` `_metadata.tests_md5` (`ba221a50..`, indent=2, from `golden_model.py`). Two serialization methods; determinism holds under both. Cosmetic, but unify the hashing method.

---

## 4. Fixes Generated

| # | Type | Description | File | Action |
|---|------|-------------|------|--------|
| 1 | STAGE_FIX | Produce planning validator + `planning_validator.log` ending `RESULT: PASS` (or a `PASS` marker) | `02_specification_stage/planning_validator.py` | Assert unique/referenced req IDs, non-overlapping memory map, module_list↔spec module parity, arithmetic reconciliation; `python3 planning_validator.py \| tee planning_validator.log` |
| 2 | STAGE_FIX | Author `traceability_matrix.md` binding each requirement to its config key (no orphan keys, no unbound MUST reqs) | `02_specification_stage/traceability_matrix.md` | Table [Req ID \| Config Key \| Block \| Value]; e.g. SYS-FR-002→UART.BAUD_DIV(434), SYS-PR-007→I2C.CLK_DIV_LO/HI, SYS-PR-001→CLK_PERIOD(20ns), SYS-FR-007→SRAM_SIZE(0x1000) |
| 3 | STAGE_FIX | Remove self-authored reserved gate file | `02_specification_stage/audit/audit_pass.json` | `rm audit/audit_pass.json`; stage self-report stays in `audit/stage_report.md` |

---

## 5. Conditional Pass Items

None. (No CONDITIONAL PASS is permitted — §G.8.)

---

## 6. Cross-Validation

| Parameter | Source A | Source B | Match? |
|-----------|----------|----------|--------|
| Total modules | module_list.md summary = 12 | inventory rows M01–M12 = 12 | ✓ |
| Reuse ratio (count) | headline 0.50 | (5 REUSE + 1 REUSE*) / 12 = 0.500 | ✓ |
| Reuse ratio (GE) | headline 0.80 | 66 reused / ~83 kGE = 0.795 | ✓ |
| Determinism tests hash | determinism.json runs (32fec48a, no-indent) | golden_output _metadata (ba221a50, indent2) | ✗ (method mismatch — non-blocking, both self-consistent) |
| Determinism identical | determinism.json identical=true | re-run seed42 reproduces hash | ✓ |

---

## 7. Final Verdict (superseded by RETRY 1)

**RETRY 0: FAIL** — 9 of 11 mandatory Stage 1 checks pass (original text below, preserved for history).

**RETRY 1: PASS** — 11 of 11 mandatory Stage 1 checks pass. All three retry-0 gaps (1.6 planning validator, 1.8a requirement→config-key `traceability_matrix.md`, §G.3 reserved-filename integrity) are closed with genuine, independently-verified evidence. See §RETRY 1 above for details.

*(Original retry-0 text:)* The specification content is strong, honest, and reconciles internally, but two rubric-mandated artifacts are simply absent (1.6 planning validator, 1.8a requirement→config-key `traceability_matrix.md`), and the stage committed a §G.3 integrity violation by self-authoring the auditor-owned `audit_pass.json` on an incomplete, mis-mapped check subset. All three are closed by concrete STAGE_FIX actions; none are structural (all gaps are ≥50% closeable by adding the missing artifact, not by a threshold waiver).

---

## 8. Handoff to Next Stage

**Gate open as of retry 1: `audit/audit_pass.json` exists with `verdict: PASS` (auditor-authored).** Architecture (03_architecture_stage) may now dispatch per §G.1.
- Consume `system_spec.md` (§8 memory map, §9 clock/reset, §10 budgets) and `module_list.md` (M01–M12, interface matrix) — both are reliable.
- Consume `traceability_matrix.md` to drive the requirement→config→architecture chain (61 requirements → 29 config keys, bidirectional).
- The golden model (`golden_model/`) is a trustworthy reference and can be reused for architecture comparison (Stage 2 §2.8).

---

*Generated by Claude Code during the validation gate. See CLAUDE.md rubric for check definitions.*
*Index entry: [00_validation_index.md](00_validation_index.md)*
