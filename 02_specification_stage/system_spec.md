# System Requirements Specification (SRS)
## PRJ-001 (Argus) Environmental Sensor-Hub SoC — Iteration 1

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-07-20 | Systems Planner (spec-product-engineer) | Initial SRS from business stage inputs |

---

## 1. Introduction

### 1.1 Purpose

This SRS defines the complete functional, performance, interface, behavioral, and constraint requirements for the PRJ-001 (Argus) Environmental Sensor-Hub SoC. It serves as the contractual specification that all downstream design, RTL, verification, and tapeout activities trace back to. Every requirement is tagged with a unique ID (SYS-xx-NNN) for full lifecycle traceability.

### 1.2 Scope

**In scope for Iteration 1:**

- RV32I RISC-V processor core (Ibex "maxperf" configuration)
- APB v2.0 internal peripheral bus
- UART TX/RX (115200 bps, 8N1, full-duplex, 8-byte FIFO)
- SPI master (Mode 0/3, up to 12.5 MHz SCLK, 8-byte FIFO)
- I2C master (100/400 kHz, 7-bit addressing, multi-byte read/write with repeated start)
- GPIO (8 pins, per-pin direction/interrupt, edge-detect)
- PWM (2 channels, 10-bit resolution, 1–25 kHz base frequency)
- 4 KB SRAM (OpenRAM, zero-wait-state at 50 MHz)
- Basic interrupt controller (aggregate peripheral IRQs → single CPU IRQ)
- APB↔Wishbone B4 bridge (Caravel harness interface)
- Caravel wrapper (top-level integration, precheck compliance)
- Power management: clock gating for idle peripherals, sleep mode with SRAM retention

**Explicitly out of scope (deferred to future iterations):**

| Feature | Rationale |
|---------|-----------|
| RISC-V M extension (multiply/divide) | Adds ~15% Ibex area; not needed for sensor-polling math |
| SPI slave mode (REQ-012) | SHOULD priority; useful for dual-MCU but not blocking MVP |
| UART hardware flow control RTS/CTS (REQ-013) | SHOULD priority; FW-based flow control adequate for 115200 bps |
| Sensor data DMA/FIFO (REQ-015) | SHOULD priority; FW-based polling viable at 50 MHz |
| I2C slave mode (REQ-016) | COULD priority; external host can use UART/SPI instead |
| UART baud rate auto-detection (REQ-017) | COULD priority; FW configuration sufficient |
| On-die temperature sensor (REQ-018) | COULD priority; external I2C temp sensors readily available |
| CRC hardware accelerator (REQ-019) | COULD priority; FW CRC at 50 MHz viable for sensor frames |
| Analog front-end (ADC, op-amp) (WONT-001) | Separate AMS flow, different PDK, different expertise |
| Wireless (BLE, Zigbee, LoRa) (WONT-002) | External module via UART/SPI; RF requires FCC/CE certification |
| Flash memory (WONT-003) | No embedded flash on sky130A; Caravel mgmt SoC loads FW via SPI flash |
| Hardware security (AES, SHA, TRNG) (WONT-004) | Out of scope for environmental sensing |
| Linux-capable MMU (WONT-006) | Sensor hub runs bare-metal/RTOS, not Linux |

### 1.3 Definitions, Acronyms, Abbreviations

| Term | Definition |
|------|------------|
| APB | Advanced Peripheral Bus (ARM IHI0024C v2.0) — low-power, simple peripheral bus |
| Caravel | Efabless harness SoC providing clock, reset, power, GPIO, and management processor on sky130A MPW shuttles |
| CDC | Clock Domain Crossing — synchronizing signals between asynchronous clock domains |
| EF_ | Efabless FOSSi — family of open-source peripheral IP blocks (UART, SPI, I2C, GPIO, TMR32) |
| GPIO | General Purpose Input/Output |
| Ibex | Open-source 32-bit RISC-V processor core (lowRISC, Apache-2.0) |
| MPW | Multi-Project Wafer — shared shuttle run for prototyping |
| OpenRAM | Open-source SRAM memory compiler (VLSIDA, BSD-3-Clause) |
| PDK | Process Design Kit — sky130A (SkyWater 130nm) |
| PPA | Power, Performance, Area |
| PWM | Pulse Width Modulation |
| RV32I | RISC-V 32-bit Integer ISA (base integer instruction set) |
| sky130A | SkyWater 130nm open-source PDK |
| SoC | System on Chip |
| SRAM | Static Random Access Memory |
| Wishbone B4 | FOSSi open-source bus standard (pipelined mode) |

### 1.4 References

| # | Document | Source |
|---|----------|--------|
| 1 | RISC-V ISA Specification v2.1 (RV32I) | https://riscv.org/technical/specifications/ |
| 2 | ARM IHI0024C — AMBA APB Protocol v2.0 | ARM Ltd. |
| 3 | Wishbone B4 Specification | https://opencores.org/howto/wishbone |
| 4 | I2C Bus Specification v3.0 (NXP UM10204) | https://www.nxp.com/docs/en/user-guide/UM10204.pdf |
| 5 | OpenTitan EarlGrey Specification | https://opentitan.org/book/hw/top_earlgrey/doc/specification.html |
| 6 | Ibex RISC-V Core — lowRISC | https://github.com/lowRISC/ibex (IP-INDEX: lowrisc-ibex, STRONG) |
| 7 | OpenRAM — VLSIDA | https://github.com/VLSIDA/OpenRAM (IP-INDEX: vlsida-openram, STRONG) |
| 8 | FOSSi Efabless IP Library | https://github.com/efabless/fossi-ef-uart (IP-INDEX: fossi-ef-*, STRONG) |
| 9 | Caravel User Project Harness | https://github.com/efabless/caravel_user_project |
| 10 | SkyWater sky130A PDK | https://github.com/google/skywater-pdk |
| 11 | PRJ-001 market_validation.md (Stage 0 PASS) | ../01_business_stage/market_validation.md |
| 12 | PRJ-001 market_requirements.md (MoSCoW) | ../01_business_stage/market_requirements.md |
| 13 | PRJ-001 baseline_metrics.json (PPA targets) | ../01_business_stage/baseline_metrics.json |

---

