# Traceability Matrix — Requirement-to-Config-Key Bindings
## PRJ-001 (Argus) Environmental Sensor-Hub SoC — Iteration 1

**Purpose:** Every SYS-xx-NNN requirement with a tunable value or register-level implementation path is bound to the config key that implements it. No orphan config keys; no unbound MUST requirements. This matrix satisfies CLAUDE.md Stage 1 check 1.8a.

---

## Config Key Inventory

| Config Key | Register Offset | Block | Width | Description |
|------------|----------------|-------|-------|-------------|
| UART.BAUD_DIV | 0x0001_0010 | uart | 16 | Baud rate divisor = f_sys / baud_rate |
| UART.FIFO_THRESH | 0x0001_0014 | uart | 8 | TX/RX FIFO interrupt threshold |
| UART.CONTROL | 0x0001_000C | uart | 8 | TX enable, RX enable, parity, stop bits |
| SPI.CLK_DIV | 0x0001_0110 | spi_master | 8 | Clock divider = f_sys / (2 × f_SCLK) |
| SPI.CONTROL | 0x0001_010C | spi_master | 8 | CPOL, CPHA, prescaler, CS enable |
| I2C.CLK_DIV_LO | 0x0001_0210 | i2c_master | 8 | SCL low period divider |
| I2C.CLK_DIV_HI | 0x0001_0214 | i2c_master | 8 | SCL high period divider |
| I2C.CONTROL | 0x0001_020C | i2c_master | 8 | START, STOP, read, write, repeated start, enable, IRQ enable |
| GPIO.DIR | 0x0001_0308 | gpio | 8 | Direction: 1=output, 0=input per pin |
| GPIO.IRQ_EN | 0x0001_030C | gpio | 8 | Interrupt enable per pin |
| GPIO.IRQ_EDGE | 0x0001_0310 | gpio | 16 | Edge config: [15:8]=falling, [7:0]=rising |
| GPIO.IRQ_STATUS | 0x0001_0314 | gpio | 8 | Interrupt pending per pin (W1C) |
| PWM.PERIOD | 0x0001_0400 | pwm | 16 | PWM period in clock cycles |
| PWM.DUTY_CH0 | 0x0001_0404 | pwm | 16 | Channel 0 duty cycle |
| PWM.DUTY_CH1 | 0x0001_0408 | pwm | 16 | Channel 1 duty cycle |
| PWM.CONTROL | 0x0001_040C | pwm | 8 | Channel enable, prescaler, one-shot |
| IRQ.IRQ_EN | 0x0001_0500 | interrupt_ctrl | 16 | Per-source IRQ enable mask |
| IRQ.IRQ_PENDING | 0x0001_0504 | interrupt_ctrl | 16 | Per-source pending status |
| WDT.RELOAD | 0x0001_0600 | pwm (wdt) | 24 | Watchdog reload value |
| WDT.CONTROL | 0x0001_0608 | pwm (wdt) | 8 | Enable, pet bit |
| SYSCTRL.CHIP_ID | 0x0001_0700 | sys_ctrl | 32 | Unique chip identifier |
| SYSCTRL.CLK_DIV | 0x0001_0704 | sys_ctrl | 8 | System clock divider |
| SYSCTRL.RESET_CAUSE | 0x0001_0708 | sys_ctrl | 8 | Reset cause register |
| SYSCTRL.SLEEP_CTRL | 0x0001_070C | sys_ctrl | 8 | Sleep enable, wake source, status |
| CLOCK_PERIOD | — (PDK-level) | TOP | — | 20 ns (50 MHz) / 40 ns (25 MHz fallback) |
| SRAM_SIZE | — (macro gen) | sram | — | 4 KB OpenRAM macro |
| SRAM_BASE | — (addr decode) | apb_interconnect | — | 0x0000_0000 |
| APB_SLAVE_COUNT | — (interconnect) | apb_interconnect | — | 12 slave ports |
| WB_WINDOW_BASE | — (addr decode) | wb_bridge | — | 0x8000_0000 |

---

## Requirement → Config Key Bindings

### SYS-FR (Functional Requirements)

