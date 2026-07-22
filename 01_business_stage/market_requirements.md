# Market Requirements — PRJ-001 (Argus) v0

## MoSCoW Feature Classification

### MUST (Minimum Viable Product — cannot ship without)

| ID | Feature | Acceptance Criteria | IP Source |
|----|---------|---------------------|-----------|
| REQ-001 | RV32I processor core (Ibex) | Boots firmware from SRAM, executes RISC-V RV32I ISA correctly, passes riscv-compliance suite. Target 50 MHz, fallback 25 MHz. | lowrisc-ibex (STRONG, Apache-2.0) |
| REQ-002 | UART TX/RX | 115200 bps, 8N1, full-duplex. Loopback test passes with ≤1% error rate at 50 MHz system clock. FIFO depth ≥ 8 bytes. | fossi-ef-uart (STRONG, Apache-2.0) |
| REQ-003 | SPI master | Mode 0 and 3, up to 12.5 MHz SCLK (f_sys/4 at 50 MHz). Single-byte and burst transfers. FIFO depth ≥ 8 bytes. | fossi-ef-spi (STRONG, Apache-2.0) |
| REQ-004 | I2C master | 100 kHz (standard) and 400 kHz (fast) modes. 7-bit addressing. Multi-byte read/write with repeated start. ACK/NACK handling. | fossi-ef-i2c (STRONG, Apache-2.0) |
| REQ-005 | GPIO (8-12 pins) | Per-pin direction (input/output), output value, input read. Per-pin interrupt on rising/falling/both edges. | fossi-ef-gpio8 (STRONG, Apache-2.0) |
| REQ-006 | PWM (2 channels) | 8-10 bit resolution, 1 kHz to 25 kHz base frequency range. Independent duty cycle per channel. | fossi-ef-tmr32 (STRONG, Apache-2.0, timer repurposed as PWM) |
| REQ-007 | SRAM (2-4 KB) | Byte/half/word read/write at 50 MHz. Verified with memory BIST (March C-). Zero wait states at target frequency. | vlsida-openram (STRONG, BSD-3-Clause) |
| REQ-008 | APB internal bus | All peripherals accessible via memory-mapped APB. Single-cycle read/write at 50 MHz. | CREATE (APB interconnect) |
| REQ-009 | Caravel Wishbone bridge | APB↔Wishbone bridge for Caravel harness. Management SoC can read/write all APB peripherals. | CREATE (bridge logic) |
| REQ-010 | Caravel harness integration | Wrapper instantiates user project, passes precheck, meets Caravel pin constraints. GDS fits in 2,800×1,760 µm area. | CREATE (wrapper) |

### SHOULD (Important but not blocking MVP)

| ID | Feature | Justification |
|----|---------|---------------|
| REQ-011 | Interrupt controller | Aggregate peripheral IRQs into single CPU IRQ. Enables efficient sensor polling without busy-wait. |
| REQ-012 | SPI slave mode | Allows sensor-hub to act as SPI peripheral for external MCU. Useful for dual-processor architectures. |
| REQ-013 | UART hardware flow control (RTS/CTS) | Avoids buffer overrun at high throughput. Important for 115200+ bps sustained transfers. |
| REQ-014 | Watchdog timer | System reliability — resets processor on firmware hang. |
| REQ-015 | Sensor data FIFO/DMA | Hardware-assisted sensor data movement from SPI/I2C to SRAM. Reduces CPU load. |

### COULD (Nice to have, include only if trivial)

| ID | Feature | Justification |
|----|---------|---------------|
| REQ-016 | I2C slave mode | Allow external host to query sensor-hub as I2C peripheral. |
| REQ-017 | UART baud rate auto-detection | Plug-and-play host connection without firmware configuration. |
| REQ-018 | On-die temperature sensor (ring oscillator) | Chip health monitoring, no external sensor needed for basic temperature. |
| REQ-019 | CRC hardware accelerator | Data integrity checking for sensor frames without CPU overhead. |

### WON'T (Explicitly excluded to prevent scope creep)