## 2. System Overview

### 2.1 Context Diagram

```
                          ┌─────────────────────────────────────┐
                          │         CARAVEL HARNESS              │
                          │  ┌───────────────────────────────┐  │
  ┌──────────┐  UART      │  │                               │  │
  │ Host PC  │◄──────────►│  │    ┌─────────────────────┐    │  │
  │ (debug)  │  TX/RX     │  │    │   PRJ-001 (Argus)   │    │  │
  └──────────┘            │  │    │  Environmental       │    │  │
                          │  │    │  Sensor-Hub SoC      │    │  │
  ┌──────────┐  SPI       │  │    │                      │    │  │
  │ SPI      │◄──────────►│  │    │  ┌───────┐           │    │  │
  │ Sensor   │  SCK/MOSI  │  │    │  │ Ibex  │           │    │  │
  │ (e.g.    │  /MISO/CS  │  │    │  │ RV32I │           │    │  │
  │  accel)  │            │  │    │  └──┬────┘           │    │  │
  └──────────┘            │  │    │     │ APB            │    │  │
                          │  │    │  ┌──┴──────────┐    │    │  │
  ┌──────────┐  I2C       │  │    │  │ APB Inter-   │    │    │  │
  │ I2C      │◄──────────►│  │    │  │ connect      │    │    │  │
  │ Sensors  │  SCL/SDA   │  │    │  └──┬──┬──┬──┬──┘    │    │  │
  │ (temp,   │            │  │    │     │  │  │  │        │    │  │
  │  humid,  │            │  │    │  ┌──┴┐┌┴┐┌┴┐┌┴┐      │    │  │
  │  press)  │            │  │    │  │U  ││S││I││G│      │    │  │
  └──────────┘            │  │    │  │A  ││P││2││P│      │    │  │
                          │  │    │  │R  ││I││C││I│      │    │  │
  ┌──────────┐  GPIO      │  │    │  │T  ││ ││ ││O│      │    │  │
  │ Actuators│◄──────────►│  │    │  │   ││ ││ ││ │      │    │  │
  │ LEDs     │  8 pins    │  │    │  └──┬┘└─┘└─┘└┬┘      │    │  │
  └──────────┘            │  │    │     │         │       │    │  │
                          │  │    │  ┌──┴┐     ┌──┴──┐    │    │  │
  ┌──────────┐  PWM       │  │    │  │PWM│     │SRAM │    │    │  │
  │ Fan/Motor│◄──────────►│  │    │  │2ch│     │4 KB │    │    │  │
  │ Driver   │  2 ch      │  │    │  └───┘     └─────┘    │    │  │
  └──────────┘            │  │    │                      │    │  │
                          │  │    │  ┌──────────────┐    │    │  │
  ┌──────────┐  Wishbone  │  │    │  │ APB↔Wishbone │    │    │  │
  │ Caravel  │◄──────────►│  │    │  │ Bridge       │    │    │  │
  │ Mgmt SoC │  B4        │  │    │  └──────────────┘    │    │  │
  └──────────┘            │  │    └─────────────────────┘    │  │
                          │  │                               │  │
                          │  └───────────────────────────────┘  │
                          │                                     │
                          │  clk, rst_n, power, 38 user I/O     │
                          └─────────────────────────────────────┘
```

### 2.2 Use Cases

| UC | Name | Description | Trigger | Key Modules |
|----|------|-------------|---------|-------------|
| UC-1 | Sensor Poll | Read environmental sensor values (temp, humidity, pressure) over I2C at configurable intervals | Firmware timer or external trigger | I2C, SRAM, APB |
| UC-2 | SPI Data Dump | Read high-speed sensor data over SPI (burst mode), store in SRAM buffer | Firmware command | SPI, SRAM, APB |
| UC-3 | Host Report | Transmit buffered sensor data over UART to host PC or gateway | Firmware timer or buffer threshold | UART, SRAM, APB |
| UC-4 | Actuator Control | Drive fan/motor speed via PWM based on sensor thresholds | Sensor value exceeding threshold | PWM, GPIO |
| UC-5 | GPIO Alert | Raise interrupt on GPIO edge (e.g., external alert, button press) | External GPIO edge event | GPIO, Interrupt Controller |
| UC-6 | Caravel Management Access | Caravel management SoC reads/writes Argus memory/peripherals via Wishbone bridge | Caravel management command | Wishbone Bridge, APB |
| UC-7 | Deep Sleep | Enter low-power sleep with SRAM retention, wake on GPIO edge or timer | Firmware sleep command | Clock gating, GPIO, PWM |

### 2.3 Block Decomposition (Overview)

| Block | Function | Source |
|-------|----------|--------|
| ibex_core | RV32I processor, 2-stage pipeline, "maxperf" config | REUSE (lowrisc-ibex, STRONG) |
| apb_interconnect | APB v2.0 bus fabric — address decode, mux, routing | CREATE |
| uart | Full-duplex UART, 115200 bps, 8-byte FIFO | REUSE (fossi-ef-uart, STRONG) |
| spi_master | SPI mode 0/3 master, up to f_sys/4 SCLK, 8-byte FIFO | REUSE (fossi-ef-spi, STRONG) |
| i2c_master | I2C 100/400 kHz master, 7-bit addr, multi-byte, repeated start | REUSE (fossi-ef-i2c, STRONG) |
| gpio | 8-pin GPIO, per-pin direction/IRQ, edge detect | REUSE (fossi-ef-gpio8, STRONG) |
| pwm | 2-channel PWM, 10-bit, derived from fossi-ef-tmr32 | REUSE* (fossi-ef-tmr32, STRONG, adapted) |
| sram | 4 KB OpenRAM SRAM macro, zero-wait-state | REUSE (vlsida-openram, STRONG) |
| interrupt_ctrl | Aggregate peripheral IRQs → single CPU IRQ, per-source mask | CREATE |
| wb_bridge | APB↔Wishbone B4 pipelined bridge for Caravel | CREATE |
| caravel_wrapper | Top-level Caravel harness integration | CREATE |
| sys_ctrl | System control: clock divider, reset manager, chip ID | CREATE |

---

## 3. Functional Requirements (SYS-FR-xxx)