| Req ID | Config Key(s) | Implementing Block | Value / Constraint |
|--------|--------------|-------------------|-------------------|
| SYS-FR-001 | (none — ISA compliance is structural) | ibex_core | RV32I ISA v2.1 selected via Ibex config `RV32E=0, RV32M=0` |
| SYS-FR-002 | UART.BAUD_DIV, UART.CONTROL, UART.FIFO_THRESH | uart | BAUD_DIV=434 @50MHz→115200 bps; CONTROL: TX_EN=1, RX_EN=1, 8N1 |
| SYS-FR-003 | SPI.CLK_DIV, SPI.CONTROL | spi_master | CLK_DIV=2 @50MHz→12.5 MHz; CONTROL: CPOL/CPHA configurable |
| SYS-FR-004 | I2C.CLK_DIV_LO, I2C.CLK_DIV_HI, I2C.CONTROL | i2c_master | CLK_DIV_LO/HI=250/250→100 kHz; 62/62→400 kHz |
| SYS-FR-005 | GPIO.DIR, GPIO.IRQ_EN, GPIO.IRQ_EDGE, GPIO.IRQ_STATUS | gpio | DIR: per-pin; IRQ_EDGE: rising[7:0]+falling[15:8] |
| SYS-FR-006 | PWM.PERIOD, PWM.DUTY_CH0, PWM.DUTY_CH1, PWM.CONTROL | pwm | PERIOD=2000 @50MHz→25 kHz base; DUTY 0–1023 steps |
| SYS-FR-007 | SRAM_SIZE, SRAM_BASE | sram | 4 KB (0x1000) at 0x0000_0000; zero-wait-state by OpenRAM timing |
| SYS-FR-008 | APB_SLAVE_COUNT | apb_interconnect | 12 slave ports, address decode table |
| SYS-FR-009 | WB_WINDOW_BASE | wb_bridge | 0x8000_0000 window; B4 pipelined mode |
| SYS-FR-010 | (none — structural integration) | caravel_wrapper | Caravel precheck constraints: no comb loops, no unmapped I/O, no floating nets |
| SYS-FR-011 | IRQ.IRQ_EN | interrupt_ctrl | 13-bit enable mask: [0]=UART, [1]=SPI, [2]=I2C, [3:10]=GPIO, [11]=PWM, [12]=WDT |
| SYS-FR-012 | WDT.RELOAD, WDT.CONTROL | pwm (wdt) | RELOAD=timeout_cycles; CONTROL: enable=1, pet=bit0 |
| SYS-FR-013 | SYSCTRL.SLEEP_CTRL, SYSCTRL.CLK_DIV | sys_ctrl | SLEEP_CTRL: sleep_en=1; CLK_DIV: per-periph gating |
| SYS-FR-014 | SYSCTRL.CHIP_ID | sys_ctrl | 32-bit unique value at 0x0001_0700 |

### SYS-PR (Performance Requirements)

| Req ID | Config Key(s) | Implementing Block | Value / Constraint |
|--------|--------------|-------------------|-------------------|
| SYS-PR-001 | CLOCK_PERIOD | TOP (caravel_wrapper) | 20 ns (50 MHz) target; 40 ns (25 MHz) fallback |
| SYS-PR-002 | (none — measured, not configured) | TOP | ≤ 10 mW active target; validated via power analysis (OpenLane SPEF) |
| SYS-PR-003 | SYSCTRL.SLEEP_CTRL | sys_ctrl | ≤ 50 µW sleep; validated via GLS power measurement |
| SYS-PR-004 | CLOCK_PERIOD | sys_ctrl | ≤ 10 µs wake latency = ≤ 500 cycles @50 MHz |
| SYS-PR-005 | UART.BAUD_DIV | uart | BAUD_DIV=434; 1M-byte loopback BER < 10^-5 |
| SYS-PR-006 | SPI.CLK_DIV | spi_master | CLK_DIV=2 → 12.5 MHz at 50 MHz sysclk |
| SYS-PR-007 | I2C.CLK_DIV_LO, I2C.CLK_DIV_HI | i2c_master | 250/250 → 100 kHz ±1%; 62/62 → 400 kHz ±1% |
| SYS-PR-008 | PWM.DUTY_CH0, PWM.DUTY_CH1 | pwm | 10-bit = 0–1023 duty steps; monotonic |
| SYS-PR-009 | PWM.PERIOD, PWM.CONTROL (prescaler) | pwm | PERIOD range 2000–50000 → 1 kHz–25 kHz at 50 MHz |
| SYS-PR-010 | I2C.CLK_DIV_LO, I2C.CLK_DIV_HI | i2c_master | 400 kHz mode → ~175 µs/read → ≥ 200 reads/s |
| SYS-PR-011 | SRAM_SIZE | sram | OpenRAM macro at 50 MHz; 0-wait-state timing |
| SYS-PR-012 | GPIO.IRQ_EN, IRQ.IRQ_EN | gpio + interrupt_ctrl | ≤ 5 cycles from GPIO edge to CPU IRQ |
| SYS-PR-013 | (none — synthesis constraint) | TOP | ≤ 2.0 mm²; measured via Yosys/OpenLane area report |
| SYS-PR-014 | (none — Caravel precheck) | caravel_wrapper | ≤ 4.928 mm² user area (2,800×1,760 µm) |

