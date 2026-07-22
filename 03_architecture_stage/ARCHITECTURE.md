# Architecture — PRJ-001 (Argus) Environmental Sensor-Hub SoC

> **Tier:** Easy (MVP)
> **PDK:** sky130A (SkyWater 130nm, sky130_fd_sc_hd)
> **Frequency:** 50 MHz target / 25 MHz fallback
> **Created:** 2026-07-20
> **Architect:** architect-engineer (Hermes)

---

## 1. Overview

PRJ-001 "Argus" is an environmental sensor-hub SoC built around the lowRISC Ibex RV32I
processor core (2-stage pipeline, "maxperf" config). The design uses a single-clock-domain
APB v2.0 peripheral bus connecting the Ibex core to six sensor/actuator peripherals (UART,
SPI master, I2C master, GPIO, PWM, system control), a 4 KB OpenRAM SRAM macro, a 13-source
interrupt controller, and an APB↔Wishbone B4 bridge for Caravel harness integration. All
peripherals except the custom interrupt controller and bridge are Efabless FOSSi IP blocks
(EF_UART, EF_SPI, EF_I2C, EF_GPIO8, EF_TMR32).

The SoC targets the Caravel MPW harness on sky130A. A single 50 MHz clock domain (derived
from Caravel user_clock2) drives all internal logic. An async FIFO-based CDC crossing
isolates the internal APB domain from the Caravel Wishbone management interface.

**Block Diagram:** see `block_diagrams/top_level.html`

**Key Specifications:**

| Spec | Value | Source |
|------|-------|--------|
| ISA | RV32I (no M, no C, no F, no A) | system_spec.md §2.3, Vera directive |
| Core | lowRISC Ibex, 2-stage "maxperf" | REUSE, IP-INDEX: lowrisc-ibex, STRONG |
| Pipeline | 2-stage (IF→ID/EX→WB), no forwarding | Ibex fixed architecture |
| Internal Bus | APB v2.0, single-cycle, no wait states | system_spec.md §8, SYS-CR-004 |
| External Bus | Wishbone B4 pipelined → Caravel mgmt SoC | system_spec.md §5, SYS-IR-006 |
| SRAM | 4 KB OpenRAM, zero-wait-state at 50 MHz | REUSE, IP-INDEX: vlsida-openram, STRONG |
| Frequency | 50 MHz (target) / 25 MHz (fallback) | system_spec.md §4, SYS-PR-001 |
| PDK | sky130A (sky130_fd_sc_hd) | system_spec.md §7, SYS-CR-002 |
| Clock domains | 2 (clk_sys=50MHz, clk_wb=10-25MHz) | system_spec.md §9.1 |
| Interrupts | 13-source custom controller → 1 CPU IRQ | system_spec.md §8, Vera directive |
| Total I/O pins | 18 used, 20 reserved | UART(2)+SPI(4)+I2C(2)+GPIO(8)+PWM(2) |

---

## 2. Memory Map

### 2.1 Full Address Space

| Region | Base Address | Size | Access | Owner Block | Description |
|--------|-------------|------|--------|-------------|-------------|
| SRAM | 0x0000_0000 | 4 KB (0x1000) | R/W/X | sram (M08) | Firmware code, stack, heap, sensor data buffer |
| Reserved (SRAM expansion) | 0x0000_1000 | 60 KB (0xF000) | — | — | Reserved for future SRAM expansion |
| UART | 0x0001_0000 | 256 B (0x100) | R/W | uart (M03) | UART TX/RX data, status, control, baud config |
| SPI | 0x0001_0100 | 256 B (0x100) | R/W | spi_master (M04) | SPI data, status, control, clock config |
| I2C | 0x0001_0200 | 256 B (0x100) | R/W | i2c_master (M05) | I2C data, status, control, clock config |
| GPIO | 0x0001_0300 | 256 B (0x100) | R/W | gpio (M06) | GPIO data, direction, interrupt enable/status/edge |
| PWM | 0x0001_0400 | 256 B (0x100) | R/W | pwm (M07) | PWM period, duty cycle (ch0/ch1), control, status |
| Interrupt Controller | 0x0001_0500 | 256 B (0x100) | R/W | interrupt_ctrl (M09) | IRQ enable, pending per source |
| Watchdog Timer | 0x0001_0600 | 256 B (0x100) | R/W | pwm/wdt (M07) | Watchdog reload, counter, control |
| System Control | 0x0001_0700 | 256 B (0x100) | R/W | sys_ctrl (M12) | Chip ID, clock divider, reset cause, sleep control |
| Reserved (peripheral) | 0x0001_0800 | 62 KB (0xF800) | — | — | Reserved for future peripherals |
| Wishbone Window | 0x8000_0000 | 2 GB (0x8000_0000) | R/W (from Caravel) | wb_bridge (M10) | Caravel Wishbone → APB bridge address window |

### 2.2 Boot/Reset Vector

- **Boot address:** 0x0000_0000 (SRAM base)
- Firmware loaded by Caravel management SoC via Wishbone bridge before reset deassertion
- No boot ROM — Ibex fetches first instruction from SRAM at 0x0000_0000
- Reset vector: mtvec default = 0x0000_0000 (direct mode)

### 2.3 APB Address Decode

The APB interconnect (M02) decodes the 32-bit address as:

```
if addr[31] == 1:                    → wb_bridge window (APB slave port)
elif addr[31:16] == 0x0001:          → peripheral region
    addr[15:8] selects peripheral:
        0x00 → UART
        0x01 → SPI
        0x02 → I2C
        0x03 → GPIO
        0x04 → PWM
        0x05 → Interrupt Ctrl
        0x06 → Watchdog (PWM timer repurpose)
        0x07 → System Control
elif addr[31:12] == 0x0000_0:        → SRAM (0x0000_0000 – 0x0000_0FFF)
else:                                → Unmapped (PSLVERR)
```

Peripheral register offset is `addr[7:0]` within the 256 B allocation.

---

## 3. Pipeline & Core Architecture

### 3.1 Ibex Core (M01)

The Ibex core is used as a fixed REUSE IP block (lowRISC, Apache-2.0). Its internal
microarchitecture is defined upstream and is NOT re-architected here.

**Ibex Configuration (PRJ-001):**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| RV32E | 0 | Full RV32I register file (32 regs) |
| RV32M | 0 | M extension OUT OF SCOPE per spec §1.2 |
| RV32C | 0 | C extension not needed; reduces decoder area |
| Pipeline | 2-stage (IF→ID/EX→WB) | "maxperf" config; single-cycle execution for most instructions |
| PMP | 0 | No Physical Memory Protection (M-mode only) |
| Debug | 0 | No debug module (Easy tier) |
| ICache | 0 | No instruction cache |
| BranchPredictor | Static (branch-not-taken) | Simplest; adequate for sensor polling |
| MHPMCounter | 0 | No performance counters |

**Ibex core interface to SoC:**

| Signal | Direction | Width | Description |
|--------|-----------|-------|-------------|
| instr_req_o | Output | 1 | Instruction fetch request to SRAM |
| instr_addr_o | Output | 32 | Instruction fetch address |
| instr_rdata_i | Input | 32 | Instruction word from SRAM |
| instr_rvalid_i | Input | 1 | Instruction data valid |
| data_req_o | Output | 1 | Data load/store request |
| data_addr_o | Output | 32 | Data access address |
| data_wdata_o | Output | 32 | Store data |
| data_we_o | Output | 1 | Write enable |
| data_be_o | Output | 4 | Byte enable |
| data_rdata_i | Input | 32 | Load data |
| data_rvalid_i | Input | 1 | Load data valid |
| irq_software_i | Input | 1 | Software interrupt (unused, tied low) |
| irq_timer_i | Input | 1 | Timer interrupt (unused, tied low) |
| irq_external_i | Input | 1 | External interrupt from M09 (interrupt_ctrl) |
| irq_fast_i | Input | 15 | Fast interrupt lines (unused, tied low) |
| debug_req_i | Input | 1 | Debug request (tied low) |
| core_sleep_o | Output | 1 | Core in WFI (routed to sys_ctrl) |