| ID | Requirement | Rationale | Priority |
|----|-------------|-----------|----------|
| SYS-FR-001 | The system shall execute RISC-V RV32I base integer instruction set (ISA v2.1) | Ibex core provides the programmable control plane for sensor polling and data processing | MUST |
| SYS-FR-002 | The system shall provide full-duplex UART communication at 115200 bps with 8N1 framing | Host reporting and debug console; REQ-002 from MoSCoW | MUST |
| SYS-FR-003 | The system shall provide SPI master capability in Mode 0 (CPOL=0, CPHA=0) and Mode 3 (CPOL=1, CPHA=1) | High-speed sensor readout; REQ-003 from MoSCoW | MUST |
| SYS-FR-004 | The system shall provide I2C master capability at 100 kHz (standard) and 400 kHz (fast) with 7-bit addressing | Multi-sensor communication on shared bus; REQ-004 from MoSCoW | MUST |
| SYS-FR-005 | The system shall provide 8 GPIO pins with per-pin direction control (input/output) and per-pin interrupt on configurable edge (rising/falling/both) | Actuator control, external alert detection; REQ-005 from MoSCoW | MUST |
| SYS-FR-006 | The system shall provide 2 independent PWM channels with configurable period and duty cycle | Fan/motor/actuator control with smooth analog-like output; REQ-006 from MoSCoW | MUST |
| SYS-FR-007 | The system shall provide 4 KB of byte-addressable SRAM accessible by the CPU with zero wait states at 50 MHz | Firmware code, stack, heap, and sensor data buffer; REQ-007 from MoSCoW | MUST |
| SYS-FR-008 | The system shall provide an APB v2.0 internal bus interconnecting the CPU to all peripherals | Standardized peripheral register access; REQ-008 from MoSCoW | MUST |
| SYS-FR-009 | The system shall provide an APB↔Wishbone B4 pipelined bridge for Caravel harness integration | Caravel management SoC must access Argus memory and peripherals; REQ-009 from MoSCoW | MUST |
| SYS-FR-010 | The system shall integrate into the Caravel harness wrapper meeting all precheck constraints | Required for sky130A MPW shuttle tapeout; REQ-010 from MoSCoW | MUST |
| SYS-FR-011 | The system shall aggregate all peripheral interrupt requests into a single CPU interrupt line with per-source enable/status registers | Enables efficient sensor polling without busy-wait; REQ-011 from MoSCoW (SHOULD) | SHOULD |
| SYS-FR-012 | The system shall support a watchdog timer that resets the processor on firmware hang | System reliability; REQ-014 from MoSCoW | SHOULD |
| SYS-FR-013 | The system shall support clock gating of idle peripherals and a sleep mode with SRAM retention | Low-power duty cycling for battery operation; domain requirement | SHOULD |
| SYS-FR-014 | The system shall provide a unique chip identification register (32-bit) readable via APB | Chip tracking and firmware identification | SHOULD |

---

## 4. Performance Requirements (SYS-PR-xxx)

| ID | Requirement | Metric | Value | Conditions | Priority |
|----|-------------|--------|-------|------------|----------|
| SYS-PR-001 | CPU clock frequency | f_cpu | 50 MHz (target), 25 MHz (fallback) | sky130A, ss/100C corner, Ibex "maxperf" | MUST |
| SYS-PR-002 | Active power | P_active | ≤ 10 mW (conservative), ≤ 5 mW (target) | 50 MHz, all peripherals clocked, 3.3V IO, 1.8V core | MUST |
| SYS-PR-003 | Sleep power | P_sleep | ≤ 50 µW (conservative), ≤ 10 µW (target) | CPU clock-gated, all peripherals clock-gated, SRAM retained | SHOULD |
| SYS-PR-004 | Wake-up latency | t_wake | ≤ 10 µs | From sleep (clock-gated) to first instruction fetch | SHOULD |
| SYS-PR-005 | UART throughput | R_UART | ≥ 115200 bps sustained full-duplex | 50 MHz sysclk, 8-byte FIFO, ≤ 1% error rate | MUST |
| SYS-PR-006 | SPI SCLK frequency | f_SCLK | Up to 12.5 MHz (f_sys/4 at 50 MHz) | Mode 0 and Mode 3 | MUST |
| SYS-PR-007 | I2C SCL frequency | f_SCL | 100 kHz ± 1% (std), 400 kHz ± 1% (fast) | Programmable divider from sysclk | MUST |
| SYS-PR-008 | PWM resolution | N_PWM | 10 bits (0–1023 duty steps) | Base frequency 1–25 kHz | MUST |
| SYS-PR-009 | PWM base frequency range | f_PWM_base | 1 kHz to 25 kHz | Derived from sysclk divider | MUST |
| SYS-PR-010 | Sensor polling throughput | R_poll | ≥ 200 sensor reads/second | I2C at 400 kHz, 2-byte register reads, assuming 7-byte transaction (addr+R+2data = ~175 µs each) | SHOULD |
| SYS-PR-011 | SRAM access latency | t_SRAM | 0 wait states (single-cycle read/write) | 50 MHz, 20 ns cycle time | MUST |
| SYS-PR-012 | GPIO interrupt latency | t_GPIO_IRQ | ≤ 5 CPU cycles from edge to IRQ assertion | 50 MHz, no higher-priority IRQ pending | SHOULD |
| SYS-PR-013 | Area | A_total | ≤ 2.0 mm² (conservative), ≤ 1.0 mm² (target) | sky130A, std cell density ~3.5 µm²/GE, 60% utilization | MUST |
| SYS-PR-014 | Caravel user area utilization | A_util | ≤ 41% of Caravel 4.928 mm² user area | 2,800×1,760 µm user area | MUST |

---

## 5. Interface Requirements (SYS-IR-xxx)

