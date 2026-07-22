# Module List — PRJ-001 (Argus) v0

**Project:** PRJ-001 (Argus) Environmental Sensor-Hub SoC
**Date:** 2026-07-20
**Author:** Systems Planner (spec-product-engineer)

## Summary

| Metric | Value |
|--------|-------|
| Total modules | 12 |
| REUSE (STRONG, unmodified) | 5 |
| REUSE* (STRONG, adapted) | 1 |
| CREATE (new) | 6 |
| REUSE ratio | 0.50 (by count), 0.80 (by gate-equivalent) |

## Module Inventory

| # | Module Name | Type | Source | IP Tier | Clock Domain | Gate Equiv. (est.) | Interfaces | Description |
|---|-------------|------|--------|----------|-------------|---------------------|------------|-------------|
| M01 | ibex_core | REUSE | lowrisc-ibex (Apache-2.0) | STRONG | clk_sys | ~15 kGE | APB master, IRQ input, debug | RV32I RISC-V core, 2-stage "maxperf" config |
| M02 | apb_interconnect | CREATE | — | — | clk_sys | ~3 kGE | Ibex APB master ↔ peripheral APB slaves | Address decoder, mux, routing. 12 slave ports (1 per peripheral + SRAM + bridge). |
| M03 | uart | REUSE | fossi-ef-uart (Apache-2.0) | STRONG | clk_sys | ~2 kGE | APB slave, TX/RX to pads | Full-duplex UART, 8-byte TX/RX FIFOs, configurable baud |
| M04 | spi_master | REUSE | fossi-ef-spi (Apache-2.0) | STRONG | clk_sys | ~2 kGE | APB slave, SCK/MOSI/MISO/CS to pads | SPI Mode 0/3 master, 8-byte FIFO, configurable prescaler |
| M05 | i2c_master | REUSE | fossi-ef-i2c (Apache-2.0) | STRONG | clk_sys | ~2 kGE | APB slave, SCL/SDA to pads (open-drain) | I2C 100/400 kHz master, 7-bit addr, multi-byte, repeated start |
| M06 | gpio | REUSE | fossi-ef-gpio8 (Apache-2.0) | STRONG | clk_sys | ~1 kGE | APB slave, gpio[7:0] to pads | 8-pin GPIO, per-pin dir/IRQ/edge |
| M07 | pwm | REUSE* | fossi-ef-tmr32 (Apache-2.0) | STRONG | clk_sys | ~4 kGE | APB slave, pwm[1:0] to pads | Adapted from EF_TMR32: 2-ch PWM, 10-bit, 1-25 kHz base. Watchdog timer in spare compare channel. REUSE* justification: PWM mode uses compare-match outputs of TMR32; watchdog repurposes overflow interrupt. No source changes to timer core — only wrapper adds PWM output gating. |
| M08 | sram | REUSE | vlsida-openram (BSD-3-Clause) | STRONG | clk_sys | ~40 kGE (macro) | APB slave (via SRAM controller), direct Ibex IMEM/DMEM interface | 4 KB SRAM macro. Zero-wait-state at 50 MHz. Byte/half/word access. |
| M09 | interrupt_ctrl | CREATE | — | — | clk_sys | ~1 kGE | APB slave, 13 peripheral IRQ inputs, 1 CPU IRQ output | Aggregate + mask. Per-source enable/pending. |
| M10 | wb_bridge | CREATE | — | — | clk_wb ↔ clk_sys CDC | ~5 kGE | Wishbone B4 slave (Caravel side) ↔ APB master (internal side) | APB↔Wishbone pipelined bridge + async FIFOs for CDC |
| M11 | caravel_wrapper | CREATE | — | — | clk_sys (+ clk_wb passthrough) | ~5 kGE | Caravel user_clock2, user_reset_n, LA probes, IO pads, power | Top-level wrapper. Instantiates all modules, maps to Caravel user project template. |
| M12 | sys_ctrl | CREATE | — | — | clk_sys | ~2 kGE | APB slave, clock gating control, reset manager | Chip ID, reset cause, clock divider, sleep/wake control. Clock gating cells for idle peripherals. |

## REUSE* Justification — M07 (PWM)

| Field | Detail |
|-------|--------|
| Base IP | fossi-ef-tmr32 (32-bit timer with compare/match, Apache-2.0, STRONG tier) |
| Adaptation | PWM output mode: TMR32 compare-match outputs (cmp[0], cmp[1]) gated to pwm[1:0] pads through an output enable wrapper. Watchdog: TMR32 overflow interrupt routed to reset generator. |
| Changes to base IP | **None.** All adaptations are in a wrapper (pwm_wrapper.v). The EF_TMR32 core is instantiated as-is from the upstream repo. |
| Verification | TMR32 core passes its own test suite. Wrapper verification: PWM duty cycle sweep (0–1023), watchdog timeout/reset, pet-before-timeout. |
| Upstream hash | `fossi-ef-tmr32` @ commit TBD — hash recorded in reuse_manifest.json |

