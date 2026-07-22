# Competitive Landscape — Environmental Sensor-Hub SoC

## Comparables

### 1. OpenTitan EarlGrey (lowRISC)
- **Type:** Open-source security SoC, RISC-V (Ibex RV32IMC)
- **Process:** sky130A (SkyWater 130nm)
- **Frequency:** 100 MHz target
- **Area:** Core ~1.0 mm² (Ibex + 128KB SRAM + peripherals)
- **Power:** ~10-20 mW active (estimated from 100MHz sky130A ST cell library)
- **Peripherals:** UART, SPI, I2C, GPIO, HMAC, AES, OTBN, key manager, alert handler, power manager — predominantly security-focused
- **Memory:** 128KB SRAM, 64KB ROM
- **License:** Apache-2.0
- **Year:** 2021+ (ongoing)
- **Source:** https://opentitan.org/book/hw/top_earlgrey/doc/specification.html
- **SI/DFT:** SI=3 (production-grade), DFT=Y (scan chains)

**Relevance:** Same core (Ibex), same process (sky130A), same bus paradigm. Proves Ibex + sky130A at 100 MHz is achievable. Too large and security-focused for our use case — EarlGrey is ~80 kGE vs our target ~60-85 kGE, but ~80% of EarlGrey's area goes to security IP we don't need.

---

### 2. NEORV32 (stnolting)
- **Type:** Open-source RISC-V microcontroller SoC
- **Process:** FPGA-primary (portable to ASIC), typically Intel Cyclone IV / Xilinx Artix-7
- **Frequency:** 50-100 MHz (FPGA); ASIC estimate 100-200 MHz in 130nm
- **Area:** ~10 kGE (CPU core only); full SoC ~20-25 kGE (estimated from VHDL synthesis reports)
- **Peripherals:** UART, SPI, GPIO, PWM (WDT as timer), external bus interface. **No native I2C in base config.**
- **Memory:** Internal DMEM + IMEM (configurable, typically 8-64 KB via block RAM)
- **License:** BSD-3-Clause
- **Year:** 2020+ (actively maintained)
- **Source:** https://github.com/stnolting/neorv32, https://stnolting.github.io/neorv32/
- **IP-INDEX:** stnolting-neorv32 (STRONG, 50 MHz ref, 10 kGE)

**Relevance:** Closest open-source feature match — RV32I, UART, SPI, GPIO, timer/PWM. Missing I2C and OpenRAM integration. FPGA-first means no silicon PPA data exists. A tapeout of NEORV32 on sky130A would be the closest comparable, but none exists yet. Our project achieves feature parity + I2C + silicon validation.

---

### 3. TI MSP430FR2355 (Texas Instruments)
- **Type:** Commercial ultra-low-power 16-bit MCU with sensor AFE
- **Process:** 130nm FRAM process (estimated)
- **Frequency:** 24 MHz max
- **Area:** Die ~1.5-3.0 mm² estimated (package 4×4 mm QFN)
- **Power:** ~120 µA/MHz active (= 2.9 mW at 24 MHz); 0.5 µA standby with RAM retention
- **Peripherals:** I2C (2×), SPI (2×), UART (2×), 12-bit ADC (12-ch), 4× smart analog combos (op-amp + PGA + DAC), 6× timer/PWM
- **Memory:** 32KB FRAM, 4KB SRAM
- **Price:** ~$1.50-2.50 @ 1k units
- **Year:** 2019+
- **Source:** https://www.ti.com/product/MSP430FR2355 (TI datasheet for FR2355 family)
- **Process scaling note:** TI 130nm FRAM is a different process — area/power scaling to sky130A is approximate (±30%).

**Relevance:** Gold standard for low-power sensor nodes. Our power target (~5 mW active) is comparable to TI's 2.9 mW active, but we add RISC-V openness + full Caravel integration. TI's analog integration (ADC, op-amp) is superior — we do NOT compete on analog. Our differentiator is open-source programmability.

---