| ID | Interface | Protocol | Direction | Signals | Voltage | Timing | Priority |
|----|-----------|----------|-----------|---------|---------|--------|----------|
| SYS-IR-001 | UART Host | UART 8N1 | Bidir | tx, rx | 3.3V (sky130A IO) | 115200 bps, ±2% baud tolerance | MUST |
| SYS-IR-002 | SPI Master | SPI Mode 0/3 | Output | sck, mosi, miso, cs_n[0] | 3.3V (sky130A IO) | f_sys/4 max SCLK (12.5 MHz at 50 MHz) | MUST |
| SYS-IR-003 | I2C Master | I2C v3.0 | Bidir (open-drain) | scl, sda | 3.3V (sky130A IO), ext pull-up | 100/400 kHz, 7-bit addr | MUST |
| SYS-IR-004 | GPIO | Parallel digital | Bidir per-pin | gpio[7:0] | 3.3V (sky130A IO) | Synchronous to sysclk, ≤ 25 MHz toggle | MUST |
| SYS-IR-005 | PWM | Pulse-width modulated | Output | pwm[1:0] | 3.3V (sky130A IO) | 1–25 kHz base, 10-bit duty | MUST |
| SYS-IR-006 | Caravel Wishbone | Wishbone B4 pipelined | Slave | wb_clk, wb_rst, wb_adr[31:0], wb_dat_i[31:0], wb_dat_o[31:0], wb_sel[3:0], wb_we, wb_stb, wb_cyc, wb_ack, wb_err | Caravel VDDIO (3.3V) | Caravel mgmt SoC clk (typically 10–25 MHz) | MUST |
| SYS-IR-007 | Caravel Clock | Digital clock input | Input | user_clock2 (from Caravel PLL) | 3.3V | 50 MHz nominal, 25 MHz fallback | MUST |
| SYS-IR-008 | Caravel Reset | Active-low reset | Input | user_reset_n | 3.3V | Async assert, sync deassert, min 4 cycles | MUST |
| SYS-IR-009 | Caravel Power | VDDIO / VDD | Input | vddio (3.3V), vdd (1.8V) | — | Caravel power grid | MUST |
| SYS-IR-010 | Caravel GPIO | Caravel logic analyzer | Output | la_data[31:0], la_oen[31:0] | 3.3V | Caravel LA interface (debug only) | SHOULD |

---

## 6. Behavioral Requirements (SYS-AR-xxx)

| ID | Requirement | Trigger/Condition | System Response | Priority |
|----|-------------|-------------------|-----------------|----------|
| SYS-AR-001 | The system shall boot from SRAM after reset deassertion | External reset (Caravel user_reset_n) deasserted | Ibex fetches first instruction from SRAM base address (0x0000_0000). Firmware loaded by Caravel management SoC via Wishbone bridge before reset deassertion. | MUST |
| SYS-AR-002 | The system shall respond to APB read within 1 cycle (no wait states) | APB read transaction (PSEL && PENABLE && !PWRITE) to any valid peripheral address | PRDATA driven in same cycle as PREADY asserted. | MUST |
| SYS-AR-003 | The system shall respond to APB write within 1 cycle (no wait states) | APB write transaction (PSEL && PENABLE && PWRITE) to any valid peripheral address | PWDATA captured as PENABLE deasserts. PREADY asserted. | MUST |
| SYS-AR-004 | The system shall return APB error on access to unmapped address | APB transaction to address outside any mapped peripheral or SRAM region | PSLVERR asserted, PREADY asserted. No side effects. | MUST |
| SYS-AR-005 | The system shall assert CPU interrupt on any enabled peripheral IRQ | Any peripheral IRQ asserted AND corresponding interrupt enable bit set in interrupt controller | Single-bit CPU IRQ line asserted. CPU reads interrupt status register to identify source. IRQ remains asserted until status register read. | MUST |
| SYS-AR-006 | The system shall generate UART TX interrupt when transmit FIFO falls below programmable threshold | UART TX FIFO depth < threshold (default: half-empty, 4 bytes) | TX interrupt asserted. CPU writes additional data or disables TX interrupt. | SHOULD |
| SYS-AR-007 | The system shall generate UART RX interrupt when receive FIFO exceeds programmable threshold | UART RX FIFO depth > threshold (default: 1 byte) | RX interrupt asserted. CPU reads data from RX FIFO. | SHOULD |
| SYS-AR-008 | The system shall handle I2C NACK by aborting transaction and raising error flag | I2C slave returns NACK after address or data byte | I2C status register NACK bit set. Optional interrupt. Transaction terminated with STOP condition. | MUST |
| SYS-AR-009 | The system shall handle I2C bus arbitration loss by backing off | Another master drives SDA low while Argus is driving high (multi-master mode not implemented, but safe) | I2C status register ARBLOST bit set. SDA/SDL released. | SHOULD |
| SYS-AR-010 | The system shall enter sleep mode when firmware writes to sleep control register | Firmware writes 1 to SLEEP bit in sys_ctrl register | CPU clock gated. Peripherals clock-gated (unless wake-enabled: GPIO, PWM timer). SRAM retained. Wake on GPIO edge or timer expiry. | SHOULD |
| SYS-AR-011 | The system shall wake from sleep on GPIO edge or PWM timer match | GPIO edge (configurable rising/falling) detected OR PWM match event when wake-enabled | Restore clocks. CPU resumes from next instruction after sleep entry. Wake source readable in sys_ctrl register. | SHOULD |
| SYS-AR-012 | The system shall assert external reset on watchdog timeout | Watchdog counter reaches zero without firmware pet | System reset asserted for 16 cycles. All registers return to reset defaults. SRAM contents indeterminate after watchdog reset. | SHOULD |

---

## 7. Constraint Requirements (SYS-CR-xxx)