| ID | Feature | Rationale |
|----|---------|-----------|
| WONT-001 | Analog front-end (ADC, op-amp) | Sky130A analog requires separate AMS flow, different PDK, different expertise. Digital-only tapeout. |
| WONT-002 | Wireless (BLE, Zigbee, LoRa) | External module via UART/SPI. RF design is a separate domain with FCC/CE certification. |
| WONT-003 | Flash memory | Sky130A has no embedded flash. External SPI flash or Caravel management SoC loads firmware. |
| WONT-004 | Hardware security (AES, SHA, TRNG) | Out of scope for environmental sensing. Security is OpenTitan's domain. |
| WONT-005 | RISC-V M extension (multiply/divide) | RV32I only. M extension adds ~15% area to Ibex. Not needed for sensor polling math. |
| WONT-006 | Linux-capable MMU | Sensor hub runs bare-metal or RTOS, not Linux. MMU is massive area overhead for no benefit. |

## Technical Constraints from Market Research

### Bus Protocol
- **Internal:** APB v2.0 (ARM IHI0024C). Simple, low-power, well-suited for peripheral register access.
- **External (Caravel):** Wishbone B4 pipelined. Bridge translates APB transactions to Wishbone at the Caravel boundary.
- **Justification:** All comparable designs (OpenTitan, NEORV32, Caravel user projects) use a peripheral bus separated from the CPU native bus. APB is the simplest standard with proven open-source implementations.

### Memory Requirements
- **SRAM:** 2-4 KB. Derived from TI MSP430FR2355 (4 KB), STM32L011D4 (2 KB). A sensor frame is ~32 bytes (timestamp + sensor ID + range + value). 50-frame buffer = 1.6 KB. Stack + heap = ~1 KB. Total: ~3 KB. Headroom for firmware data = 1 KB.
- **No ROM (boot from SRAM):** Caravel management SoC loads firmware into SRAM via Wishbone. Avoids ROM mask costs on MPW shuttle.

### I/O Requirements
- **Total pins:** ~20-25 digital GPIO (multiplexed with UART TX/RX, SPI SCK/MOSI/MISO/CS, I2C SCL/SDA, PWM×2). Within Caravel's 38 user IO pads.
- **Voltage:** 3.3V (sky130A IO Pad voltage). Compatible with standard sensor modules.
- **External crystal:** Optional — Caravel provides system clock.

### Clock Frequency
- **Target:** 50 MHz on sky130_fd_sc_hd. Achievable per OpenTitan's 100 MHz demonstration with same core on same process.
- **Fallback:** 25 MHz. Conservative, nearly guaranteed. Still sufficient for 115200 UART + 400 kHz I2C sensor polling.
- **External interface clocks:** I2C/SPI/UART derived from system clock divider — no separate PLL needed.

### Power Budget
- **Active (50 MHz, all peripherals):** ≤10 mW conservative, ≤5 mW target. Comparable scaled baselines: 2.6-5 mW.
- **Sleep (clock-gated, SRAM retained):** ≤50 µW conservative, ≤10 µW target.
- **Battery life (example):** 2000 mAh Li-Ion at 3.7V = 7.4 Wh. At 5 mW active, 10% duty cycle (10 ms on, 90 ms off) = 0.5 mW average → ~617 days. At 10 µW sleep + 5 mW active, 0.1% duty cycle (1 s poll, 999 s sleep) → ~3 years.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Ibex synthesis fails to close timing at 50 MHz | Low | Medium | 25 MHz fallback is defined and validated; OpenTitan proves 100 MHz on same process+core. |
| OpenRAM SRAM macro generation fails for sky130A | Low | High | OpenRAM has sky130A support; fallback to register-file-based SRAM (area penalty but functional). |
| APB↔Wishbone bridge bugs cause Caravel integration failures | Medium | Medium | Early standalone bridge verification; Caravel precheck tool catches protocol violations. |
| Multi-IP integration uncovers incompatibilities (bus width, clock domains) | Medium | Medium | All EF_ IP uses same Wishbone B4 interface convention; APB is standardized. Integration testbench before tapeout. |
| Power target missed (higher-than-expected leakage in sky130A) | Medium | Low | Sky130A is a mature process; OpenTitan measurements provide reference. Power is a nice-to-have metric, not a functional blocker. |
| Caravel shuttle slot unavailable or delayed | Low | High | Multiple shuttle providers (chipIgnite, Efabless, TinyTapeout). Plan 1 quarter buffer. |
| MPW shuttle cost exceeds budget | Low | High | Caravel MPW slots range $50-$300 via TinyTapeout/Efabless academic programs. Budget $500 for contingency. |