### 3.2 APB Bus Topology

The Ibex core's instruction and data memory ports connect directly to the SRAM controller
(not through the APB bus — Harvard split at the SRAM interface). All peripheral register
accesses go through the APB bus via the Ibex data interface when `data_addr_o` targets the
peripheral region (`addr[31:16] == 0x0001`).

Bus topology:

```
                    ┌──────────┐
                    │   Ibex   │
                    │  RV32I   │
                    └──┬───┬───┘
              instr_req │   │ data_req (addr=SRAM)
                       │   │
              ┌────────▼───▼─────────┐
              │      SRAM (M08)      │
              │      4 KB macro      │
              │  (IMEM + DMEM ports) │
              └──────────────────────┘

         data_req (addr=0x0001_xxxx or 0x8000_0000)
                       │
              ┌────────▼────────┐
              │ APB Interconnect │  ← M02 (CREATE)
              │   addr decode   │
              │   mux + routing │
              └──┬─┬─┬─┬─┬─┬─┬──┘
                 │ │ │ │ │ │ └─────► wb_bridge (slave port, Wishbone window)
                 │ │ │ │ │ └───────► sys_ctrl   (0x0001_0700)
                 │ │ │ │ └─────────► pwm/wdt    (0x0001_0400/0x0001_0600)
                 │ │ │ └───────────► irq_ctrl   (0x0001_0500)
                 │ │ └─────────────► gpio       (0x0001_0300)
                 │ └───────────────► i2c        (0x0001_0200)
                 └─────────────────► uart+spi   (0x0001_0000/0x0001_0100)
```

APB bus rules (per SYS-CR-004, SYS-AR-002, SYS-AR-003, SYS-AR-004):
- Single-cycle read/write (PREADY asserted same cycle as PENABLE)
- PSLVERR on unmapped address (addr decode miss)
- No wait states, no retry
- All peripherals are APB slaves; Ibex data port is the APB master through the interconnect

### 3.3 Interrupt Routing

13 sources → 1 CPU IRQ (custom aggregator, M09):

```
  UART IRQ ────┐
  SPI IRQ  ────┤
  I2C IRQ  ────┤
  GPIO[0] ─────┤
  GPIO[1] ─────┤
  GPIO[2] ─────┤
  GPIO[3] ─────┤  ┌──────────────┐     ┌────────┐
  GPIO[4] ─────┼──►  interrupt_ctrl ├────►│  Ibex  │
  GPIO[5] ─────┤  │  (M09, CREATE) │     │irq_ext │
  GPIO[6] ─────┤  │                │     └────────┘
  GPIO[7] ─────┤  │  per-source:   │
  PWM IRQ  ────┤  │  IRQ_EN mask   │
  WDT IRQ  ────┘  │  IRQ_PENDING   │
                  └──────────────┘
```

IRQ source assignment (from golden model, matches spec):

| Source # | Signal | M09 bit | Description |
|----------|--------|---------|-------------|
| 0 | IRQ_UART | 0 | UART TX/RX threshold |
| 1 | IRQ_SPI | 1 | SPI transfer complete / RX data available |
| 2 | IRQ_I2C | 2 | I2C transfer complete |
| 3 | IRQ_GPIO0 | 3 | GPIO pin 0 edge |
| 4 | IRQ_GPIO1 | 4 | GPIO pin 1 edge |
| 5 | IRQ_GPIO2 | 5 | GPIO pin 2 edge |
| 6 | IRQ_GPIO3 | 6 | GPIO pin 3 edge |
| 7 | IRQ_GPIO4 | 7 | GPIO pin 4 edge |
| 8 | IRQ_GPIO5 | 8 | GPIO pin 5 edge |
| 9 | IRQ_GPIO6 | 9 | GPIO pin 6 edge |
| 10 | IRQ_GPIO7 | 10 | GPIO pin 7 edge |
| 11 | IRQ_PWM | 11 | PWM period match |
| 12 | IRQ_WDT | 12 | Watchdog timeout warning |

All peripheral IRQs are level-sensitive, synchronous to clk_sys. CPU IRQ remains
asserted until the firmware reads the pending status register (or the peripheral
itself clears the interrupt condition).

---

## 4. Modules

### M01 — ibex_core

- **Source:** REUSE, lowrisc-ibex (Apache-2.0), STRONG tier
- **Reference:** https://github.com/lowRISC/ibex
- **Config:** RV32I, 2-stage "maxperf", no M/C/PMP/Debug/ICache

**Purpose:** 32-bit RISC-V processor executing the RV32I instruction set. Provides the
programmable control plane for sensor polling, data processing, and peripheral management.

**Interface:** See §3.1 Ibex core interface table.

**Functional Description:**
Standard Ibex 2-stage pipeline. Instruction fetch and data access both target the SRAM
macro (Harvard-style split at the memory interface level). The core boots from SRAM at
address 0x0000_0000 after reset deassertion. External interrupt line connected to
interrupt_ctrl CPU IRQ output. No timer or software interrupts used.

**Timing Notes:**
- Clock domain: clk_sys (50 MHz)
- Most ALU ops: 1 cycle (single-cycle execute)
- Loads: 2 cycles (pipeline stall)
- Branches: 2 cycles (mispredict penalty for taken branches)
- Multicycle ops: none (no M extension)

**Edge Cases:**
- Reset values: All architectural registers = 0x0000_0000. PC = 0x0000_0000 (reset vector).
  CSRs per RISC-V spec: mstatus=0, mie=0, mtvec=0, mcause=0.
- Default outputs: instr_req_o=0, data_req_o=0 when sleeping (WFI). core_sleep_o=1 during WFI.
- Non-obvious: Ibex "maxperf" config uses static branch prediction (not-taken). Taken branches
  cost 2 cycles. No forwarding — load-use penalty is 1 stall cycle.

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~15 kGE |
| Expected FFs | ~800 (pipeline + register file + CSRs) |
| Critical path | ~12 ns (Ibex characterized at 100 MHz sky130A; 50 MHz has ~8 ns slack) |

---

### M02 — apb_interconnect

- **Source:** CREATE
- **Complexity:** Moderate

**Purpose:** APB v2.0 bus fabric. Address decoder, mux, and routing connecting the Ibex
data port (APB master) to up to 12 APB slave ports.

**Interface:**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| master_paddr | Input | 32 | Address from Ibex data port |
| master_pwdata | Input | 32 | Write data from Ibex |
| master_pwrite | Input | 1 | Write=1, Read=0 |
| master_psel | Input | 1 | Transaction select |
| master_penable | Input | 1 | Strobe |
| master_prdata | Output | 32 | Read data to Ibex |
| master_pready | Output | 1 | Transfer complete |
| master_pslverr | Output | 1 | Transfer error |
| slave_paddr[N] | Output | 32 | Address to slave N |
| slave_pwdata[N] | Output | 32 | Write data to slave N |
| slave_pwrite[N] | Output | 1 | Direction to slave N |
| slave_psel[N] | Output | 1 | Select slave N |
| slave_penable[N] | Output | 1 | Strobe to slave N |
| slave_prdata[N] | Input | 32 | Read data from slave N |
| slave_pready[N] | Input | 1 | Ready from slave N |
| slave_pslverr[N] | Input | 1 | Error from slave N |

