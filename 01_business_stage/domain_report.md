# Domain Report — Environmental Sensor-Hub SoC

## Domain Overview

An environmental sensor-hub SoC aggregates data from multiple environmental sensors (temperature, humidity, barometric pressure, gas, light, particulate matter) over standard serial interfaces (I2C, SPI), buffers and optionally processes the data, drives actuators (fans, valves, alerts) via PWM/GPIO, and reports results over UART to a host system or network gateway. These devices form the edge-compute layer of IoT infrastructure for smart buildings, precision agriculture, industrial condition monitoring, and environmental compliance.

The market for sensor hubs is expanding rapidly: STMicroelectronics' $950M acquisition of NXP's sensor business in 2025 underscores the strategic value of integrated sensing platforms [https://www.embedded.com/stmicroelectronics-950m-mems-deal-a-strategic-reset-in-turbulent-times/]. The sensor hub market is projected to grow at double-digit CAGR through 2033, driven by smart building mandates, agricultural IoT, and emissions monitoring regulations [https://www.linkedin.com/pulse/sensor-hub-market-outlook-20242033-trends-innovations-tqxkc].

Open-source silicon is a nascent but rapidly maturing segment. Efabless Caravel-based MPW shuttles on sky130A have produced over 500 designs since 2021, but few target environmental sensing with an integrated, production-quality peripheral set. This creates a unique opportunity: a fully open-source RISC-V sensor-hub ASIC with REUSE-able, verified IP blocks.

## Key Technical Challenges

- **Multi-protocol sensor polling:** I2C (100/400 kHz) and SPI (up to 25 MHz) require concurrent access arbitration. Sensors have varying readout cadences (10 ms for gas, 1 s for temperature/humidity).
- **Low-power duty cycling:** Battery/solar-powered sensor nodes must sleep at sub-µA currents and wake within microseconds to poll sensors. Aggressive clock gating and power-domain management are essential.
- **Data buffering under memory constraints:** 2-4 KB SRAM must hold buffered sensor frames, command queues, and stack space. Efficient ring-buffer management with minimal firmware overhead is critical.
- **Actuator control with deterministic timing:** PWM outputs for fan speed, valve position, or LED indicators must maintain stable duty cycles even under interrupt load from sensor polling.
- **Caravel harness integration:** The APB↔Wishbone bridge at the Caravel boundary requires careful address-mapping and clock-domain crossing (management SoC runs at a different clock).
- **Open-source IP verification:** While STRONG-tier IP blocks exist (Ibex, EF_UART, EF_SPI, EF_I2C, EF_GPIO8, EF_TMR32), no prior project has integrated all six into a single sky130A tapeout with full formal+simulation coverage.

## Relevant Standards/Protocols

| Standard | Application | Reference |
|----------|-------------|-----------|
| I2C (v3.0, NXP) | Sensor communication (100/400 kHz) | NXP UM10204 |
| SPI (Motorola, mode 0/3) | High-speed sensor readout | Motorola M68HC11 ref |
| UART (8N1, 115200 baud) | Host reporting, debug | RS-232/485 |
| PWM (variable duty, 0-100%) | Actuator/fan/LED control | Industry standard |
| APB v2.0 (ARM IHI0024C) | Internal peripheral bus | ARM spec |
| Wishbone B4 (FOSSi) | Caravel harness interconnect | fossi-wishbone-spec (IP-INDEX) |
| RISC-V RV32I ISA v2.1 | Processor ISA | riscv.org |

## Domain-Specific Metrics That Matter

**Primary (gate the design):**
- **Active power at 50 MHz:** Target ≤ 5 mW. Comparable to TI MSP430FR (~120 µA/MHz = ~0.36 mW at 25 MHz, scaled to 130nm ~0.5 mW) and STM32L0 (~88 µA/MHz at 32 MHz = ~0.5 mW at 180nm). Sky130A expects 3-8 mW for Ibex-class designs.
- **Sleep/standby current:** Target ≤ 10 µA (clock-gated, SRAM retained). Critical for battery life.
- **Sensor polling throughput:** ≥ 200 sensor reads/second over I2C at 400 kHz with 2-byte register reads.
- **Wake-up latency:** ≤ 10 µs from sleep to first sensor read. Enables aggressive duty cycling.

**Secondary (desirable):**
- **Data buffer depth:** 2-4 KB ring buffer must hold ≥ 50 sensor frames (each ~32 bytes: timestamp + sensor ID + value).
- **PWM resolution:** 8-10 bits at 1-25 kHz base frequency for smooth actuator control.
- **UART throughput:** 115200 bps reliable full-duplex under sensor polling load.

**Market differentiator:** No fully open-source (Apache-2.0/BSD) RISC-V environmental sensor-hub ASIC exists on sky130A with a complete, verified REUSE IP stack (Ibex + EF_UART + EF_SPI + EF_I2C + EF_GPIO8 + EF_TMR32 + OpenRAM). This project fills that gap with auditable quality gates.