| ID | Constraint | Rationale | Priority |
|----|------------|-----------|----------|
| SYS-CR-001 | All RTL shall be written in synthesizable SystemVerilog (IEEE 1800-2017) compatible with Yosys/OpenLane flow | Open-source toolchain requirement; Yosys supports SV synthesis subset | MUST |
| SYS-CR-002 | The design shall target sky130A PDK (sky130_fd_sc_hd standard cells, sky130_fd_io IO pads) | Open-source silicon; Caravel MPW shuttle requirement | MUST |
| SYS-CR-003 | All REUSE IP shall be integrated without source modification except where documented in a REUSE* justification file | Preserve upstream IP integrity for community auditability | MUST |
| SYS-CR-004 | The APB bus shall follow ARM IHI0024C v2.0 protocol — no wait states, single-cycle read/write | Simplicity; all EF_ peripherals are APB-native | MUST |
| SYS-CR-005 | The Wishbone bridge shall implement B4 pipelined mode with CTI/BTE support for burst | Caravel harness expects B4 pipelined; management SoC uses burst transfers | MUST |
| SYS-CR-006 | CDC between Caravel Wishbone clock domain and internal APB clock domain shall use standard 2-FF synchronizer for single-bit and async FIFO for multi-bit | Robustness; standard practice for single-clock-domain peripheral bus | MUST |
| SYS-CR-007 | Reset shall be asynchronous assert (active low), synchronous deassert to APB clock | Standard practice; avoids metastability on deassert | MUST |
| SYS-CR-008 | Maximum SRAM macro aspect ratio shall be ≤ 4:1 for routability within Caravel user area | Floorplanning constraint; tall macros complicate routing | SHOULD |
| SYS-CR-009 | All external-facing I/O pads shall include ESD protection (sky130_fd_io) | Reliability; ESD diodes are part of sky130A IO pad cells | MUST |
| SYS-CR-010 | The design shall meet Caravel precheck constraints: no combinational loops, no unmapped I/O, no floating nets | Gate for tapeout acceptance | MUST |
| SYS-CR-011 | Clock tree shall be single-domain from Caravel user_clock2 with local gating for power management | Single clock domain eliminates CDC complexity for peripheral bus | MUST |

---

## 8. Memory Map

| Region | Base Address | Size | Access | Owner Block | Description |
|--------|-------------|------|--------|-------------|-------------|
| SRAM | 0x0000_0000 | 4 KB (0x1000) | R/W/X | sram | Firmware code, stack, heap, sensor data buffer |
| Reserved | 0x0000_1000 | 60 KB (0xF000) | — | — | Reserved for SRAM expansion (up to 64 KB total) |
| UART | 0x0001_0000 | 256 B (0x100) | R/W | uart | UART TX/RX data, status, control, baud config |
| SPI | 0x0001_0100 | 256 B (0x100) | R/W | spi_master | SPI data, status, control, clock config |
| I2C | 0x0001_0200 | 256 B (0x100) | R/W | i2c_master | I2C data, status, control, clock config |
| GPIO | 0x0001_0300 | 256 B (0x100) | R/W | gpio | GPIO data, direction, interrupt enable/status/edge |
| PWM | 0x0001_0400 | 256 B (0x100) | R/W | pwm | PWM period, duty cycle (ch0/ch1), control, status |
| Interrupt Controller | 0x0001_0500 | 256 B (0x100) | R/W | interrupt_ctrl | IRQ enable, pending, mask per source |
| Watchdog Timer | 0x0001_0600 | 256 B (0x100) | R/W | pwm (timer repurpose) | Watchdog reload, control, status |
| System Control | 0x0001_0700 | 256 B (0x100) | R/W | sys_ctrl | Chip ID, clock divider, reset cause, sleep control |
| Reserved (periph) | 0x0001_0800 | 62 KB (0xF800) | — | — | Reserved for future peripherals (DMA, CRC, I2C slave, etc.) |
| Wishbone Window | 0x8000_0000 | 2 GB (0x8000_0000) | R/W (from Caravel mgmt SoC) | wb_bridge | Caravel Wishbone → APB bridge address window |

### Register Map Details

**UART (0x0001_0000):**
| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | TXDATA | 8 | W | Transmit data (write pushes to TX FIFO) |
| 0x04 | RXDATA | 8 | R | Receive data (read pops from RX FIFO) |
| 0x08 | STATUS | 8 | R | TX full, TX empty, RX full, RX empty, TX busy, RX error |
| 0x0C | CONTROL | 8 | R/W | TX enable, RX enable, parity enable, stop bits |
| 0x10 | BAUD_DIV | 16 | R/W | Baud rate divisor = f_sys / baud_rate (e.g., 434 for 115200 at 50 MHz) |
| 0x14 | FIFO_THRESH | 8 | R/W | TX/RX FIFO interrupt threshold |

**SPI (0x0001_0100):**
| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | TXDATA | 8 | W | Transmit data (write starts SPI transfer) |
| 0x04 | RXDATA | 8 | R | Receive data (from shift register) |
| 0x08 | STATUS | 8 | R | TX empty, RX full, busy, mode |
| 0x0C | CONTROL | 8 | R/W | CPOL, CPHA, prescaler, CS enable |
| 0x10 | CLK_DIV | 8 | R/W | Clock divider = f_sys / (2 × f_SCLK) |

**I2C (0x0001_0200):**
| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | DATA | 8 | R/W | Transmit/receive data byte |
| 0x04 | ADDR | 8 | R/W | Slave address (7-bit in [7:1], R/W in [0]) |
| 0x08 | STATUS | 8 | R | Busy, ACK, NACK, arbitration lost, transfer done |
| 0x0C | CONTROL | 8 | R/W | START, STOP, read, write, repeated start, enable, IRQ enable |
| 0x10 | CLK_DIV_LO | 8 | R/W | SCL low period divider |
| 0x14 | CLK_DIV_HI | 8 | R/W | SCL high period divider |

**GPIO (0x0001_0300):**
| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | DATA_OUT | 8 | R/W | Output data for pins [7:0] |
| 0x04 | DATA_IN | 8 | R | Input data from pins [7:0] |
| 0x08 | DIR | 8 | R/W | Direction: 1=output, 0=input per pin |
| 0x0C | IRQ_EN | 8 | R/W | Interrupt enable per pin |
| 0x10 | IRQ_EDGE | 16 | R/W | Edge config: [15:8] = falling enable, [7:0] = rising enable |
| 0x14 | IRQ_STATUS | 8 | R/W1C | Interrupt pending per pin (write 1 to clear) |

**PWM (0x0001_0400):**
| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | PERIOD | 16 | R/W | PWM period in clock cycles |
| 0x04 | DUTY_CH0 | 16 | R/W | Channel 0 duty cycle (0 = always low, PERIOD = always high) |
| 0x08 | DUTY_CH1 | 16 | R/W | Channel 1 duty cycle |
| 0x0C | CONTROL | 8 | R/W | Channel 0/1 enable, prescaler, one-shot mode |