**Functional Description:**
1. Decode `master_paddr` against the memory map (§2.1)
2. Assert exactly one `slave_psel[N]` for valid addresses
3. Route `paddr`, `pwdata`, `pwrite`, `penable` to selected slave
4. OR together all `slave_pready[N]` → `master_pready`
5. Mux selected `slave_prdata[N]` → `master_prdata`
6. OR `slave_pslverr[N]` → `master_pslverr`
7. Unmapped address: assert `master_pslverr`, `master_pready`, no slave selected

**Edge Cases:**
- Reset values: No state — purely combinational decode + registered slave select outputs.
  Registered outputs reset to 0 (no slave selected).
- Default outputs: All slave_psel=0, slave_penable=0. master_prdata=0 when no slave selected.
- Non-obvious: Address decode is combinational (within one clk_sys cycle). PSLVERR asserted
  for any address outside SRAM (0x0000_0xxx), peripheral (0x0001_0xxx), or Wishbone window
  (0x8xxx_xxxx) regions.

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~3 kGE |
| Expected FFs | ~200 (registered slave select/control outputs) |
| Critical path | ~3 ns (address decode mux chain) |

---

### M03 — uart

- **Source:** REUSE, fossi-ef-uart (Apache-2.0), STRONG tier
- **Reference:** https://github.com/efabless/fossi-ef-uart

**Purpose:** Full-duplex UART with 8-byte TX and RX FIFOs. Configurable baud rate.
115200 bps target at 50 MHz.

**Interface:**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| paddr | Input | 8 | APB register address |
| pwdata | Input | 32 | APB write data |
| prdata | Output | 32 | APB read data |
| pwrite | Input | 1 | APB write enable |
| psel | Input | 1 | APB select |
| penable | Input | 1 | APB enable |
| pready | Output | 1 | APB ready |
| pslverr | Output | 1 | APB error (unused, tied 0) |
| uart_tx | Output | 1 | Transmit data (to IO pad) |
| uart_rx | Input | 1 | Receive data (from IO pad) |
| irq_o | Output | 1 | Combined TX/RX interrupt |

**Register Map:**

| Offset | Register | Width | Access | Reset | Description |
|--------|----------|-------|--------|-------|-------------|
| 0x00 | TXDATA | 8 | W | 0x00 | Transmit data (pushes to TX FIFO) |
| 0x04 | RXDATA | 8 | R | 0x00 | Receive data (pops from RX FIFO) |
| 0x08 | STATUS | 8 | R | 0x0A | [7:5] reserved, [4] RX overrun, [3] RX empty, [2] RX full, [1] TX empty, [0] TX full |
| 0x0C | CONTROL | 8 | R/W | 0x00 | [7:2] reserved, [1] RX enable, [0] TX enable |
| 0x10 | BAUD_DIV | 16 | R/W | 0x01B2 | Baud divisor = f_clk / baud_rate (434 = 115200 at 50 MHz) |
| 0x14 | FIFO_THRESH | 8 | R/W | 0x41 | [7:4] RX threshold, [3:0] TX threshold |

**Functional Description:**
Standard UART 8N1 framing. TX FIFO (8 bytes deep) loaded via TXDATA writes, shifted out
at baud rate. RX FIFO (8 bytes deep) captures received bits, available via RXDATA reads.
Baud rate = f_sys / BAUD_DIV. Interrupts: TX when FIFO depth < TX threshold; RX when
FIFO depth ≥ RX threshold.

**Edge Cases:**
- W1C: No W1C registers in UART. IRQ cleared by reading RXDATA (drain RX FIFO below threshold)
  or writing TXDATA (fill TX FIFO above threshold).
- Read-clear: RXDATA read pops from RX FIFO. STATUS bits reflect current FIFO state.
- Reset values: All registers 0x00 except STATUS=0x0A (TX empty + RX empty), BAUD_DIV=0x01B2 (434).
- Default outputs: uart_tx=1 (idle high). irq_o=0.
- Non-obvious: RX overrun (STATUS[4]) is sticky until read — but reading STATUS alone does
  NOT clear it; a RXDATA read is needed to advance the FIFO. Writing TXDATA while TX FIFO
  is full silently drops the byte (per EF_UART behavior).

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~2 kGE |
| Expected FFs | ~150 (2×8-byte FIFO + control/status) |
| Critical path | ~5 ns (baud divider chain) |

---

### M04 — spi_master

- **Source:** REUSE, fossi-ef-spi (Apache-2.0), STRONG tier
- **Reference:** https://github.com/efabless/fossi-ef-spi

**Purpose:** SPI master supporting Mode 0 (CPOL=0, CPHA=0) and Mode 3 (CPOL=1, CPHA=1).
Up to f_sys/4 SCLK (12.5 MHz at 50 MHz). 8-byte FIFOs.

**Interface:**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| paddr | Input | 8 | APB register address |
| pwdata | Input | 32 | APB write data |
| prdata | Output | 32 | APB read data |
| pwrite | Input | 1 | APB write enable |
| psel | Input | 1 | APB select |
| penable | Input | 1 | APB enable |
| pready | Output | 1 | APB ready |
| sck | Output | 1 | SPI clock |
| mosi | Output | 1 | Master-out slave-in |
| miso | Input | 1 | Master-in slave-out |
| cs_n | Output | 4 | Chip select (only cs_n[0] used) |
| irq_o | Output | 1 | Transfer complete / RX data available |

**Register Map:**

| Offset | Register | Width | Access | Reset | Description |
|--------|----------|-------|--------|-------|-------------|
| 0x00 | TXDATA | 8 | W | 0x00 | Write byte to TX FIFO (starts transfer) |
| 0x04 | RXDATA | 8 | R | 0x00 | Read byte from RX FIFO |
| 0x08 | STATUS | 8 | R | 0x01 | [5] CPHA, [4] CPOL, [3:2] reserved, [1] RX full, [0] TX empty |
| 0x0C | CONTROL | 8 | R/W | 0x00 | [4] CS enable, [3:2] reserved, [1] CPHA, [0] CPOL |
| 0x10 | CLK_DIV | 8 | R/W | 0x02 | SCLK divider = f_sys / (2 × CLK_DIV). Min=2 → 12.5 MHz |

**Functional Description:**
Full-duplex SPI master. Writing TXDATA starts an 8-bit transfer on the SPI bus. MISO is
sampled simultaneously; received byte placed in RX FIFO. CS is asserted before transfer
and deasserts after. Mode 0 (CPOL=0, CPHA=0): data sampled on rising edge. Mode 3
(CPOL=1, CPHA=1): data sampled on rising edge (inverted idle).

**Edge Cases:**
- W1C: No W1C registers.
- Read-clear: RXDATA read pops from RX FIFO.
- Reset values: All registers 0x00 except STATUS=0x01 (TX empty), CLK_DIV=0x02.
- Default outputs: sck=CPOL, mosi=0, cs_n=1. irq_o=0.
- Non-obvious: CLK_DIV minimum is 2. Writing CLK_DIV=0 or 1 defaults to CLK_DIV=2.
  STATUS bits [5:4] reflect current CONTROL settings. TXDATA write while busy is
  buffered in TX FIFO (up to 8 bytes).

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~2 kGE |
| Expected FFs | ~120 (shift register + 2×8-byte FIFO + control) |
| Critical path | ~4 ns (prescaler + shift logic) |

---

### M05 — i2c_master

- **Source:** REUSE, fossi-ef-i2c (Apache-2.0), STRONG tier
- **Reference:** https://github.com/efabless/fossi-ef-i2c

**Purpose:** I2C master controller at 100 kHz (standard) and 400 kHz (fast) with 7-bit
addressing, multi-byte read/write, and repeated start.

**Interface:**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| paddr | Input | 8 | APB register address |
| pwdata | Input | 32 | APB write data |
| prdata | Output | 32 | APB read data |
| pwrite | Input | 1 | APB write enable |
| psel | Input | 1 | APB select |
| penable | Input | 1 | APB enable |
| pready | Output | 1 | APB ready |
| scl | Bidir | 1 | I2C clock (open-drain, external pull-up) |
| sda | Bidir | 1 | I2C data (open-drain, external pull-up) |
| irq_o | Output | 1 | Transfer complete / error |

