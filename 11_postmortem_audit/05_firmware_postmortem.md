# Stage 05: Firmware — Postmortem

**Date:** 2026-07-21
**Project:** PRJ-001 Argus
**Stage Directory:** /home/smdadmin/hermes_workspace/projects/PRJ-001/v0/05_firmware_stage
**Verdict:** PASS (17/17) — audit cost $0.00 (recorded)

## What Went Well
- **Fully buildable image, pinned toolchain.** `fw_build.log` confirms `riscv32-unknown-elf-gcc 14.2.1` from `/opt/OpenROAD/riscv/gcc14-no-zcmp/bin/`, `-march=rv32i_zicsr -mabi=ilp32` — correct for Ibex RV32I.
- **Tight, honest ROM budget.** `bootrom_report.json`: 2,466 / 4,096 bytes (60.2%), sourced `GENERATED-FROM: memory_map.json`. `size.txt` and `.elf` agree (2466 text / 0 data / 0 bss).
- **Address contract holds end-to-end.** All 8 peripheral bases in `soc.h` match `memory_map.json` exactly (UART 0x00010000 … SYSCTRL 0x00010700); 13-source IRQ vector table in `crt0.S` matches INTCTRL bit defs.
- **Complete driver set.** 9 peripheral drivers (uart, spi, i2c, gpio, pwm, watchdog, sysctrl, intctrl, sensor), each with `.c/.h` + `results.xml`; BSP manifest catalogues 35 files with provenance banners.
- **Honest blocked-status reporting.** RTL cosim was genuinely blocked (no SoC top RTL at this stage) and was reported as BLOCKED rather than faked — the §G.6 honest-stub norm.

## What Went Wrong
- **No RTL-level driver verification.** `tb-fw-bringup/results.xml` is BLOCKED — drivers validated only by compile + `main.c` register-readback self-tests, not against real RTL. Genuine driver/hardware bugs (timing, register side-effects) could survive to integration.
- **Caravel management firmware split off.** `caravel_fw/` exists but management-FW bring-up (`mgmt_fw.hex` referenced in precheck) was deferred to the Caravel stage.
- **Self-tests inlined to save SRAM.** `quick_test` folded into `main.c` rather than per-driver TBs — pragmatic under the 4 KB budget but reduces isolation.

## Root Causes
- **Ordering dependency:** firmware ran parallel to/ahead of SoC top-level RTL availability, so cosim had no DUT. This is a pipeline sequencing constraint, not a firmware defect.
- **4 KB SRAM ceiling** forced size-conscious choices (inlined tests, `-Os`, `--gc-sections`).

## Fixes Applied
- No rework iterations — stage passed the first audit 17/17. The size and address-contract checks passed without adjustment.

## Iterations
- 0 reworks. Single audit pass.

## Framework Improvements Recommended
- **Dispatch firmware cosim after SoC top RTL exists** (or provide a minimal top stub) so `tb-fw-bringup` can actually exercise drivers instead of returning BLOCKED — this is the recurring "RTL cosim blocked" pattern.
- Add an explicit gate that firmware BLOCKED cosim status must be re-run and cleared post-integration before tapeout, so the deferral cannot be silently forgotten.
- Standardize the BSP manifest filename (`bsp_manifest.json` vs `bsp/manifest.json`) per rubric §6b.2 to remove the lint ambiguity.

## Metrics
- Duration: 2026-07-20 ~11:05–11:15 · Cost: $0.00 (recorded) · Rework: 0
- Image: 2,466 B / 4,096 B (60.2%) · Drivers: 9 · Register headers: 8 · IRQ sources: 13
- Known deferral: RTL cosim + Caravel mgmt-FW bring-up
