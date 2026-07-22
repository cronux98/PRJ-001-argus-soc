# Third-Party Components — PRJ-001 ARGUS SoC

This project integrates open-source hardware IP from multiple sources. Each component retains its original license. This file documents attribution as required by those licenses.

## RISC-V Core

**Component:** Ibex RISC-V Core (RV32IMC, 5-stage pipeline)
**Source:** lowRISC — https://github.com/lowRISC/ibex
**License:** Apache 2.0
**Copyright:** lowRISC contributors, ETH Zürich, University of Bologna
**Files:** `rtl/ibex_core*.v`, `rtl/alu.v`, `rtl/branch_unit.v`, `rtl/ctrl_unit.v`, `rtl/reg_file.v`, `rtl/imm_gen.v`, `rtl/forwarding_unit.v`, `rtl/hazard_unit.v`, `rtl/pc.v`, `rtl/if_id.v`, `rtl/id_ex.v`, `rtl/ex_mem.v`, `rtl/mem_wb.v`

## Efabless IP Library

The following peripheral IP blocks are from the Efabless IP library:

| Block | Source File | License |
|-------|-------------|---------|
| EF_UART | `rtl/EF_UART.v`, `rtl/EF_UART_APB.v` | Apache 2.0 |
| EF_SPI | `rtl/EF_SPI.v`, `rtl/EF_SPI_APB.v` | Apache 2.0 |
| EF_I2C | `rtl/EF_I2C_APB.v`, `rtl/i2c_init.v` | Apache 2.0 |
| EF_GPIO8 | `rtl/EF_GPIO8.v`, `rtl/EF_GPIO8_APB.v` | Apache 2.0 |
| EF_TMR32 | `rtl/EF_TMR32.v`, `rtl/EF_TMR32_APB.v` | Apache 2.0 |
| EF_WDT32 | `rtl/EF_WDT32.v`, `rtl/EF_WDT32_APB.v` | Apache 2.0 |
| ef_util_lib | `rtl/ef_util_lib.v` | Apache 2.0 |

**Source:** Efabless IP — https://github.com/efabless/EF_IPs
**License:** Apache 2.0
**Copyright:** Efabless Corporation

## Custom IP (Original Work)

The following modules are original designs created by the Hermes agentic ASIC framework:

| Block | File |
|-------|------|
| argus_soc_chip (top-level with pad ring) | `rtl/top/argus_soc_chip.v` |
| argus_soc (digital core) | `rtl/argus_soc.v` |
| apb_interconnect | `rtl/apb_interconnect.v` |
| wb_bridge | `rtl/wb_bridge.v` |
| interrupt_ctrl | `rtl/interrupt_ctrl.v` |
| pwm_wrapper | `rtl/pwm_wrapper.v` |
| spi_master | `rtl/spi_master.v` |
| i2c_master (3 variants) | `rtl/i2c_master*.v` |
| axis_fifo | `rtl/axis_fifo.v` |
| sys_ctrl | `rtl/sys_ctrl.v` |
| io_pads | `rtl/io_pads/` |

**License:** Apache 2.0 (same as rest of project)

## PDK

**Component:** SkyWater sky130_fd_sc_hd (130nm open-source PDK)
**Source:** SkyWater Technology / Google — https://github.com/google/skywater-pdk
**License:** Apache 2.0

## Toolchain

The following open-source EDA tools were used by the agentic framework (not distributed in this repository):

| Tool | Version | License |
|------|---------|---------|
| Yosys | 0.62 | ISC |
| OpenROAD | 2026-02-17 | BSD 3-Clause |
| Magic VLSI | 8.3.623 | MIT-style |
| Klayout | 0.30.7 | GPL |
| Netgen | 1.5.316 | GPL |
| Icarus Verilog | s20250103 | GPL |
| Verilator | 5.044 | LGPL |

## Framework

The agentic workflow that produced this chip uses the Hermes agent framework and the Vera ASIC orchestration system. No human wrote RTL, testbenches, SDC constraints, or invoked EDA tools — all design artifacts were produced autonomously by Claude Opus 4.8 subagents working from project templates.

---

*If you believe any attribution is missing or incorrect, please open an issue.*