**Register Map:**

| Offset | Register | Width | Access | Reset | Description |
|--------|----------|-------|--------|-------|-------------|
| 0x00 | DATA | 8 | R/W | 0x00 | Transmit/receive data byte |
| 0x04 | ADDR | 8 | R/W | 0x00 | [7:1]=7-bit slave addr, [0]=R/W |
| 0x08 | STATUS | 8 | R | 0x10 | [4] transfer done, [3] ARB lost, [2] NACK, [0] busy |
| 0x0C | CONTROL | 8 | R/W | 0x00 | [3] IRQ enable, [2] repeated start, [1] STOP, [0] START |
| 0x10 | CLK_DIV_LO | 8 | R/W | 0x7D | SCL low period = (CLK_DIV_LO+1) × t_sys |
| 0x14 | CLK_DIV_HI | 8 | R/W | 0x7D | SCL high period = (CLK_DIV_HI+1) × t_sys |

**Functional Description:**
Byte-level I2C master. Firmware sets ADDR (slave addr + R/W) and DATA, then writes
START to CONTROL. The state machine generates START, sends address byte, waits for ACK,
sends/receives data byte, then generates STOP (or repeated START). NACK from slave sets
STATUS[2] and aborts the transaction with STOP. Arbitration loss detection (STATUS[3])
for multi-master safety (not actively used).

**Edge Cases:**
- W1C: No W1C registers. STATUS bits are cleared by starting a new transaction or by
  reading STATUS after transaction completion.
- Read-clear: STATUS read does NOT clear bits. Only a new START clears busy/NACK/ARBLOST.
  Transfer done (STATUS[4]) persists until next START.
- Reset values: All registers 0x00 except STATUS=0x10 (transfer done, idle), CLK_DIV_LO/HI=0x7D (125).
- Default outputs: scl=Z (open-drain, pulled high externally), sda=Z. irq_o=0.
- Non-obvious: SCL frequency = f_sys / (CLK_DIV_LO + CLK_DIV_HI + 2). At reset defaults:
  50M/(125+125+2) = ~198 kHz (near 200 kHz center). Must write CLK_DIV_LO=CLK_DIV_HI=62
  for 400 kHz (400 kHz = 50M/126 → div=61.5). Address 0x78-0x7F are reserved I2C addresses;
  the EF_I2C hardware does NOT reject them, but the golden model simulates NACK for addr≥0x78.

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~2 kGE |
| Expected FFs | ~100 (state machine + byte-level shift + timer) |
| Critical path | ~5 ns (SCL timing divider + I2C FSM) |

---

### M06 — gpio

- **Source:** REUSE, fossi-ef-gpio8 (Apache-2.0), STRONG tier
- **Reference:** https://github.com/efabless/fossi-ef-gpio8

**Purpose:** 8-pin GPIO with per-pin direction control, per-pin edge-detect interrupt
(rising, falling, both), and W1C interrupt status.

**Interface:**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| paddr | Input | 8 | APB register address |
| pwdata | Input | 32 | APB write data |
| prdata | Output | 32 | APB read data |
| pwrite | Input | 1 | APB write enable |
| psel | Input | 1 | APB select |
| penable | Input | 1 | APB enable |
| pready | Output | 1 | APB ready |
| gpio[7:0] | Bidir | 8 | GPIO pins (to IO pads) |
| irq_o | Output | 8 | Per-pin interrupt (one line per pin to M09) |

**Register Map:**

| Offset | Register | Width | Access | Reset | Description |
|--------|----------|-------|--------|-------|-------------|
| 0x00 | DATA_OUT | 8 | R/W | 0x00 | Output data for pins configured as output |
| 0x04 | DATA_IN | 8 | R | — | Input data from pins (read-only) |
| 0x08 | DIR | 8 | R/W | 0x00 | Direction: 1=output, 0=input per pin |
| 0x0C | IRQ_EN | 8 | R/W | 0x00 | Interrupt enable per pin |
| 0x10 | IRQ_EDGE | 16 | R/W | 0x0000 | [15:8]=falling enable, [7:0]=rising enable |
| 0x14 | IRQ_STATUS | 8 | R/W1C | 0x00 | Pending interrupt per pin (write 1 to clear) |

**Functional Description:**
DIR register controls per-pin direction. Output pins drive DATA_OUT value. Input pins
read external level into DATA_IN. Edge detection: rising edge = transition 0→1;
falling edge = 1→0; configurable per-pin via IRQ_EDGE. When edge detected AND IRQ_EN[pin]=1,
IRQ_STATUS[pin] is set. IRQ_STATUS is Write-1-to-Clear: firmware writes 1 to clear.

**Edge Cases:**
- **W1C:** IRQ_STATUS is W1C per-pin. Writing 1 to bit N clears IRQ_STATUS[N]. Writing 0
  has no effect. W1C has higher priority than edge detection — if a new edge occurs in the
  same cycle as W1C clear, the IRQ_STATUS bit is set (hardware set wins if simultaneous).
- Read-clear: No read-clear behavior. Reading IRQ_STATUS returns current value without
  modification.
- Reset values: DATA_OUT=0x00, DIR=0x00 (all inputs), IRQ_EN=0x00, IRQ_EDGE=0x0000,
  IRQ_STATUS=0x00. DATA_IN reflects external pin state.
- Default outputs: gpio pins are inputs (DIR=0) after reset — high-impedance state driven
  by external circuitry. irq_o=0.
- Non-obvious: DIR register is applied combinatorially — changing DIR from input to output
  immediately drives DATA_OUT onto the pin. No synchronization delay.

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~1 kGE |
| Expected FFs | ~80 (DATA_OUT + DIR + IRQ_EN + IRQ_EDGE + IRQ_STATUS + edge detect sync) |
| Critical path | ~3 ns (edge detect + IRQ mux) |

---

### M07 — pwm (with watchdog)

- **Source:** REUSE* (fossi-ef-tmr32, Apache-2.0, STRONG tier, adapted)
- **Reference:** https://github.com/efabless/fossi-ef-tmr32
- **REUSE* Justification:** PWM mode uses TMR32 compare-match outputs. Watchdog repurposes
  TMR32 overflow interrupt. No source changes to TMR32 core — all adaptation in wrapper.

**Purpose:** 2-channel PWM (10-bit resolution, 1–25 kHz base) plus watchdog timer from
the same 32-bit EF_TMR32 IP block.

**Interface (PWM registers at 0x0001_0400):**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| paddr | Input | 8 | APB register address (PWM base) |
| pwdata | Input | 32 | APB write data |
| prdata | Output | 32 | APB read data |
| pwrite | Input | 1 | APB write enable |
| psel | Input | 1 | APB select |
| penable | Input | 1 | APB enable |
| pready | Output | 1 | APB ready |
| pwm[0] | Output | 1 | Channel 0 output |
| pwm[1] | Output | 1 | Channel 1 output |
| irq_o | Output | 1 | PWM period match interrupt |
| wdt_irq_o | Output | 1 | Watchdog timeout warning (to M09 IRQ[12]) |
| wdt_rst_n | Output | 1 | Watchdog system reset (to sys_ctrl) |

**PWM Register Map (0x0001_0400):**

| Offset | Register | Width | Access | Reset | Description |
|--------|----------|-------|--------|-------|-------------|
| 0x00 | PERIOD | 16 | R/W | 0x07D0 | PWM period in clock cycles (default 2000 → 25 kHz) |
| 0x04 | DUTY_CH0 | 16 | R/W | 0x0000 | Channel 0 duty cycle |
| 0x08 | DUTY_CH1 | 16 | R/W | 0x0000 | Channel 1 duty cycle |
| 0x0C | CONTROL | 8 | R/W | 0x00 | [6:4] prescaler, [1] ch1 enable, [0] ch0 enable |

