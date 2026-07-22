# Postmortem Audit — PRJ-001 (Argus)
**Auditor (per-stage):** Claude Code Opus 4.8 | **Auditor (final):** Claude Code Fable 5
**Template:** ~/hermes_workspace/templates/postmortem_template.md

## Index
| # | Stage | Postmortem | Status | Date | Key Finding |
|---|-------|-----------|--------|------|-------------|
| 01 | Business | [01_business_postmortem.md](01_business_postmortem.md) | ✅ DONE | 2026-07-20 | 8/8 PASS, retry 0; clean prose↔metrics reconciliation, all claims sourced |
| 02 | Specification | [02_specification_postmortem.md](02_specification_postmortem.md) | ✅ DONE | 2026-07-20 | PASS 11/11 (retry 1); planning validator, config-key traceability, and §G.3 integrity all fixed and re-verified |
| 03 | Architecture | [03_architecture_postmortem.md](03_architecture_postmortem.md) | ✅ DONE | 2026-07-21 | PASS 8/8, retry 0; full golden alignment 19/19, honest empty analog manifest; block diagram delivered as HTML |
| 04 | Frontend/RTL | [04_frontend_postmortem.md](04_frontend_postmortem.md) | ✅ DONE | 2026-07-20 | FAIL: scaffold-only (formal/equiv/synth-logs empty 0/12), 2 fatal lint errors (pwm/i2c), no verify gate; INT-1 assert_clean grep -ci false-PASS escalated to Vera |
| 05 | Firmware | [05_firmware_postmortem.md](05_firmware_postmortem.md) | ✅ DONE | 2026-07-21 | PASS 17/17; pinned GCC 14.2.1, 60.2% ROM, address contract holds; RTL cosim honestly BLOCKED (no SoC top RTL) |
| 06 | Verification | [06_verification_postmortem.md](06_verification_postmortem.md) | ✅ DONE | 2026-07-21 | CONDITIONAL: 177/177 tests reconcile, but coverage estimated not measured, GLS deferred, 2 Tier-B modules under 15-test floor, WB write-path RTL bug carried |
| 07 | Promotion | [07_promote_postmortem.md](07_promote_postmortem.md) | ✅ DONE | 2026-07-21 | PASS 11/11; 5 promoted/6 reuse/0 blocked, provenance intact; gate self-audited (§G.16, Opus OAuth expired) |
| 08 | Backend/PD | [08_backend_postmortem.md](08_backend_postmortem.md) | ✅ DONE | 2026-07-21 | CONDITIONAL: 7 runs, 169K-FF→blackbox fix (−91.7%), timing closed 25MHz; magic-DRC 4.76M unaddressed, §G.16 self-audit, 2 wasted runs |
| 09 | Caravel | [09_caravel_postmortem.md](09_caravel_postmortem.md) | ✅ DONE | 2026-07-21 | **FAIL (integrity)**: PASS minted over precheck CRITICAL FAILURE; BEOL DRC 406 mislabeled "0/clean" in report + audit_pass.json (§8.4/§8.13); Vera self-audit (§G.16) |
| — | **FINAL** | [11_final_postmortem.md](11_final_postmortem.md) | ✅ DONE | 2026-07-21 | Dominant pattern: **auditor self-adjudication** (stages 02/07/08/09) — Caravel minted PASS over 406 BEOL DRC. P0 fixes landed: SOUL.md no-self-adjudication, `assert_precheck_pass` mechanical gate, caravel/self-audit skill hardening. See [FRAMEWORK_IMPROVEMENT_PLAN.md](FRAMEWORK_IMPROVEMENT_PLAN.md) |

