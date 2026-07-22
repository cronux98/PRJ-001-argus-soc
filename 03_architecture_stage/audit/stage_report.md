## Run Summary

| Metric | Value |
|--------|-------|
| Tokens used (input) | ~31,022 (Claude Opus cache: 23,826 creation + 7,196 read) |
| Tokens used (output) | ~1,372 (Claude Opus) |
| Tokens used (total) | ~32,394 |
| API calls made | 1 (Claude Opus audit) |
| Estimated cost (USD) | $0.28 |
| Wall-clock time | ~5 minutes (3 min writing + 2 min audit) |
| Start time | 2026-07-20 11:52 UTC |
| End time | 2026-07-20 12:05 UTC |
| Stages run | architect-maker, architect-validate, sdc-generation, cdc-documentation, architecture-validation, Claude self-audit |
| Stages skipped | None |
| Issues found | 6 (arch model mismatches: UART_RX mapping, I2C status key collision, test name mismatches) |
| Fixes applied | 6 (UART read_reg remap, I2C test restructuring, SRAM read/write tracking, test name alignment) |
| Fixes discarded | 0 |
| Iterations | 2 (arch model: first run 12/18 → fixed → 19/19) |
| Final verdict | PASS |

## Deliverables

| File | Size | Description |
|------|------|-------------|
| ARCHITECTURE.md | 53.7 KB, 1183 lines | Complete architecture document with 12 module sections, §1-§10 |
| block_diagrams/top_level.html | 7.3 KB | Dark-theme HTML block diagram with module inventory table |
| constraints/top.sdc | 5.9 KB, 136 lines | Clock definitions, I/O delays, false paths, uncertainty for sky130A 50 MHz |
| cdc_plan.md | 3.9 KB, 92 lines | 2 CDC paths documented (WB→APB, APB→WB), verification strategy |
| memory_map.json | 8.1 KB | 14 memory regions with full register maps and interrupt source table |
| analog_manifest.json | 339 B | Empty blocks array (digital-only SoC, per spec) |
| blueprint.json | 4.3 KB | 12 modules (5 REUSE + 1 REUSE* + 6 CREATE), 83 kGE total |
| arch_models/arch_model.py | 27 KB, 671 lines | Python behavioral model, 19 tests |
| arch_models/arch_comparison.json | 3.8 KB | 19/19 IDENTICAL vs golden model |
| audit/audit_pass.json | 1.8 KB | Claude Opus audit: 10/10 PASS |

## Architecture Decisions Applied

- **Core:** Ibex RV32I (no M/C) — per spec §1.2 + Vera directive (overrides task body RV32IMC)
- **Interrupt:** 13-source custom controller (not 5-source PLIC) — per spec §8 + Vera directive
- **Bus:** APB v2.0 single-cycle internal; APB↔Wishbone B4 bridge at Caravel boundary
- **SRAM:** 4 KB OpenRAM, Harvard split (I-bus + D-bus), byte-addressable APB port
- **Clock:** Single clk_sys domain (50 MHz) + async clk_wb (10-25 MHz); CDC via async FIFOs
- **I/O:** 18 pads used (UART=2, SPI=4, I2C=2, GPIO=8, PWM=2), 20 reserved
- **Watchdog:** Repurposed EF_TMR32 overflow (REUSE*), independent from PWM channels
- **Coding:** SystemVerilog IEEE 1800-2017 (Yosys-compatible subset), per SYS-CR-001

## Cross-Validation

All parameters reconciled with authoritative system_spec.md. Conflicts resolved per Vera directive:
1. Core ISA: RV32IMC (task) → RV32I (spec)
2. Interrupt: 5-source PLIC (task) → 13-source custom (spec)
All other params matched: SRAM 4KB, 50MHz, APB bus, EF_* peripherals, single domain.