**Watchdog Register Map (0x0001_0600):**

| Offset | Register | Width | Access | Reset | Description |
|--------|----------|-------|--------|-------|-------------|
| 0x00 | RELOAD | 24 | R/W | 0xFFFFFF | Watchdog reload value (in clock cycles) |
| 0x04 | COUNTER | 24 | R | 0xFFFFFF | Current counter value |
| 0x08 | CONTROL | 8 | R/W | 0x00 | [1] enable, [0] pet (write 1 to reload) |

**Functional Description:**
- **PWM mode:** EF_TMR32 configured as up-counter. Period defines max count. CH0 and CH1
  duties set compare-match thresholds. When counter < duty: output high; counter ≥ duty:
  output low. PWM frequency = f_sys / (PERIOD × prescaler). At PERIOD=2000, prescaler=1:
  50 MHz / 2000 = 25 kHz base. 10-bit effective resolution.
- **Watchdog mode:** EF_TMR32 overflow counter. Firmware writes RELOAD value and enables.
  Counter decrements each clock cycle. Firmware pets by writing 1 to CONTROL[0] (reloads
  counter from RELOAD). If counter reaches zero: wdt_rst_n asserted for 16 cycles.

**Edge Cases:**
- W1C: No W1C registers in PWM. Watchdog CONTROL[0] is pet (write 1 to reload counter).
  CONTROL[1] is enable (1=enable, 0=disable).
- Read-clear: No read-clear behavior. COUNTER is read-only.
- Reset values: PERIOD=2000, DUTY_CH0=0, DUTY_CH1=0, CONTROL=0x00 (both channels disabled).
  RELOAD=0xFFFFFF, COUNTER=0xFFFFFF, WDT disabled.
- Default outputs: pwm[0]=0, pwm[1]=0. irq_o=0. wdt_irq_o=0. wdt_rst_n=1 (not asserted).
- Non-obvious: DUTY values clamped to PERIOD at write (duty > period → duty = period).
  PWM output is 0 when channel disabled or DUTY=0. PWM output stays high (100%) when
  DUTY=PERIOD. Watchdog COUNTER freezes when disabled; re-enabling resumes from frozen value
  (not reloaded). WDT timeout triggers wdt_irq_o at counter < RELOAD/4 (early warning), then
  wdt_rst_n at counter=0.

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~4 kGE (TMR32 core ~3 kGE + PWM/WDT wrapper ~1 kGE) |
| Expected FFs | ~200 (32-bit counter + 2×16-bit compare + control) |
| Critical path | ~3 ns (32-bit counter increment) |

---

### M08 — sram

- **Source:** REUSE, vlsida-openram (BSD-3-Clause), STRONG tier
- **Reference:** https://github.com/VLSIDA/OpenRAM

**Purpose:** 4 KB single-port SRAM macro for firmware code, stack, heap, and sensor data
buffer. Zero-wait-state at 50 MHz.

**Interface:**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| imem_addr | Input | 32 | Instruction fetch address from Ibex |
| imem_rdata | Output | 32 | Instruction word to Ibex |
| dmem_addr | Input | 32 | Data access address from Ibex |
| dmem_wdata | Input | 32 | Store data from Ibex |
| dmem_rdata | Output | 32 | Load data to Ibex |
| dmem_we | Input | 1 | Write enable |
| dmem_be | Input | 4 | Byte enable |
| apb_paddr | Input | 12 | APB address (word-aligned for SRAM region) |
| apb_pwdata | Input | 32 | APB write data |
| apb_prdata | Output | 32 | APB read data |
| apb_pwrite | Input | 1 | APB write enable |
| apb_psel | Input | 1 | APB select |
| apb_penable | Input | 1 | APB enable |
| apb_pready | Output | 1 | APB ready |

**Functional Description:**
The SRAM controller arbitrates between the Ibex instruction port, Ibex data port, and
APB access (from Caravel management SoC via Wishbone bridge). Priority: Ibex instruction
fetch > Ibex data access > APB access. All accesses are single-cycle at 50 MHz. The
macro is byte-addressable via the APB port using byte-enable masking.

**Edge Cases:**
- Reset values: SRAM contents UNDEFINED after power-on reset (not initialized). Firmware
  loaded by Caravel mgmt SoC after power-up but before Ibex reset deassertion.
- Default outputs: imem_rdata=0x0000_0000, dmem_rdata=0x0000_0000, apb_prdata=0x0000_0000
  during idle/no-select.
- Non-obvious: Memory contention: if Ibex instruction and data ports access the same address
  in the same cycle, the data port stalls for 1 cycle. OpenRAM macro aspect ratio ≤ 4:1
  per SYS-CR-008. The SRAM macro itself is a hard macro — the controller is synthesized
  around it.

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~40 kGE (macro) + ~1 kGE (controller) |
| Expected FFs | ~0 (SRAM array, no FFs in macro) |
| Critical path | ~3 ns (SRAM read access time at 50 MHz, 20 ns cycle) |

---

### M09 — interrupt_ctrl

- **Source:** CREATE
- **Complexity:** Low

**Purpose:** Aggregate 13 peripheral IRQ sources into a single CPU interrupt line with
per-source enable and pending status registers.

**Interface:**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| paddr | Input | 8 | APB register address |
| pwdata | Input | 32 | APB write data |
| prdata | Output | 32 | APB read data |
| pwrite | Input | 1 | APB write enable |
| psel | Input | 1 | APB select |
| penable | Input | 1 | APB enable |
| pready | Output | 1 | APB ready |
| irq_in[12:0] | Input | 13 | Peripheral IRQ inputs |
| cpu_irq_o | Output | 1 | CPU interrupt (to Ibex irq_external_i) |

**Register Map:**

| Offset | Register | Width | Access | Reset | Description |
|--------|----------|-------|--------|-------|-------------|
| 0x00 | IRQ_EN | 16 | R/W | 0x0000 | Per-source enable: bit[N]=1 enables source N |
| 0x04 | IRQ_PENDING | 16 | R | 0x0000 | Per-source pending: bit[N]=1 if IRQ_EN[N] AND irq_in[N] |
| 0x08 | CPU_IRQ | 1 | R | 0 | Global IRQ: OR of all bits in IRQ_PENDING |

**Functional Description:**
IRQ_PENDING = IRQ_EN & irq_in (bitwise AND). CPU_IRQ = |IRQ_PENDING (reduction OR).
All combinational — no pipeline delay for IRQ assertion. irq_in values are raw level
signals from peripherals; per §3.3, all are synchronous to clk_sys. CPU IRQ deasserts
when the firmware clears the peripheral condition (or disables the source via IRQ_EN).

**Edge Cases:**
- W1C: No W1C registers. IRQ clearing is done at the peripheral (e.g., GPIO W1C,
  UART FIFO drain). The interrupt controller itself does not latch or clear IRQs — it
  is a pure combinational aggregator.
- Read-clear: No read-clear behavior. IRQ_PENDING is a read-only mirror of
  (IRQ_EN & irq_in).
- Reset values: IRQ_EN=0x0000 (all IRQs disabled). IRQ_PENDING=0x0000. CPU_IRQ=0.
- Default outputs: cpu_irq_o=0 when all IRQs disabled.
- Non-obvious: The interrupt controller does NOT latch IRQs. If a peripheral IRQ is a
  pulse shorter than one clock cycle, it may be missed. All peripheral IRQs are designed
  as level signals that persist until explicitly cleared at the source.

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~1 kGE |
| Expected FFs | ~16 (IRQ_EN register only) |
| Critical path | ~2 ns (13-input OR reduction) |