## Interface Matrix

| From Module | To Module | Interface | Protocol | Width | Notes |
|------------|-----------|-----------|----------|-------|-------|
| ibex_core | apb_interconnect | APB master | APB v2.0 | 32-bit addr, 32-bit data | Single-cycle, no wait states |
| apb_interconnect | uart | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0001_0000 |
| apb_interconnect | spi_master | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0001_0100 |
| apb_interconnect | i2c_master | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0001_0200 |
| apb_interconnect | gpio | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0001_0300 |
| apb_interconnect | pwm | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0001_0400 |
| apb_interconnect | interrupt_ctrl | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0001_0500 |
| apb_interconnect | pwm (watchdog) | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0001_0600 |
| apb_interconnect | sys_ctrl | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0001_0700 |
| apb_interconnect | sram | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x0000_0000, 4 KB |
| apb_interconnect | wb_bridge (APB side) | APB slave | APB v2.0 | 32-bit addr, 32-bit data | Base 0x8000_0000 window |
| ibex_core | sram | IMEM/DMEM | Native | 32-bit addr, 32-bit data | Direct SRAM interface (instruction + data) |
| uart | interrupt_ctrl | IRQ | Level | 1 bit | UART TX/RX combined |
| spi_master | interrupt_ctrl | IRQ | Level | 1 bit | SPI transfer done |
| i2c_master | interrupt_ctrl | IRQ | Level | 1 bit | I2C transfer done / error |
| gpio | interrupt_ctrl | IRQ | Level | 8 bits | gpio_irq[7:0] |
| pwm | interrupt_ctrl | IRQ | Level | 1 bit | PWM period match |
| pwm (watchdog) | interrupt_ctrl | IRQ | Level | 1 bit | Watchdog timeout warning |
| interrupt_ctrl | ibex_core | cpu_irq | Level | 1 bit | Aggregated IRQ |
| wb_bridge (WB side) | Caravel harness | Wishbone B4 | Pipelined | 32-bit addr, 32-bit data | Caravel management SoC master |
| uart | caravel_wrapper (IO pads) | uart_tx, uart_rx | Digital | 2 bits | To external pins |
| spi_master | caravel_wrapper (IO pads) | sck, mosi, miso, cs_n[0] | Digital | 4 bits | To external pins |
| i2c_master | caravel_wrapper (IO pads) | scl, sda | Open-drain | 2 bits | To external pins |
| gpio | caravel_wrapper (IO pads) | gpio[7:0] | Digital | 8 bits | To external pins |
| pwm | caravel_wrapper (IO pads) | pwm[1:0] | Digital | 2 bits | To external pins |
| pwm (watchdog) | sys_ctrl | wdt_rst_n | Digital | 1 bit | Internal reset |
| sys_ctrl | ALL (clock gating) | clk_gate_en[N] | Digital | 12 bits | Per-module clock enable |
| caravel_wrapper | user_clock2 | clk_sys | Clock | 1 bit | From Caravel PLL |
| caravel_wrapper | user_reset_n | rst_n | Reset | 1 bit | From Caravel |

## Verification Ownership

| Module | Primary Verification | Owner |
|--------|---------------------|-------|
| ibex_core | riscv-compliance (rv32i), random testbench, GLS | RTL agent (ibex test suite) |
| apb_interconnect | Formal BMC depth 20, directed address decode test | RTL agent |
| uart | Loopback 1M-byte, formal BMC depth 20 | RTL agent |
| spi_master | Loopback Mode 0/3, formal BMC depth 20 | RTL agent |
| i2c_master | I2C slave model, ACK/NACK/arbitration, formal BMC depth 20 | RTL agent |
| gpio | Per-pin loopback, edge IRQ, formal BMC depth 10 | RTL agent |
| pwm | Duty cycle sweep, jitter, watchdog timeout | RTL agent |
| sram | Memory BIST (March C-), zero-wait-state timing with SDF | RTL agent |
| interrupt_ctrl | Directed: all 13 sources, masking, CPU IRQ assertion | RTL agent |
| wb_bridge | Wishbone checker, APB checker, CDC formal | RTL agent |
| caravel_wrapper | Caravel precheck, GDS DRC, LVS, antenna | RTL agent |
| sys_ctrl | Sleep/wake sequence, clock gating verification, reset cause | RTL agent |
| TOP (integration) | Full-chip GLS, Caravel precheck, user project testbench | RTL agent |
