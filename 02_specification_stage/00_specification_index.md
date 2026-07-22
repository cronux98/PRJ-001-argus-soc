# 02_specification_stage — Index
**Project:** PRJ-001 (Argus) | **Agent(s):** spec-product-engineer | **Skills:** asic-design/systems-planner, golden-model-generator

## Artifacts
| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | system_spec.md | System Requirements Specification (43 KB, 12 sections, 65+ REQ-IDs) | READY |
| 2 | module_list.md | Module inventory (12 modules, interface matrix, verification ownership) | READY |
| 3 | golden_model/golden_model.py | Python behavioral model (9 component models, 17 tests, 19 assertions) | 19/19 PASS |
| 4 | golden_model/golden_output.json | Golden reference output (seed=42) | READY |
| 5 | golden_model/determinism.json | Determinism check: N=3, identical=true | PASS |
| 6 | golden_model/run_determinism.sh | Determinism check script | READY |
| 7 | audit/stage_report.md | Stage run report (metrics, issues, fixes) | READY |

## Validation
- **Report:** [../00_validation_report/02_specification_validation.md](../00_validation_report/02_specification_validation.md)
- **Postmortem:** [../11_postmortem_audit/02_specification_postmortem.md](../11_postmortem_audit/02_specification_postmortem.md)
- **Audit:** [audit/audit_pass.json](audit/audit_pass.json)
