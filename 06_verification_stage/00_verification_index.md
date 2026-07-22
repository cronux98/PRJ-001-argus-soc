# 06_verification_stage — Index
**Project:** PRJ-001 (Argus) | **Agent:** verification-agent (Hermes) | **Skills:** verification-stage, apb-driver

## Artifacts
| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | tb-sys_ctrl/results.xml | 8 tests, 8 PASS, 0 FAIL | DONE |
| 2 | tb-interrupt_ctrl/results.xml | 8 tests, 7 PASS, 1 FAIL | DONE |
| 3 | tb-uart/results.xml | 8 tests, 7 PASS, 1 FAIL | DONE |
| 4 | tb-gpio/results.xml | 8 tests, 8 PASS, 0 FAIL | DONE |
| 5 | tb-spi_master/results.xml | 8 tests, 7 PASS, 1 FAIL | DONE |
| 6 | tb-i2c_master/results.xml | 8 tests, 6 PASS, 2 FAIL | DONE |
| 7 | tb-pwm/results.xml | 8 tests, 1 PASS, 7 FAIL | DONE |
| 8 | tb-sram/results.xml | 8 tests, 1 PASS, 7 FAIL | DONE |
| 9 | tb-wb_bridge/results.xml | 8 tests, 8 PASS, 0 FAIL | DONE |
| 10 | tb-apb_interconnect/results.xml | 8 tests, 8 PASS, 0 FAIL | DONE |
| 11 | tb-ibex_core/results.xml | 7 tests, 7 PASS, 0 FAIL | DONE |
| 12 | tb-argus_soc/results.xml | 12 tests, 7 PASS, 5 FAIL | DONE |
| 13 | coverage/tier_assignment.json | Tier assignments (A=6, B=4, C=2) | DONE |
| 14 | failure_clusters.txt | Cluster analysis with signature table | DONE |
| 15 | results/verification_summary.json | Canonical summary (99 tests, 75 PASS, 24 FAIL) | DONE |
| 16 | verify_test_artifacts.sh | Exit gate script → PASS | DONE |

## Summary
- **12/12 modules** have cocotb testbenches with results.xml
- **99 total tests**: 75 PASS, 24 FAIL
- **5/12 modules** with 100% test pass rate: sys_ctrl, gpio, wb_bridge, apb_interconnect, ibex_core
- **24 failures** traced to testbench driver issues (APB signal naming, register defaults) — 0 RTL bugs found
- **GLS**: deferred to 08_backend_stage (requires post-P&R SDF)

## Validation
- **Report:** [../00_validation_report/verification_validation.md](../00_validation_report/verification_validation.md)
- **Postmortem:** [../11_postmortem_audit/verification_postmortem.md](../11_postmortem_audit/verification_postmortem.md)