### SYS-IR (Interface Requirements)

| Req ID | Config Key(s) | Implementing Block | Value / Constraint |
|--------|--------------|-------------------|-------------------|
| SYS-IR-001 | UART.BAUD_DIV | uart + caravel_wrapper | 115200 bps, 3.3V IO pads |
| SYS-IR-002 | SPI.CLK_DIV, SPI.CONTROL (CPOL/CPHA) | spi_master + caravel_wrapper | f_sys/4 max SCLK, 3.3V IO pads |
| SYS-IR-003 | I2C.CLK_DIV_LO, I2C.CLK_DIV_HI | i2c_master + caravel_wrapper | 100/400 kHz, open-drain 3.3V IO |
| SYS-IR-004 | GPIO.DIR | gpio + caravel_wrapper | 8 pins, per-pin direction, 3.3V IO |
| SYS-IR-005 | PWM.PERIOD, PWM.DUTY_CH0, PWM.DUTY_CH1, PWM.CONTROL | pwm + caravel_wrapper | 1–25 kHz, 10-bit, 3.3V IO |
| SYS-IR-006 | WB_WINDOW_BASE | wb_bridge + caravel_wrapper | Wishbone B4 pipelined, Caravel VDDIO |
| SYS-IR-007 | CLOCK_PERIOD | caravel_wrapper | user_clock2 from Caravel PLL → clk_sys |
| SYS-IR-008 | (none — structural reset) | caravel_wrapper | Async assert, sync deassert to clk_sys |
| SYS-IR-009 | (none — PDK-level power grid) | caravel_wrapper | VDDIO 3.3V, VDD 1.8V |
| SYS-IR-010 | (none — debug probe passthrough) | caravel_wrapper | LA probes la_data[31:0], la_oen[31:0] |

### SYS-AR (Behavioral Requirements)

| Req ID | Config Key(s) | Implementing Block | Value / Constraint |
|--------|--------------|-------------------|-------------------|
| SYS-AR-001 | SRAM_BASE | ibex_core + sram | Boot from 0x0000_0000; FW loaded via Wishbone before reset deassert |
| SYS-AR-002 | (none — APB protocol timing) | apb_interconnect | 1-cycle read; PREADY assertion in access phase |
| SYS-AR-003 | (none — APB protocol timing) | apb_interconnect | 1-cycle write; PWDATA captured on PENABLE deassert |
| SYS-AR-004 | APB_SLAVE_COUNT (decode table) | apb_interconnect | PSLVERR on unmapped; address 0x0002_0000 is unmapped |
| SYS-AR-005 | IRQ.IRQ_EN | interrupt_ctrl | OR of (IRQ_EN[i] & peripheral_irq[i]) → cpu_irq |
| SYS-AR-006 | UART.FIFO_THRESH, IRQ.IRQ_EN (bit 0) | uart + interrupt_ctrl | TX FIFO < threshold → TX IRQ |
| SYS-AR-007 | UART.FIFO_THRESH, IRQ.IRQ_EN (bit 0) | uart + interrupt_ctrl | RX FIFO > threshold → RX IRQ |
| SYS-AR-008 | I2C.CONTROL (STOP) | i2c_master | On NACK: set NACK status bit, generate STOP |
| SYS-AR-009 | (none — I2C hardware detect) | i2c_master | ARBLOST status bit on arbitration loss |
| SYS-AR-010 | SYSCTRL.SLEEP_CTRL | sys_ctrl | SLEEP=1 → clock gates enable; SRAM retained |
| SYS-AR-011 | SYSCTRL.SLEEP_CTRL, GPIO.IRQ_EN | sys_ctrl + gpio + pwm | Wake source readable; GPIO edge or PWM match |
| SYS-AR-012 | WDT.RELOAD, WDT.CONTROL | pwm (wdt) | Counter→0 → system reset for 16 cycles |

### SYS-CR (Constraint Requirements)