---

### M10 — wb_bridge

- **Source:** CREATE
- **Complexity:** High (CDC crossing)

**Purpose:** APB↔Wishbone B4 pipelined bridge enabling the Caravel management SoC to
access internal Argus peripherals and SRAM via the Wishbone window (0x8000_0000).
Includes CDC async FIFOs between clk_wb and clk_sys domains.

**Interface (Wishbone side — Caravel, clk_wb):**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| wb_clk_i | Input | 1 | Wishbone clock (Caravel mgmt SoC, 10–25 MHz) |
| wb_rst_i | Input | 1 | Wishbone reset |
| wb_adr_i | Input | 32 | Wishbone address |
| wb_dat_i | Input | 32 | Wishbone write data |
| wb_dat_o | Output | 32 | Wishbone read data |
| wb_sel_i | Input | 4 | Byte select |
| wb_we_i | Input | 1 | Write enable |
| wb_stb_i | Input | 1 | Strobe |
| wb_cyc_i | Input | 1 | Bus cycle |
| wb_ack_o | Output | 1 | Acknowledge |
| wb_err_o | Output | 1 | Error |

**Interface (APB side — internal, clk_sys):**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| apb_paddr | Output | 32 | APB address (derived from wb_adr_i) |
| apb_pwdata | Output | 32 | APB write data |
| apb_prdata | Input | 32 | APB read data |
| apb_pwrite | Output | 1 | APB write enable |
| apb_psel | Output | 1 | APB select (to interconnect slave port) |
| apb_penable | Output | 1 | APB enable |
| apb_pready | Input | 1 | APB ready |
| apb_pslverr | Input | 1 | APB error |

**Functional Description:**
The bridge maps Caravel Wishbone transactions to internal APB transactions. WB→APB path:
WB command captured, crossed into clk_sys via async FIFO, translated to APB read/write,
response crossed back to clk_wb via a second async FIFO. Address translation: Wishbone
address must be within 0x8000_0000 window; internal APB address = wb_adr_i & 0x7FFFFFFF.
(For SRAM at 0x0000_0000, Caravel uses 0x8000_0000.)

**CDC Details:**

| Path | Method | Depth |
|------|--------|-------|
| clk_wb → clk_sys (command) | Async FIFO, 32-bit × 8 deep | 8 |
| clk_sys → clk_wb (read response) | Async FIFO, 32-bit × 4 deep | 4 |
| Single-bit control (ack/err) | 2-FF synchronizer | 2 |

**Edge Cases:**
- Reset values: All FIFOs empty. wb_ack_o=0, wb_err_o=0. apb_psel=0, apb_penable=0.
- Default outputs: wb_dat_o=0x0000_0000 when no read data available. apb_paddr=0x0000_0000
  when idle.
- Non-obvious: The bridge handles Wishbone-to-APB address remapping. The Caravel mgmt SoC
  sees the entire 2 GB window; internal addresses are the lower 31 bits (0x0000_0000–0x7FFF_FFFF).
  APB read latency from WB side: ~2 clk_wb cycles (FIFO write) + ~2 clk_sys cycles (APB access)
  + ~2 clk_wb cycles (FIFO read) ≈ 6–8 clk_wb cycles total. Backpressure: if the command FIFO
  fills, wb_ack_o is withheld (stall Wishbone master).

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~5 kGE |
| Expected FFs | ~350 (2× FIFO 8+4 deep × 40 bits + control) |
| Critical path | ~6 ns (FIFO read pointer to mux) |

---

### M11 — caravel_wrapper

- **Source:** CREATE
- **Complexity:** Integration

**Purpose:** Top-level wrapper instantiating all Argus modules and connecting them to
the Caravel harness. Manages clock input (user_clock2), reset input (user_reset_n),
IO pad connections, and logic analyzer probe routing.

**Interface (Caravel harness side):**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| user_clock2 | Input | 1 | 50 MHz clock from Caravel PLL |
| user_reset_n | Input | 1 | Active-low async reset from Caravel |
| io_in[37:0] | Input | 38 | Input from Caravel IO pads (unused pins tied low) |
| io_out[37:0] | Output | 38 | Output to Caravel IO pads |
| io_oeb[37:0] | Output | 38 | Output enable bar (0=drive, 1=high-Z) |
| la_data_in[127:0] | Input | 128 | Logic analyzer input (unused) |
| la_data_out[127:0] | Output | 128 | Logic analyzer output (debug probes) |
| la_oen[127:0] | Input | 128 | Logic analyzer output enable |
| wb_clk_i | Input | 1 | Wishbone clock from Caravel mgmt SoC |
| wb_rst_i | Input | 1 | Wishbone reset |
| wb_adr_i | Input | 32 | Wishbone address |
| wb_dat_i | Input | 32 | Wishbone write data |
| wb_dat_o | Output | 32 | Wishbone read data |
| wb_sel_i | Input | 4 | Wishbone byte select |
| wb_we_i | Input | 1 | Wishbone write enable |
| wb_stb_i | Input | 1 | Wishbone strobe |
| wb_cyc_i | Input | 1 | Wishbone cycle |
| wb_ack_o | Output | 1 | Wishbone acknowledge |
| wb_err_o | Output | 1 | Wishbone error |

**IO Pad Assignment:**

| Caravel io[N] | Signal | Direction | Description |
|---------------|--------|-----------|-------------|
| io[0] | uart_tx | Output | UART transmit |
| io[1] | uart_rx | Input | UART receive |
| io[2] | sck | Output | SPI clock |
| io[3] | mosi | Output | SPI MOSI |
| io[4] | miso | Input | SPI MISO |
| io[5] | cs_n[0] | Output | SPI chip select |
| io[6] | scl | Bidir | I2C clock (open-drain, ext pull-up) |
| io[7] | sda | Bidir | I2C data (open-drain, ext pull-up) |
| io[15:8] | gpio[7:0] | Bidir | GPIO pins |
| io[17:16] | pwm[1:0] | Output | PWM outputs |
| io[37:18] | — | — | Reserved (20 pins unconnected, tied to input=0, oeb=1) |

**Functional Description:**
The wrapper instantiates all 12 modules (M01–M12). user_clock2 is buffered and distributed
as clk_sys to all internal modules. user_reset_n is the primary reset; synchronized
deassert to clk_sys posedge. wb_* signals are passed directly to wb_bridge (M10).

**Edge Cases:**
- Reset values: All internal module states per their individual reset values. IO pads
  default to high-impedance (io_oeb=1) until configured.
- Default outputs: io_out=0, io_oeb=1 (all pads high-Z after reset until firmware configures).
- Non-obvious: The wrapper performs NO logic function beyond buffering and routing. The
  Caravel precheck tool verifies no combinational loops, no floating nets, and correct
  pad instantiation per SYS-CR-010.

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~5 kGE (wrapper + padframe routing overhead) |
| Expected FFs | ~50 (reset synchronizer + IO control registers) |
| Critical path | ~3 ns (clock buffer tree insertion delay) |

---

### M12 — sys_ctrl

- **Source:** CREATE
- **Complexity:** Low

**Purpose:** System control module providing chip identification, clock divider for
peripheral baud rate generation, reset cause tracking, and sleep/wake control with
per-module clock gating.

**Interface:**

| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| paddr | Input | 8 | APB register address |
| pwdata | Input | 32 | APB write data |
| prdata | Output | 32 | APB read data |
| pwrite | Input | 1 | APB write enable |
| psel | Input | 1 | APB select |
| penable | Input | 1 | APB enable |
| pready | Output | 1 | APB ready |
| clk_sys | Input | 1 | System clock |
| rst_n | Input | 1 | System reset |
| wdt_rst_n | Input | 1 | Watchdog reset (from M07) |
| ext_rst_n | Input | 1 | External reset (user_reset_n) |
| core_sleep_i | Input | 1 | Core WFI status (from Ibex) |
| clk_gate_en[11:0] | Output | 12 | Per-module clock gate enable |
| wake_event_i | Input | 2 | GPIO edge (0) and PWM match (1) wake events |