**Interrupt Controller (0x0001_0500):**
| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | IRQ_EN | 16 | R/W | Per-source enable: [0]=UART, [1]=SPI, [2]=I2C, [3:10]=GPIO[7:0], [11]=PWM, [12]=Watchdog |
| 0x04 | IRQ_PENDING | 16 | R | Per-source pending status (read-only copy of peripheral IRQ outputs ANDed with IRQ_EN) |
| 0x08 | CPU_IRQ | 1 | R | Global CPU IRQ: logical OR of all (IRQ_EN & peripheral_irq) |

**Watchdog (0x0001_0600):**
| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | RELOAD | 24 | R/W | Watchdog reload value (in clock cycles) |
| 0x04 | COUNTER | 24 | R | Current counter value |
| 0x08 | CONTROL | 8 | R/W | Enable, reset-on-pet (write 1 to bit 0 to pet) |

**System Control (0x0001_0700):**
| Offset | Register | Width | Access | Description |
|--------|----------|-------|--------|-------------|
| 0x00 | CHIP_ID | 32 | R | Unique chip identifier |
| 0x04 | CLK_DIV | 8 | R/W | System clock divider (UART/SPI/I2C peripheral clocks) |
| 0x08 | RESET_CAUSE | 8 | R | Reset cause: 0=POR, 1=external, 2=watchdog, 3=software |
| 0x0C | SLEEP_CTRL | 8 | R/W | Sleep enable, wake source select, sleep status |

---

## 9. Clock & Reset Architecture

### 9.1 Clock Domains

| Domain | Source | Frequency | PLL/Divider | Consumers | Notes |
|--------|--------|-----------|-------------|-----------|-------|
| clk_sys | Caravel user_clock2 | 50 MHz (target), 25 MHz (fallback) | Caravel PLL → user_clock2 pad | All internal logic: Ibex, APB, peripherals, SRAM | Single clock domain. Single-cycle APB possible. |
| clk_wb | Caravel wb_clk | 10–25 MHz | Caravel management SoC clock | Wishbone bridge (WB side) | Async to clk_sys. CDC at bridge boundary. |

### 9.2 Reset Architecture

| Signal | Type | Assert | Deassert | Min Width | Source |
|--------|------|--------|----------|-----------|--------|
| rst_n (sys) | Async assert, sync deassert | user_reset_n from Caravel (active low) | Synchronized to clk_sys posedge | 4 clk_sys cycles | Caravel harness |
| rst_n (wb) | Async assert, sync deassert | wb_rst from Caravel | Synchronized to clk_wb posedge | 4 clk_wb cycles | Caravel harness |
| wdt_rst_n | Internal, sync | Watchdog timeout | Extended 16 clk_sys cycles | 16 clk_sys cycles | Watchdog timer |

### 9.3 CDC Strategy

| From Domain | To Domain | Method | Verification |
|-------------|-----------|--------|-------------|
| clk_wb → clk_sys | Wishbone → APB bridge | Async FIFO for data (32-bit × 8 deep), 2-FF sync for control signals | Formal CDC check (Yosys-SMTBMC), GLS |
| clk_sys → clk_wb | APB → Wishbone bridge | Async FIFO for read-response data (32-bit × 4 deep), 2-FF sync for ack/err | Formal CDC check, GLS |
| Peripheral IRQ → CPU | Multiple async sources → clk_sys | IRQs are synchronous to clk_sys (peripherals clocked by clk_sys). No CDC needed. | Not applicable — single clock domain |

---

## 10. Budgets

### 10.1 Timing Budget

| Block | Target Freq | Critical Path Budget (ns) | Setup Margin (ns) |
|-------|-------------|--------------------------|-------------------|
| Ibex (maxperf) | 50 MHz | 20.0 | 2.0 |
| APB interconnect | 50 MHz | 20.0 | 3.0 |
| UART | 50 MHz | 20.0 | 5.0 (low-speed peripheral, generous margin) |
| SPI master | 50 MHz | 20.0 | 4.0 |
| I2C master | 50 MHz | 20.0 | 5.0 (400 kHz SCL = 2500 ns period, internal logic fast) |
| GPIO | 50 MHz | 20.0 | 5.0 |
| PWM | 50 MHz | 20.0 | 3.0 |
| SRAM macro | 50 MHz | 20.0 | 2.0 (OpenRAM macro characterized at 50 MHz) |
| Wishbone bridge | 25 MHz (wb_clk) | 40.0 | 5.0 (slower WB domain, relaxed) |
| **TOP (clk_sys)** | **50 MHz** | **20.0** | **≥ 2.0 (10% margin)** |

### 10.2 Area Budget

| Block | Gate Equiv. (kGE) | Area (µm²) | % of Total (2.0 mm² target) |
|-------|-------------------|-----------|------------------------------|
| Ibex (maxperf, RV32I) | ~15 | ~87,500 | 4.4% |
| APB interconnect | ~3 | ~17,500 | 0.9% |
| UART | ~2 | ~11,700 | 0.6% |
| SPI master | ~2 | ~11,700 | 0.6% |
| I2C master | ~2 | ~11,700 | 0.6% |
| GPIO | ~1 | ~5,800 | 0.3% |
| PWM (2 ch + timer) | ~4 | ~23,400 | 1.2% |
| Interrupt controller | ~1 | ~5,800 | 0.3% |
| Watchdog | ~1 | ~5,800 | 0.3% |
| APB↔Wishbone bridge + CDC FIFOs | ~5 | ~29,200 | 1.5% |
| Caravel wrapper + padframe routing | ~5 | ~29,200 | 1.5% |
| Sys ctrl + clock gating | ~2 | ~11,700 | 0.6% |
| SRAM (4 KB OpenRAM) | ~40 | ~250,000 | 12.5% |
| **Subtotal (logic)** | **~83 kGE** | **~490,600** | **24.5%** |
| Routing, filler, decap, padding | — | ~1,509,400 | 75.5% |
| **Total** | **~83 kGE** | **~2,000,000** | **100%** |

*Note: At sky130A std cell density ~3.5 µm²/GE with ~60% utilization and 4 KB SRAM at ~250K µm², total physical area ≈ 0.7–2.0 mm². The conservative 2.0 mm² allocation includes substantial routing/padding headroom. The target 1.0 mm² assumes 70% utilization and compact floorplanning.*