### 4. STM32L011D4 (STMicroelectronics)
- **Type:** Commercial ultra-low-power ARM Cortex-M0+ MCU
- **Process:** 110nm ULP (ST FCMOS)
- **Frequency:** 32 MHz max
- **Area:** Die ~1.0-2.0 mm² estimated (TSSOP-14 package, 3×3 mm)
- **Power:** 88 µA/MHz run mode (= 0.28 mW at 32 MHz, 1.8V); 0.5 µA stop with RTC
- **Peripherals:** I2C (1×), SPI (1×), USART (1×), 12-bit ADC (5-ch), 2× timer/PWM, RTC
- **Memory:** 16KB Flash, 2KB SRAM
- **Price:** ~$0.80-1.20 @ 1k units
- **Year:** 2014+ (mature product line)
- **Source:** https://www.st.com/en/microcontrollers-microprocessors/stm32l011d4.html

**Relevance:** Closest commercial feature match (UART, SPI, I2C, GPIO, timer/PWM, 2KB SRAM). ST's process advantage (110nm ULP) gives them a 10× power advantage. Our sky130A design is competitive on openness, not on power. At 3.3V sky130A, our power will be higher; at 1.8V we approach comparability.

---

### 5. Silicon Labs EFM8BB10F8G (Silicon Labs)
- **Type:** Commercial 8-bit MCU (CIP-51, 8051-compatible)
- **Process:** 180nm (estimated)
- **Frequency:** 25 MHz max
- **Area:** Die ~0.7-1.5 mm² estimated (QFN-20, 3×3 mm)
- **Power:** 150 µA/MHz (= 3.75 mW at 25 MHz); 0.05 µA sleep
- **Peripherals:** I2C (1×, SMBus), SPI (1×), UART (1×), 12-bit ADC (12-ch), 6× PWM, programmable counter array
- **Memory:** 8KB Flash, 512B SRAM
- **Price:** ~$0.50-0.80 @ 1k units
- **Year:** 2015+
- **Source:** https://www.silabs.com/mcu/8-bit/efm8-busy-bee
- **Process scaling:** 180nm→130nm: ~1.5× density, ~0.7× power at same frequency.

**Relevance:** Minimum viable sensor hub. 8-bit limits programmability; 512B SRAM limits buffering. Scaled to sky130A: ~0.5 mm², ~2.6 mW at 25 MHz. Our design adds 32-bit RISC-V and 4-8× SRAM at comparable area.

---

## Gap Analysis

| Gap | Description | Our Position |
|-----|-------------|-------------|
| **Open-source RISC-V sensor hub ASIC** | No fully open-source RV32I SoC on sky130A has taped out with a complete UART+SPI+I2C+GPIO+PWM+SRAM peripheral set. NEORV32 is FPGA-only; OpenTitan is security-focused; Caravel user projects are mostly single-function. | **We fill this gap.** First open-source sensor-hub ASIC with full REUSE IP stack. |
| **Verified multi-protocol REUSE IP integration** | Efabless EF_ IP blocks (UART, SPI, I2C, GPIO8, TMR32) exist as STRONG-tier IP, but no project has integrated all five + Ibex + OpenRAM into a single tapeout with full formal+simulation coverage. | **We prove this integration.** Each block is individually STRONG; our value is the audited integration. |
| **Silicon-validated Ibex + OpenRAM on Caravel** | Ibex has been taped out in OpenTitan but not as a user-project on Caravel shuttle. OpenRAM has limited sky130A tapeout history. | **We create a reference integration.** Future open-source sensor projects can fork our design. |
| **Low-power duty cycling with open-source RISC-V** | Commercial MCUs (MSP430, STM32L0) achieve µA-level sleep. Open-source RISC-V SoCs on sky130A have no published sleep-current measurements. | **We establish a benchmark.** Even 10-50 µA sleep in sky130A is a published data point that enables battery/solar sensor nodes. |

## Positioning

Argus positions as the **open-source reference design for RISC-V environmental sensing on silicon**. It does not compete with MSP430/STM32L0 on cost or power — those are mature commercial products on optimized processes. Instead, Argus provides:

1. **A silicon-proven baseline** for the open-source community to iterate on
2. **An audited IP integration template** showing how to combine STRONG-tier IP into a working SoC
3. **A Caravel user-project reference** for Efabless MPW workflows

The primary audience is academic research groups, open-source hardware startups, and hobbyist tapeout participants who need a known-good sensor-hub template they can modify and extend.