**Register Map:**

| Offset | Register | Width | Access | Reset | Description |
|--------|----------|-------|--------|-------|-------------|
| 0x00 | CHIP_ID | 32 | R | 0x41524755 | Chip identifier ("ARGU" in ASCII) |
| 0x04 | CLK_DIV | 8 | R/W | 0x01 | System clock divider for peripheral baud gen |
| 0x08 | RESET_CAUSE | 8 | R | — | [2:0]: 0=POR, 1=external, 2=watchdog, 3=software |
| 0x0C | SLEEP_CTRL | 8 | R/W | 0x00 | [7:4] wake source, [0] sleep enable |

**Functional Description:**
- CHIP_ID: hardcoded 32-bit identifier (0x41524755 = "ARGU"). Read-only.
- CLK_DIV: divided clock enable for UART/SPI/I2C baud generators. Default = 1 (no division).
- RESET_CAUSE: latches cause of most recent reset. Cleared to 0 (POR) on power-on reset.
  Set to 1 on external reset assertion, 2 if wdt_rst_n asserted, 3 on software reset.
- SLEEP_CTRL: bit 0 = sleep mode. When set AND core_sleep_i=1: clock gate all peripherals
  except GPIO and PWM (wake sources). SRAM retained. Wake on GPIO edge or PWM match restores
  clocks. Wake source captured in bits [7:4].

**Edge Cases:**
- W1C: No W1C registers. RESET_CAUSE is updated by hardware on reset, read-only afterward.
- Read-clear: No read-clear behavior.
- Reset values: CHIP_ID=0x41524755 (constant), CLK_DIV=0x01, RESET_CAUSE=0x00 (POR),
  SLEEP_CTRL=0x00.
- Default outputs: clk_gate_en=0xFFF (all modules clocked after reset).
- Non-obvious: CLK_DIV is a global divider affecting all three communication peripherals
  (UART, SPI, I2C). Individual peripheral prescalers are in addition to this global divider.
  Sleep wake latency: ~4 clk_sys cycles from wake event to first instruction fetch
  (clock restoration + core wake).

**Area/Timing Budget:**

| Metric | Value |
|--------|-------|
| Expected cells | ~2 kGE |
| Expected FFs | ~50 (CLK_DIV + RESET_CAUSE + SLEEP_CTRL + reset cause latch) |
| Critical path | ~3 ns (clock gate enable distribution) |

---

## 5. Reset & Clock Strategy

### 5.1 Reset Architecture

| Signal | Type | Assert | Deassert | Min Width | Source |
|--------|------|--------|----------|-----------|--------|
| rst_n (sys) | Async assert, sync deassert | user_reset_n from Caravel (active low) | Synchronized to clk_sys posedge | 4 clk_sys cycles | Caravel harness |
| rst_n (wb) | Async assert, sync deassert | wb_rst_i from Caravel (active low) | Synchronized to clk_wb posedge | 4 clk_wb cycles | Caravel harness |
| wdt_rst_n | Sync assert, sync deassert | Watchdog timeout (internal) | Extended 16 clk_sys cycles | 16 clk_sys cycles | PWM/WDT (M07) |

**Reset type:** Asynchronous assert (immediate), synchronous deassert (on posedge clk_sys).
**Reset polarity:** Active low (`rst_ni`).
**Reset vector:** 0x0000_0000 (SRAM base).
**Register init:** All registers at reset values specified per-module in §4.
**Boot sequence:**
1. Caravel power-on reset (POR). rst_n and wb_rst_n asserted.
2. Caravel management SoC loads firmware into SRAM via Wishbone bridge (0x8000_0000 → 0x0000_0000).
3. Caravel deasserts user_reset_n. Internal rst_n synchronously deasserted.
4. Ibex fetches first instruction from SRAM at 0x0000_0000.
5. Firmware initializes peripherals, enables interrupts, enters main loop.

### 5.2 Clock Architecture

| Domain | Source | Frequency | Consumers | Notes |
|--------|--------|-----------|-----------|-------|
| clk_sys | Caravel user_clock2 | 50 MHz target / 25 MHz fallback | All internal modules: Ibex, APB, peripherals, SRAM, interrupt_ctrl, sys_ctrl | Single domain. Clock gated per-module via sys_ctrl. |
| clk_wb | Caravel wb_clk_i | 10–25 MHz | wb_bridge (Wishbone side only) | Async to clk_sys. CDC at bridge boundary. |

**Clock gating (per SYS-FR-013, SHOULD):**
Each peripheral module (M03–M07, M09) has a clock gate cell controlled by
`sys_ctrl.clk_gate_en[N]`. When a peripheral is idle (firmware disables it via CONTROL
register), firmware can write to SLEEP_CTRL to gate its clock. GPIO and PWM timers
are never gated when wake-enabled.

### 5.3 CDC Strategy

| From Domain | To Domain | Method | Verification |
|-------------|-----------|--------|-------------|
| clk_wb → clk_sys | WB → APB bridge command | Async FIFO (32-bit × 8 deep), 2-FF sync for control | Formal CDC (Yosys-SMTBMC), GLS |
| clk_sys → clk_wb | APB → WB bridge response | Async FIFO (32-bit × 4 deep), 2-FF sync for ack/err | Formal CDC, GLS |
| Peripheral IRQ → CPU | N/A | All IRQs synchronous to clk_sys. No CDC needed. | N/A — single domain |

---

## 6. Coding Constraints

### 6.1 Language
- **SystemVerilog** (IEEE 1800-2017 synthesizable subset) per SYS-CR-001
- Yosys-compatible SV constructs only: `always_ff`, `always_comb`, `logic`, `enum`, `struct`,
  `typedef`, interfaces (for APB/Wishbone bus bundles)
- No dynamic types, no classes, no program blocks, no assertions in synthesizable code

### 6.2 Naming Conventions
- Inputs: `signal_name_i`
- Outputs: `signal_name_o`
- Bidirectional: `signal_name_io`
- Internal: `signal_name` (no suffix)
- Clock: `clk_i` or `clk_sys_i` / `clk_wb_i`
- Reset: `rst_ni` (active-low async)
- Active-low signals: `_n` suffix (e.g., `cs_n`, `rst_n`)
- APB bus: `paddr`, `pwdata`, `prdata`, `pwrite`, `psel`, `penable`, `pready`, `pslverr`
- Constants: UPPER_CASE (e.g., `UART_BASE`, `SRAM_SIZE`)

### 6.3 Forbidden Patterns
- No `initial` in synthesizable code
- No latches: every `always_comb` covers all branches; every `if` has `else`; every `case`
  has `default`
- No partial bit-slice assignments on LHS of `assign` or `always_comb`
- No blocking assignments (`=`) in `always_ff` blocks
- No non-blocking assignments (`<=`) in `always_comb` blocks
- No implicit wires: all signals explicitly declared with `logic`
- No `#delay` in synthesizable code

### 6.4 Required Patterns
- Async reset: `always_ff @(posedge clk_i or negedge rst_ni)`
- Registered outputs on all module boundaries (1-cycle latency unless combinational)
- `default` in every `case` statement inside `always_comb`

### 6.5 Module Boundaries
- Each module has exactly one clock domain (clk_sys or clk_wb)
- M10 (wb_bridge) is the only module spanning two domains — it uses async FIFOs, not
  direct clock-domain crossings
- Module outputs are registered (1-cycle latency) unless annotated as combinational
  in the interface table
- Bus interfaces use APB v2.0 (internal) or Wishbone B4 pipelined (Caravel boundary)

