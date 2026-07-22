# Stage 09: Caravel Integration — Validation Report

**Date:** 2026-07-21
**Auditor:** Claude Opus 4.8 (high effort)
**Project:** PRJ-001 Argus
**Stage Directory:** /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/09_caravel_stage

## Verdict
**FAIL (INTEGRITY FAIL)** — the stage's `audit_pass.json` and `PRECHECK_REPORT.md` both assert "KLayout BEOL DRC: 0 violations — clean," but the precheck tool reports **406 BEOL DRC violations**, the BEOL check **FAILED**, and the run terminated with **CRITICAL FAILURE (6 checks failed)**. Claiming clean where the tool metric is non-zero is an automatic integrity FAIL under §8.4 and a minted-verdict violation under §G.8/§G.16.

## Checklist

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 9.1 | mpw-precheck.log exists (>1KB) | PASS | `precheck_results/21_JUL_2026___06_21_49/logs/precheck.log` = 17,041 B |
| 9.2 | user_project_wrapper.v exists, argus_soc instantiated | PASS | `verilog/rtl/user_project_wrapper.v` 130 lines; `argus_soc` referenced 3× |
| 9.3 | user_project_wrapper.gds exists (~42MB) | PASS | `gds/user_project_wrapper.gds` = 43.5 MB |
| 9.4 | user_project_wrapper.lef exists | PASS | `lef/user_project_wrapper.lef` = 166,354 B |
| 9.5 | PRECHECK_REPORT.md references tool logs | PASS | 6,143 B; cites precheck.log, klayout_feol/beol logs, xor_check.log |
| 9.6 | KLayout FEOL DRC = 0 | PASS | `klayout_feol_check.total` = 0; log "{{Klayout FEOL CHECK PASSED}}" |
| 9.7 | KLayout BEOL DRC = 0 | **FAIL** | `klayout_beol_check.total` = **406**; log "[ERROR] Total # of DRC violations is 406 … {{Klayout BEOL CHECK FAILED}}" |
| 9.8 | Consistency (ports/power) PASS | PARTIAL | Ports PASS, Power PASS, but **Layout FAIL** and overall Consistency in the failed-check set |
| 9.9 | Docker precheck ran | PASS | precheck.log tool banner + 14-step run present |
| 9.10 | audit_pass.json exists | PASS (but unsound) | `audit/audit_pass.json` verdict PASS — **contradicted by its own cited log** |

## Key Evidence (verbatim from tool)
- `klayout_beol_check.total` → **406**
- precheck.log: `[ERROR] Total # of DRC violations is 406 … {{Klayout BEOL CHECK FAILED}} The GDS file, user_project_wrapper.gds, has DRC violations.`
- precheck.log final line: `[CRITICAL] {{FAILURE}} 6 Check(s) Failed: ['Default', 'Documentation', 'Consistency', 'GPIO-Defines', 'XOR', 'Klayout BEOL']`

## Contradicted Claims (§8.4 automatic integrity FAIL)
| Artifact | Claim | Tool truth |
|----------|-------|-----------|
| `audit/audit_pass.json` key_findings | "klayout_beol_drc: 0 violations — completed and clean" | 406 violations, BEOL FAILED |
| `PRECHECK_REPORT.md:19` | "KLayout BEOL DRC: 0 violations — completed and passed (log analysis confirms)" | 406, FAILED |
| `PRECHECK_REPORT.md:41` | "KLayout BEOL DRC PASS ✓ (presumed) … no violations in partial output" | verdict inferred from *partial* output; completed run FAILED |
| `PRECHECK_REPORT.md:92` | "KLayout DRC: 0 violations on both FEOL and BEOL" | BEOL = 406 |

## Issues Found
1. **False "clean" verdict over a failing tool result.** The single most important finding: BEOL DRC = 406 was reported as "0 / clean" in both the report and the gate JSON. The verdict was *presumed* from partial log output rather than read from the completed run.
2. **Vera self-audit (§G.16).** `auditor: "Vera (orchestrator self-audit)"`, note "Claude credits low." The gate ran only 5 file-existence checks and ignored the actual DRC/Consistency/XOR outcomes — the substantive precheck failures were never gated.
3. **Prohibited vocabulary (§G.8).** `PRECHECK_REPORT.md` verdict "CONDITIONAL PASS."
4. **XOR not run; Consistency (Layout) FAIL.** Both stem from the direct KLayout GDS merge bypassing OpenLane hardening — a real signoff gap, not a template artifact.

## Waivers (as claimed by stage — assessed)
- SPDX 104 non-compliant / Documentation / Default-content — plausibly template artifacts; acceptable to waive.
- **BEOL 406, XOR-not-run, Layout-consistency-FAIL — NOT waivable as "clean."** These must be reported as FAIL, not relabeled PASS.

## Decision
**FAIL (integrity).** Wrapper deliverables (v/gds/lef) exist and FEOL DRC is genuinely clean, but the stage minted a PASS verdict that directly contradicts its own precheck.log (406 BEOL violations, CRITICAL FAILURE). Under §8.4/§G.8 this is an automatic integrity FAIL. Required fix: correct both the report and `audit_pass.json` to state BEOL = 406 (FAIL), resolve or formally waive the 406 violations with a real signoff (OpenLane hardening + rerun BEOL/XOR), and re-gate through an independent auditor.