### 10.3 Power Budget

| Block | Dynamic (mW) | Leakage (µW) | % of Total (5 mW target) |
|-------|-------------|--------------|---------------------------|
| Ibex (maxperf, 50 MHz) | 1.5–3.0 | 5 | 40% |
| SRAM (4 KB, 50 MHz) | 0.5–1.0 | 10 | 15% |
| UART (active, 115200 bps) | 0.1 | 1 | 3% |
| SPI master (12.5 MHz SCLK) | 0.2 | 1 | 5% |
| I2C master (400 kHz SCL) | 0.1 | 1 | 3% |
| GPIO (8 pins toggling) | 0.1 | 1 | 3% |
| PWM (2 channels, 25 kHz) | 0.1 | 1 | 3% |
| APB interconnect | 0.2 | 2 | 5% |
| Wishbone bridge + CDC FIFOs | 0.2 | 2 | 5% |
| Other (clock tree, I/O pads) | 0.5–1.0 | 5 | 18% |
| **Total (50 MHz, all active)** | **3.5–5.8 mW** | **~29 µW** | **≈ 100%** |
| **Total (sleep, SRAM retained)** | **—** | **10–50 µW** | **≤ 50 µW** |

*Note: Baselines derived from OpenTitan EarlGrey measurements (Ibex at 100 MHz sky130A ~6-10 mW core-only), scaled to 50 MHz and adjusted for fewer peripherals. Conservative 10 mW assumes no clock gating; target 5 mW assumes per-peripheral clock gating. Leakage baseline from sky130A published data (~2-5 nA/µm gate leakage at nominal VDD).*

---

## 11. Traceability Matrix