### 6.6 REUSE IP Integrity (SYS-CR-003)
- All REUSE IP (M01, M03, M04, M05, M06, M07 base, M08) used without source modification
- REUSE* adaptation (M07 PWM/WDT wrapper) confined to pwm_wrapper.v
- Upstream commit hashes recorded in `reuse_manifest.json`

---

## 7. CSR Summary (RISC-V Standard)

Ibex CSRs are standard RISC-V Machine-mode (M-mode only per Easy tier):

| CSR | Address | Access | Reset Value | Description |
|-----|---------|--------|-------------|-------------|
| mstatus | 0x300 | RW | 0x0000_0000 | Machine status (MIE, MPIE) |
| misa | 0x301 | RO | 0x4000_0100 | ISA and extensions (RV32I) |
| mie | 0x304 | RW | 0x0000_0000 | Machine interrupt enable (MEIE only) |
| mtvec | 0x305 | RW | 0x0000_0000 | Machine trap-handler base address |
| mscratch | 0x340 | RW | 0x0000_0000 | Machine scratch register |
| mepc | 0x341 | RW | 0x0000_0000 | Machine exception program counter |
| mcause | 0x342 | RW | 0x0000_0000 | Machine trap cause |
| mtval | 0x343 | RW | 0x0000_0000 | Machine bad address or instruction |
| mip | 0x344 | RW | 0x0000_0000 | Machine interrupt pending (MEIP from M09) |
| mhartid | 0xF14 | RO | 0x0000_0000 | Hardware thread ID |

Note: Peripherals use memory-mapped registers (§4), not CSRs. The RISC-V `mie.MEIE` bit
must be set for the external interrupt from M09 to reach the Ibex core.

---

## 8. ORFS Compatibility Review

### 8.1 Reference Comparison

| Feature | PRJ-001 Argus | stock riscv32i | stock ibex | Notes |
|---------|---------------|----------------|------------|-------|
| Core | Ibex RV32I, 2-stage | Custom RV32I, single-cycle | Ibex "maxperf" | Identical core config to stock ibex |
| Memory | 4 KB SRAM (OpenRAM) | N/A | N/A | OpenRAM macro, ORFS-compatible |
| Bus | APB v2.0 internal | N/A | N/A | Simple single-cycle protocol |
| Bus wrapper | APB↔Wishbone bridge at Caravel boundary | N/A | N/A | No APB synthesized into core |
| Boot | Caravel loads SRAM via WB; Ibex boots from SRAM | N/A | N/A | No hardcoded boot ROM |
| Byte-enable | SRAM controller provides byte-enable for APB | N/A | N/A | Controller, not core |

### 8.2 ORFS Compatibility Checklist

1. **Bus interfaces are external wrappers:** ✅ The APB interconnect (M02) is a separate
   module at SoC level. Ibex exports simple memory ports (instr_req, data_req). The
   APB↔Wishbone bridge (M10) is at the Caravel boundary. No APB/AXI/AHB inside the core.

2. **Memory interfaces are ORFS-friendly:** ✅ No hardcoded boot ROM. No `$readmemh` needed
   — Caravel loads SRAM via Wishbone. Word-aligned data memory with ARB controller for
   Ibex instruction/data/APB ports. Byte-enable in SRAM controller, not core.

3. **Cell count sanity check:** Ibex RV32I "maxperf" at 50 MHz sky130A ≈ 15 kGE.
   Total chip estimate ≈ 83 kGE. Stock ibex is ~15 kGE. Our additional 68 kGE comes from
   peripherals + SRAM + bridge. Comparable to other Caravel projects (IP-005: 16-module SoC
   ≈ 70 kGE). No red flags.

4. **Reference examples:**
   - `/opt/OpenROAD/OpenROAD-flow-scripts/flow/designs/sky130hd/ibex/` — stock ibex
   - Project builds on proven Caravel harness with standard EF_ peripherals.

### 8.3 Deviations from Reference (with Justification)

| Deviation | Justification |
|-----------|---------------|
| Ibex RV32I (no M) vs stock ibex RV32IM | M extension adds ~15% area; sensor-polling math doesn't need hardware multiply. Spec §1.2. |
| Custom 13-source interrupt controller vs PLIC | PLIC is overkill for 13 sources. Per spec §8 + Vera directive. 1 kGE vs ~5 kGE for PLIC. |
| EF_TMR32 repurpose for PWM+WDT vs dedicated PWM IP | Reduces IP count; TMR32 compare-match naturally produces PWM. WDT reuses overflow. REUSE* justified in module_list.md. |

---

## 9. Assumptions & Open Items

### 9.1 Simplifications (Easy Tier)
- M-mode only (no U/S mode)
- No debug module (no JTAG, no DMI)
- No branch predictor (Ibex static not-taken)
- No instruction/data cache
- No performance counters
- No DMA
- No hardware flow control (RTS/CTS)
- No I2C slave mode, no SPI slave mode
- Single-master I2C bus (arbitration loss detection included for safety)
- Firmware loaded by Caravel mgmt SoC (no boot ROM)

### 9.2 Open Items
- `reuse_manifest.json` — upstream commit hashes TBD (recorded when IP is cloned)
- SRAM macro exact dimensions from OpenRAM (varies by configuration; 4 KB macro aspect
  ratio validated at floorplanning stage)
- GPIO IO pad drive strength selection (4/8/12 mA, TBD at padframe stage)

### 9.3 Known Limitations
- Single-issue, in-order execution only
- No memory protection (PMP disabled)
- No atomic operations (no A extension)
- Sleep wake latency ~4 cycles (acceptable for SHOULD priority)
- All peripheral IRQs are level-sensitive; pulse IRQs may be missed

### 9.4 Items Deferred to Future Iterations
Per spec §1.2 out-of-scope list: M extension, SPI slave, UART RTS/CTS, DMA, I2C slave,
baud auto-detection, on-die temp sensor, CRC accelerator, analog front-end, wireless,
flash, hardware security, MMU.

---

## 10. Traceability

| Architecture Section | Spec Reference | Module |
|---------------------|----------------|--------|
| §1 Key Specs | SYS-FR-001, SYS-PR-001 | M01 |
| §2 Memory Map | §8 Memory Map, SYS-FR-007 | M08, M02 |
| §3.1 Ibex Core | §2.3, SYS-FR-001 | M01 |
| §3.2 APB Bus | §8, SYS-FR-008, SYS-CR-004 | M02 |
| §3.3 Interrupt Routing | §8, SYS-FR-011, SYS-AR-005 | M09 |
| §4 M03 UART | §8 UART Registers, SYS-FR-002 | M03 |
| §4 M04 SPI | §8 SPI Registers, SYS-FR-003 | M04 |
| §4 M05 I2C | §8 I2C Registers, SYS-FR-004 | M05 |
| §4 M06 GPIO | §8 GPIO Registers, SYS-FR-005 | M06 |
| §4 M07 PWM/WDT | §8 PWM+WDT Registers, SYS-FR-006, SYS-FR-012 | M07 |
| §4 M08 SRAM | §8, SYS-FR-007, SYS-PR-011 | M08 |
| §4 M10 WB Bridge | §8, SYS-FR-009, SYS-CR-005, SYS-CR-006 | M10 |
| §4 M11 Caravel | SYS-FR-010, SYS-CR-009, SYS-CR-010 | M11 |
| §4 M12 Sys Ctrl | §8, SYS-FR-013, SYS-FR-014 | M12 |
| §5 Reset/Clock | §9, SYS-CR-007, SYS-CR-011 | M11, M12 |
| §5.3 CDC | §9.3, SYS-CR-006 | M10 |
| §6 Coding | SYS-CR-001, SYS-CR-003 | ALL |
| §8 ORFS | IP-004 post-mortem | ALL |
