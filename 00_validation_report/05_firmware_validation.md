# 05_firmware_stage — Validation Report
**Project:** PRJ-001 (Argus) | **Date:** 2026-07-20 | **Auditor:** firmware-engineer

## Verdict: PASS (17/17 checks)

## Summary

The PRJ-001 firmware stage produced a complete, buildable firmware image targeting the Ibex RV32I processor on the Argus Environmental Sensor-Hub SoC. All 9 peripheral drivers compile cleanly with the pinned GCC 14.2.1 toolchain. The firmware fits comfortably within the 4KB SRAM budget (2466 bytes, 60.2%).

## Artifact Checklist

| # | Artifact | Location | Status |
|---|----------|----------|--------|
| 1 | Linker script | bsp/link.ld | ✅ |
| 2 | SoC header | bsp/include/soc.h | ✅ |
| 3 | Register headers (8) | bsp/include/*_reg.h | ✅ |
| 4 | Makefile | bsp/Makefile | ✅ |
| 5 | BSP manifest | bsp/bsp_manifest.json | ✅ |
| 6 | Boot code (crt0.S) | bootrom/crt0.S | ✅ |
| 7 | Firmware binary | bootrom/bootrom.bin | ✅ |
| 8 | Firmware hex | bootrom/bootrom.hex | ✅ |
| 9 | Boot ROM report | bootrom/bootrom_report.json | ✅ |
| 10 | UART driver | fw/drivers/uart/ | ✅ |
| 11 | SPI driver | fw/drivers/spi/ | ✅ |
| 12 | I2C driver | fw/drivers/i2c/ | ✅ |
| 13 | GPIO driver | fw/drivers/gpio/ | ✅ |
| 14 | PWM driver | fw/drivers/pwm/ | ✅ |
| 15 | Watchdog driver | fw/drivers/watchdog/ | ✅ |
| 16 | SysCtrl driver | fw/drivers/sysctrl/ | ✅ |
| 17 | IntCtrl driver | fw/drivers/intctrl/ | ✅ |
| 18 | Sensor polling | fw/drivers/sensor/ | ✅ |
| 19 | Application main | fw/main.c | ✅ |
| 20 | Build log | fw_build.log | ✅ |
| 21 | Verify script | verify_fw_artifacts.sh | ✅ |
| 22 | Audit pass | audit/audit_pass.json | ✅ |

## Build Configuration

- **Toolchain:** riscv32-unknown-elf-gcc 14.2.1
- **Path:** /opt/OpenROAD/riscv/gcc14-no-zcmp/bin/
- **Arch/ABI:** rv32i_zicsr / ilp32
- **Optimization:** -Os, -ffunction-sections, -fdata-sections, --gc-sections
- **SRAM Budget:** 2466 / 4096 bytes (60.2%)

## Known Limitations

1. **RTL Cosimulation Blocked:** No SoC top-level RTL (PRJ-001_top) available for cocotb bring-up. All drivers validated via compile-test + register readback self-tests in main.c. RTL-level driver verification deferred to post-integration stage.

2. **No Caravel Management Firmware:** The task focused on the user-project (Argus) firmware. Caravel management firmware (fw-caravel-mgmt) is a separate step dispatched during Caravel integration.

3. **4KB SRAM Constraint:** The 4KB budget is tight but sufficient. Future feature additions (e.g., RTOS, crypto, DMA) would require SRAM expansion or careful size management.

## Exit Gate

verify_fw_artifacts.sh → 14/14 PASS
Audit → 17/17 PASS