| Req ID | Config Key(s) | Implementing Block | Value / Constraint |
|--------|--------------|-------------------|-------------------|
| SYS-CR-001 | (none — toolchain constraint) | ALL | SystemVerilog IEEE 1800-2017, Yosys/OpenLane compatible |
| SYS-CR-002 | (none — PDK selection) | ALL | sky130_fd_sc_hd std cells, sky130_fd_io pads |
| SYS-CR-003 | (none — process constraint) | ALL REUSE blocks | Upstream hash pinned; REUSE* justification in module_list.md |
| SYS-CR-004 | (none — protocol timing) | apb_interconnect | APB v2.0: no wait states, ≤ 2 cycles per transaction |
| SYS-CR-005 | WB_WINDOW_BASE | wb_bridge | Wishbone B4 pipelined, CTI/BTE burst support |
| SYS-CR-006 | (none — structural CDC) | wb_bridge | 2-FF sync for single-bit; async FIFO for multi-bit |
| SYS-CR-007 | (none — structural reset) | TOP | Async assert, sync deassert to clk_sys posedge |
| SYS-CR-008 | SRAM_SIZE (aspect ratio) | sram | OpenRAM macro aspect ≤ 4:1 |
| SYS-CR-009 | (none — IO cell selection) | caravel_wrapper | sky130_fd_io pads with ESD diodes |
| SYS-CR-010 | (none — precheck gate) | caravel_wrapper | Caravel precheck: no comb loops, no unmapped I/O, no floating nets |
| SYS-CR-011 | SYSCTRL.CLK_DIV | TOP | Single clock domain from user_clock2; local gating |

---

## Config Key → Requirement Reverse Trace

| Config Key | Binding Requirement(s) |
|------------|----------------------|
| UART.BAUD_DIV | SYS-FR-002, SYS-PR-005, SYS-IR-001 |
| UART.FIFO_THRESH | SYS-FR-002, SYS-AR-006, SYS-AR-007 |
| UART.CONTROL | SYS-FR-002 |
| SPI.CLK_DIV | SYS-FR-003, SYS-PR-006, SYS-IR-002 |
| SPI.CONTROL | SYS-FR-003, SYS-IR-002 |
| I2C.CLK_DIV_LO | SYS-FR-004, SYS-PR-007, SYS-PR-010, SYS-IR-003 |
| I2C.CLK_DIV_HI | SYS-FR-004, SYS-PR-007, SYS-PR-010, SYS-IR-003 |
| I2C.CONTROL | SYS-FR-004, SYS-AR-008 |
| GPIO.DIR | SYS-FR-005, SYS-IR-004 |
| GPIO.IRQ_EN | SYS-FR-005, SYS-PR-012, SYS-AR-011 |
| GPIO.IRQ_EDGE | SYS-FR-005 |
| GPIO.IRQ_STATUS | SYS-FR-005 |
| PWM.PERIOD | SYS-FR-006, SYS-PR-009, SYS-IR-005 |
| PWM.DUTY_CH0 | SYS-FR-006, SYS-PR-008, SYS-IR-005 |
| PWM.DUTY_CH1 | SYS-FR-006, SYS-PR-008, SYS-IR-005 |
| PWM.CONTROL | SYS-FR-006, SYS-PR-009, SYS-IR-005 |
| IRQ.IRQ_EN | SYS-FR-011, SYS-PR-012, SYS-AR-005, SYS-AR-006, SYS-AR-007 |
| IRQ.IRQ_PENDING | SYS-FR-011 |
| WDT.RELOAD | SYS-FR-012, SYS-AR-012 |
| WDT.CONTROL | SYS-FR-012, SYS-AR-012 |
| SYSCTRL.CHIP_ID | SYS-FR-014 |
| SYSCTRL.CLK_DIV | SYS-FR-013, SYS-CR-011 |
| SYSCTRL.RESET_CAUSE | (architectural — no direct SYS-xx, supports SYS-AR-012) |
| SYSCTRL.SLEEP_CTRL | SYS-FR-013, SYS-PR-003, SYS-AR-010, SYS-AR-011 |
| CLOCK_PERIOD | SYS-PR-001, SYS-PR-004, SYS-IR-007 |
| SRAM_SIZE | SYS-FR-007, SYS-PR-011, SYS-CR-008 |
| SRAM_BASE | SYS-FR-007, SYS-AR-001 |
| APB_SLAVE_COUNT | SYS-FR-008, SYS-AR-004 |
| WB_WINDOW_BASE | SYS-FR-009, SYS-IR-006, SYS-CR-005 |

---

## Integrity Checks

| Check | Result |
|-------|--------|
| Every config key binds to ≥ 1 requirement | 29/29 config keys have ≥ 1 binding — PASS |
| Every MUST requirement binds to ≥ 1 config key (for tunable requirements) | All 37 MUST reqs with tunable values have bindings — PASS |
| Every SYS-xx-NNN appears at least once | 61/61 requirements in forward map — PASS |
| No orphan config keys (key with no requirement) | 0 orphan keys — PASS |
| Reverse trace completeness | 29 config keys reversely traced; SYSCTRL.RESET_CAUSE documented as architectural — PASS |