| Req ID | Block | Verification Method | Priority |
|--------|-------|-------------------|----------|
| SYS-FR-001 | ibex_core | riscv-compliance suite (rv32i), random instruction testbench, GLS | MUST |
| SYS-FR-002 | uart | Loopback test at 115200 bps, 10K frames, ≤1% error. Formal BMC depth 20. | MUST |
| SYS-FR-003 | spi_master | Loopback (MOSI↔MISO), Mode 0 + Mode 3, 12.5 MHz SCLK. Formal BMC depth 20. | MUST |
| SYS-FR-004 | i2c_master | I2C slave model testbench. 100/400 kHz. Multi-byte read/write + repeated start. ACK/NACK coverage. | MUST |
| SYS-FR-005 | gpio | Per-pin output→input loopback. Edge interrupt verification. 8-pin parallel toggle test. | MUST |
| SYS-FR-006 | pwm | Duty cycle measurement (oscilloscope in sim). Jitter ≤ 1 sysclk. 10-bit resolution verified. | MUST |
| SYS-FR-007 | sram | Memory BIST (March C-). Zero-wait-state read/write at 50 MHz with back-annotated SDF. | MUST |
| SYS-FR-008 | apb_interconnect | APB protocol checker (formal). All peripheral base addresses tested for correct decode. | MUST |
| SYS-FR-009 | wb_bridge | Wishbone B4 checker. APB-side read/write from WB side. CDC formal (async FIFO). Caravel precheck. | MUST |
| SYS-FR-010 | caravel_wrapper | Caravel precheck tool. Pin constraint check. GDS area check (≤ 2,800×1,760 µm). | MUST |
| SYS-FR-011 | interrupt_ctrl | Directed test: each peripheral IRQ asserted, CPU receives IRQ, reads status, clears. All 13 sources. | SHOULD |
| SYS-FR-012 | pwm (watchdog) | Watchdog timeout simulation. Verify system reset assertion. Pet-before-timeout test. | SHOULD |
| SYS-FR-013 | sys_ctrl | Clock-gating simulation. Power estimation with/without gating. Sleep/wake sequence test. | SHOULD |
| SYS-FR-014 | sys_ctrl | Read CHIP_ID at 0x0001_0700. Verify non-zero, consistent across resets. | SHOULD |
| SYS-PR-001 | ibex_core | Static timing analysis (OpenSTA) at ss/100C corner. 50 MHz ≥ 0 slack, 25 MHz ≥ 0 slack. | MUST |
| SYS-PR-002 | TOP | Power analysis (OpenLane, SPEF-annotated). Active power measurement in GLS. | MUST |
| SYS-PR-003 | TOP | Sleep power measurement in GLS with clock gating enabled. | SHOULD |
| SYS-PR-004 | sys_ctrl | Simulate sleep-to-wake transition. Measure clk_sys cycles from wake event to first instruction fetch. | SHOULD |
| SYS-PR-005 | uart | 1M-byte loopback test at 115200 bps. BER < 10^-5. | MUST |
| SYS-PR-006 | spi_master | SCLK frequency measurement in sim. 12.5 MHz at 50 MHz sysclk. | MUST |
| SYS-PR-007 | i2c_master | SCL period measurement at 100 kHz and 400 kHz settings. ±1% tolerance. | MUST |
| SYS-PR-008 | pwm | Sweep duty 0–1023. Measure output pulse width at 25 kHz base. 10-bit monotonic. | MUST |
| SYS-PR-009 | pwm | Sweep period divider. Measure 1 kHz, 10 kHz, 25 kHz base frequencies. | MUST |
| SYS-PR-010 | i2c_master + ibex_core | Firmware polling loop: 200 I2C reads in 1 second. Average ≥ 200 reads/s. | SHOULD |
| SYS-PR-011 | sram | SDF-annotated timing. Read data valid at capture edge. Setup/hold met. | MUST |
| SYS-PR-012 | gpio + interrupt_ctrl | GPIO edge to CPU IRQ assertion latency ≤ 5 cycles. | SHOULD |
| SYS-PR-013 | TOP | Post-synthesis area report (Yosys/OpenLane). ≤ 2.0 mm². | MUST |
| SYS-PR-014 | caravel_wrapper | Caravel precheck area check. User area ≤ 4.928 mm². | MUST |
| SYS-CR-001 | ALL | Yosys synthesis without SV feature errors. OpenLane flow completes. | MUST |
| SYS-CR-002 | ALL | sky130_fd_sc_hd cells in netlist. sky130_fd_io pads at top level. GDS passes DRC. | MUST |
| SYS-CR-003 | ALL | REUSE IP hash matches upstream commit. Diff shows only documented REUSE* changes. | MUST |
| SYS-CR-004 | apb_interconnect | APB protocol checker (formal) — all transactions complete in ≤ 2 cycles (setup + access). | MUST |
| SYS-CR-005 | wb_bridge | Wishbone B4 checker (formal) — pipelined mode, CTI/BTE support. | MUST |
| SYS-CR-006 | wb_bridge | CDC formal check. No metastability paths. Async FIFO full/empty flags correct. | MUST |
| SYS-CR-007 | TOP | Reset deassert synchronized to clk_sys posedge. Recovery time met. | MUST |
| SYS-CR-008 | sram | Floorplan in OpenLane. SRAM macro aspect ratio ≤ 4:1. | SHOULD |
| SYS-CR-009 | caravel_wrapper | IO pad instantiation uses sky130_fd_io cells with ESD. DRC check on pad ring. | MUST |
| SYS-CR-010 | caravel_wrapper | Caravel precheck passes. No combinational loops in LEC. No floating nets. | MUST |
| SYS-CR-011 | TOP | Clock tree report: single source (user_clock2), max skew, max latency within budget. | MUST |
| SYS-IR-001 | uart + caravel_wrapper | UART loopback through IO pads (GLS). Signal integrity at 115200 bps. | MUST |
| SYS-IR-002 | spi_master + caravel_wrapper | SPI loopback through IO pads. MISO sampled correctly at all SCLK frequencies. | MUST |
| SYS-IR-003 | i2c_master + caravel_wrapper | I2C pull-up model. SCL/SDA timing (t_HD_STA, t_SU_STO, t_LOW, t_HIGH). | MUST |
| SYS-IR-004 | gpio + caravel_wrapper | Per-pin direction test through pads. Output drive strength (4/8/12 mA). | MUST |
| SYS-IR-005 | pwm + caravel_wrapper | PWM output to pad. Duty cycle measured at pad. | MUST |
| SYS-IR-006 | wb_bridge + caravel_wrapper | Wishbone read/write from Caravel management SoC via precheck testbench. | MUST |
| SYS-IR-007 | caravel_wrapper | user_clock2 input buffered. Internal clk_sys derived correctly. | MUST |
| SYS-IR-008 | caravel_wrapper | user_reset_n async assert, sync deassert verified. Glitch filter on reset input. | MUST |
| SYS-IR-009 | caravel_wrapper | Power grid connection. IR drop analysis within 5% of nominal. | MUST |
| SYS-IR-010 | caravel_wrapper | LA probes connected to internal debug signals. LA readback test. | SHOULD |
| SYS-AR-001 | ibex_core + sram | Reset vector 0x0000_0000. Firmware loaded via Wishbone. First instruction fetch verified. | MUST |
| SYS-AR-002 | apb_interconnect | All APB reads complete in 1 cycle. PREADY timing verified. | MUST |
| SYS-AR-003 | apb_interconnect | All APB writes complete in 1 cycle. PWDATA captured correctly. | MUST |
| SYS-AR-004 | apb_interconnect | APB access to unmapped address produces PSLVERR. Address 0x0002_0000 tested. | MUST |
| SYS-AR-005 | interrupt_ctrl | Each peripheral IRQ → CPU IRQ verified. CPU IRQ clears on status read. | MUST |
| SYS-AR-006 | uart + interrupt_ctrl | TX FIFO threshold interrupt verified. Empty→full→threshold sequence. | SHOULD |
| SYS-AR-007 | uart + interrupt_ctrl | RX FIFO threshold interrupt verified. Full→empty→threshold sequence. | SHOULD |
| SYS-AR-008 | i2c_master | NACK from slave model → transaction aborted → NACK status bit set. | MUST |
| SYS-AR-009 | i2c_master | Arbitration loss injection → ARBLOST status. | SHOULD |
| SYS-AR-010 | sys_ctrl | Firmware writes SLEEP=1 → clocks stop → SRAM retained. Verified in GLS. | SHOULD |
| SYS-AR-011 | sys_ctrl + gpio + pwm | GPIO edge wakes system. PWM match wakes system. Wake source readable. | SHOULD |
| SYS-AR-012 | pwm (watchdog) | Counter reaches 0 → system reset for 16 cycles → CPU restarts. | SHOULD |

---

## 12. Open Issues & Ambiguities

| ID | Issue | Status | Resolution |
|----|-------|--------|------------|
| AMB-001 | SRAM size — market_requirements.md says "2-4 KB" | RESOLVED | 4 KB selected. Sufficient for 50-frame buffer (1.6 KB) + stack/heap (1 KB) + 1.4 KB headroom. OpenRAM can generate 4 KB macro. |
| AMB-002 | GPIO pin count — market_requirements.md says "8-12 pins" | RESOLVED | 8 pins selected. EF_GPIO8 provides exactly 8. Expandable to 12 in future iteration if needed. |
| AMB-003 | PWM resolution — market_requirements.md says "8-10 bit" | RESOLVED | 10-bit selected. EF_TMR32 32-bit timer easily supports 10-bit PWM. Better actuator control than 8-bit. |
| AMB-004 | Interrupt controller — REQ-011 is SHOULD priority | RESOLVED | Included as SHOULD. Base design includes simple 13-source aggregator. Maskable per source. |
| AMB-005 | Watchdog timer — REQ-014 is SHOULD priority | RESOLVED | Included as SHOULD. Repurposes PWM timer channel. Independent from PWM function. |
| AMB-006 | Clock source — Crystal optional per market_requirements.md | RESOLVED | Caravel user_clock2 is primary source. No external crystal needed for MVP. |
| AMB-007 | I2C multi-master support | RESOLVED | Not supported in Iteration 1. Single-master (Argus) on I2C bus. Arbitration loss detection included for safety but not actively used. |
| AMB-008 | Firmware loading mechanism | RESOLVED | Caravel management SoC loads firmware into SRAM via Wishbone bridge. No boot ROM. Initial firmware provided as hex image. |
