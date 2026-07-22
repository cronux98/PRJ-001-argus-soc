# 05_firmware_stage — Index
**Project:** PRJ-001 (Argus) | **Agent:** firmware-engineer (Hermes) | **Skills:** firmware-stage, fw-memory-map-contract, fw-bootrom, fw-bsp-assembly, fw-driver-gen

## Artifacts
| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | bsp/link.ld | Linker script (4KB SRAM, 0x00000000 entry) | ✅ |
| 2 | bsp/include/soc.h | SoC header: memory regions, peripheral bases, IRQ map | ✅ |
| 3 | bsp/include/uart_reg.h | UART register map (0x00010000) | ✅ |
| 4 | bsp/include/spi_reg.h | SPI register map (0x00010100) | ✅ |
| 5 | bsp/include/i2c_reg.h | I2C register map (0x00010200) | ✅ |
| 6 | bsp/include/gpio_reg.h | GPIO register map (0x00010300) | ✅ |
| 7 | bsp/include/pwm_reg.h | PWM register map (0x00010400) | ✅ |
| 8 | bsp/include/intctrl_reg.h | Interrupt controller register map (0x00010500) | ✅ |
| 9 | bsp/include/watchdog_reg.h | Watchdog register map (0x00010600) | ✅ |
| 10 | bsp/include/sysctrl_reg.h | System control register map (0x00010700) | ✅ |
| 11 | bsp/Makefile | Build system (rv32i_zicsr, -Os, gc-sections) | ✅ |
| 12 | bsp/bsp_manifest.json | Per-file provenance manifest | ✅ |
| 13 | bootrom/crt0.S | Startup code: stack init, BSS clear, trap vector, IRQ dispatch | ✅ |
| 14 | bootrom/bootrom.hex | Intel HEX firmware image | ✅ |
| 15 | bootrom/bootrom.bin | Binary firmware image | ✅ |
| 16 | bootrom/bootrom_report.json | Boot ROM budget report (2466/4096, 60.2%) | ✅ |
| 17 | fw/drivers/uart/uart_driver.h + .c | UART polled driver (115200 bps, 8N1) | ✅ |
| 18 | fw/drivers/spi/spi_driver.h + .c | SPI master driver (Mode 0/3) | ✅ |
| 19 | fw/drivers/i2c/i2c_driver.h + .c | I2C master driver (100/400 kHz) | ✅ |
| 20 | fw/drivers/gpio/gpio_driver.h + .c | GPIO driver (8-pin, per-pin IRQ) | ✅ |
| 21 | fw/drivers/pwm/pwm_driver.h + .c | PWM driver (2ch, 10-bit) | ✅ |
| 22 | fw/drivers/watchdog/watchdog_driver.h + .c | Watchdog driver (24-bit, pet) | ✅ |
| 23 | fw/drivers/sysctrl/sysctrl_driver.h + .c | System control driver (CHIP_ID, sleep) | ✅ |
| 24 | fw/drivers/intctrl/intctrl_driver.h + .c | Interrupt controller driver (13 sources) | ✅ |
| 25 | fw/drivers/sensor/sensor_poll.h + .c | Sensor polling template (I2C/SPI/UART report) | ✅ |
| 26 | fw/main.c | Application entry: init, self-test, sensor loop | ✅ |
| 27 | fw_build.log | Build log with compiler version + full command lines | ✅ |
| 28 | verify_fw_artifacts.sh | Exit gate script (14 checks) | ✅ |

## Build
- **Toolchain:** riscv32-unknown-elf-gcc 14.2.1 at /opt/OpenROAD/riscv/gcc14-no-zcmp/bin/
- **Flags:** -march=rv32i_zicsr -mabi=ilp32 -Os -ffunction-sections -fdata-sections
- **Result:** 2466 bytes text, 0 data, 0 bss → 60.2% of 4KB SRAM
- **ROM budget:** PASS (2466/4096)

## Drivers
| Peripheral | .h | .c | Compiled | Self-test | RTL Cosim |
|-----------|----|----|----------|-----------|-----------|
| UART | ✅ | ✅ | ✅ | register readback | ⚠️ BLOCKED |
| SPI | ✅ | ✅ | ✅ | register readback | ⚠️ BLOCKED |
| I2C | ✅ | ✅ | ✅ | register readback | ⚠️ BLOCKED |
| GPIO | ✅ | ✅ | ✅ | register readback | ⚠️ BLOCKED |
| PWM | ✅ | ✅ | ✅ | register readback | ⚠️ BLOCKED |
| Watchdog | ✅ | ✅ | ✅ | register readback | ⚠️ BLOCKED |
| SysCtrl | ✅ | ✅ | ✅ | register readback | ⚠️ BLOCKED |
| IntCtrl | ✅ | ✅ | ✅ | register readback | ⚠️ BLOCKED |
| Sensor | ✅ | ✅ | ✅ | — | ⚠️ BLOCKED |

## Interrupt Vector Table
- 13 sources → 1 CPU IRQ (direct mode, mtvec → _trap_handler)
- crt0.S unified handler dispatches to weak ISR stubs
- ISR stubs: isr_uart, isr_spi, isr_i2c, isr_gpio, isr_pwm, isr_wdt

## Validation
- **Gate:** verify_fw_artifacts.sh → 14/14 PASS
- **Report:** [../00_validation_report/firmware_validation.md](../00_validation_report/firmware_validation.md)
- **Postmortem:** [../11_postmortem_audit/firmware_postmortem.md](../11_postmortem_audit/firmware_postmortem.md)
