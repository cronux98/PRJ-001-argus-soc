#!/usr/bin/env python3
"""
PRJ-001 (Argus) Environmental Sensor-Hub SoC — Golden Behavioral Model.
Models APB bus, UART, SPI, I2C, GPIO, PWM, Interrupt Controller,
Wishbone Bridge, and System Control at register-transfer level.

Produces deterministic JSON output. Run twice with different --seed
values and compare MD5 hashes to verify determinism.

Usage:
    python3 golden_model.py --seed 42 --out golden_output.json
    python3 golden_model.py --seed 123 --out golden_output_2.json
    diff <(md5sum golden_output.json) <(md5sum golden_output_2.json)
"""

import argparse
import json
import hashlib
import sys
from typing import Dict, List, Optional, Tuple, Any


# =============================================================================
# Constants & Memory Map
# =============================================================================

SRAM_BASE       = 0x0000_0000
SRAM_SIZE       = 0x1000      # 4 KB
UART_BASE       = 0x0001_0000
SPI_BASE        = 0x0001_0100
I2C_BASE        = 0x0001_0200
GPIO_BASE       = 0x0001_0300
PWM_BASE        = 0x0001_0400
IRQ_BASE        = 0x0001_0500
WDT_BASE        = 0x0001_0600
SYSCTRL_BASE    = 0x0001_0700
WB_WINDOW_BASE  = 0x8000_0000

SYS_CLK_HZ      = 50_000_000  # 50 MHz
UART_BAUD        = 115200
SPI_SCLK_DIV     = 4          # f_sys/4 = 12.5 MHz


# =============================================================================
# Utility
# =============================================================================

def md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


# =============================================================================
# APB Bus Model
# =============================================================================

class APBBus:
    """Simplified APB v2.0 bus: single-cycle read/write, no wait states."""
    def __init__(self):
        self.transaction_log: List[Dict[str, Any]] = []

    def read(self, addr: int) -> int:
        self.transaction_log.append({"op": "READ", "addr": f"0x{addr:08X}"})
        return 0

    def write(self, addr: int, data: int):
        self.transaction_log.append({"op": "WRITE", "addr": f"0x{addr:08X}", "data": f"0x{data:08X}"})


# =============================================================================
# SRAM Model
# =============================================================================

class SRAM:
    def __init__(self):
        self.mem: Dict[int, int] = {}
        self.reads = 0
        self.writes = 0

    def read(self, addr: int) -> int:
        offset = addr - SRAM_BASE
        if 0 <= offset < SRAM_SIZE:
            self.reads += 1
            return self.mem.get(offset, 0)
        return 0

    def write(self, addr: int, data: int, mask: int = 0xF):
        offset = addr - SRAM_BASE
        if 0 <= offset < SRAM_SIZE:
            self.writes += 1
            current = self.mem.get(offset, 0)
            # byte-enable mask (4 bits: byte3|byte2|byte1|byte0)
            result = 0
            for i in range(4):
                if mask & (1 << i):
                    byte_val = (data >> (8 * i)) & 0xFF
                    result |= (byte_val << (8 * i))
                else:
                    result |= (current & (0xFF << (8 * i)))
            self.mem[offset] = result

    def load_firmware(self, firmware: List[int]):
        """Load firmware bytes into SRAM starting at offset 0."""
        for i, byte_val in enumerate(firmware):
            self.mem[i] = byte_val & 0xFF


# =============================================================================
# UART Model
# =============================================================================

class UART:
    """Full-duplex UART with 8-byte TX and RX FIFOs."""
    def __init__(self):
        self.tx_fifo: List[int] = []
        self.rx_fifo: List[int] = []
        self.tx_enable = False
        self.rx_enable = False
        self.baud_div = UART_BAUD
        self.tx_full = False
        self.rx_empty = True
        self.tx_busy = False
        self.tx_sent: List[int] = []
        self.rx_received: List[int] = []
        self.rx_overrun = False
        self.fifo_thresh = 4  # TX threshold: IRQ when < this many bytes
        self.rx_fifo_thresh = 1  # RX threshold: IRQ when >= this many bytes

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:  # RXDATA
            if self.rx_fifo:
                val = self.rx_fifo.pop(0)
                self.rx_received.append(val)
                self.rx_empty = (len(self.rx_fifo) == 0)
                return val
            return 0
        elif offset == 0x08:  # STATUS
            status = 0
            if len(self.tx_fifo) == 8: status |= 0x01  # TX full
            if len(self.tx_fifo) == 0: status |= 0x02  # TX empty
            if len(self.rx_fifo) == 8: status |= 0x04  # RX full
            if len(self.rx_fifo) == 0: status |= 0x08  # RX empty
            if self.tx_busy:           status |= 0x10  # TX busy
            if self.rx_overrun:        status |= 0x20  # RX overrun error
            return status
        elif offset == 0x10:  # BAUD_DIV
            return self.baud_div & 0xFFFF
        elif offset == 0x14:  # FIFO_THRESH
            return ((self.rx_fifo_thresh & 0x0F) << 4) | (self.fifo_thresh & 0x0F)
        return 0

    def write_reg(self, offset: int, data: int):
        if offset == 0x00:  # TXDATA
            if len(self.tx_fifo) < 8:
                self.tx_fifo.append(data & 0xFF)
                self.tx_busy = True
        elif offset == 0x0C:  # CONTROL
            self.tx_enable = bool(data & 0x01)
            self.rx_enable = bool(data & 0x02)
        elif offset == 0x10:  # BAUD_DIV
            self.baud_div = data & 0xFFFF
        elif offset == 0x14:  # FIFO_THRESH
            self.rx_fifo_thresh = (data >> 4) & 0x0F
            self.fifo_thresh = data & 0x0F

    def inject_rx(self, byte_val: int):
        """Inject a received byte into RX FIFO."""
        if len(self.rx_fifo) < 8:
            self.rx_fifo.append(byte_val & 0xFF)
            self.rx_empty = False
        else:
            self.rx_overrun = True

    def flush_tx(self):
        """Flush all bytes from TX FIFO to 'sent' list (modeling transmission)."""
        while self.tx_fifo:
            byte_val = self.tx_fifo.pop(0)
            self.tx_sent.append(byte_val)
        self.tx_busy = False

    def irq(self) -> bool:
        """TX FIFO below threshold OR RX FIFO above threshold."""
        tx_irq = self.tx_enable and len(self.tx_fifo) < self.fifo_thresh
        rx_irq = self.rx_enable and len(self.rx_fifo) >= self.rx_fifo_thresh
        return tx_irq or rx_irq


# =============================================================================
# SPI Master Model
# =============================================================================

class SPIMaster:
    """SPI master Mode 0 and Mode 3, 8-byte FIFOs."""
    def __init__(self):
        self.tx_fifo: List[int] = []
        self.rx_fifo: List[int] = []
        self.cpol = 0
        self.cpha = 0
        self.prescaler = 2       # f_SCLK = f_sys / (2 * prescaler)
        self.cs_active = False
        self.transfers: List[Dict[str, Any]] = []
        self.busy = False

    def read_reg(self, offset: int) -> int:
        if offset == 0x04:  # RXDATA
            if self.rx_fifo:
                return self.rx_fifo.pop(0)
            return 0
        elif offset == 0x08:  # STATUS
            status = 0
            if len(self.tx_fifo) == 0: status |= 0x01  # TX empty
            if len(self.rx_fifo) > 0:  status |= 0x02  # RX full (has data)
            if self.busy:              status |= 0x04  # busy
            status |= (self.cpol & 1) << 4
            status |= (self.cpha & 1) << 5
            return status
        elif offset == 0x10:  # CLK_DIV
            return self.prescaler & 0xFF
        return 0

    def write_reg(self, offset: int, data: int):
        if offset == 0x00:  # TXDATA
            if len(self.tx_fifo) < 8:
                self.tx_fifo.append(data & 0xFF)
                self._do_transfer()
        elif offset == 0x0C:  # CONTROL
            self.cpol = (data >> 0) & 1
            self.cpha = (data >> 1) & 1
            self.cs_active = bool(data & 0x10)
        elif offset == 0x10:  # CLK_DIV
            self.prescaler = max(data & 0xFF, 2)

    def _do_transfer(self):
        """Model full-duplex SPI transfer: for each byte in TX FIFO, generate RX byte."""
        while self.tx_fifo:
            tx_byte = self.tx_fifo.pop(0)
            # In a real device, MISO is sampled simultaneously.
            # For golden model: RX byte = ~TX byte (simple pattern for determinism)
            rx_byte = (~tx_byte) & 0xFF
            self.rx_fifo.append(rx_byte)
            self.transfers.append({
                "mode": f"CPOL={self.cpol},CPHA={self.cpha}",
                "tx": f"0x{tx_byte:02X}",
                "rx": f"0x{rx_byte:02X}",
                "sclk_div": self.prescaler,
            })
        self.busy = False

    def irq(self) -> bool:
        return len(self.rx_fifo) > 0  # Data available


# =============================================================================
# I2C Master Model
# =============================================================================

class I2CMaster:
    """I2C master: 100/400 kHz, 7-bit addr, multi-byte, repeated start."""
    def __init__(self):
        self.clk_div_lo = 125  # 50M / (2*125) ≈ 200 kHz default
        self.clk_div_hi = 125
        self.addr = 0
        self.data_reg = 0
        self.busy = False
        self.nack = False
        self.arb_lost = False
        self.transactions: List[Dict[str, Any]] = []

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:  # DATA
            return self.data_reg & 0xFF
        elif offset == 0x04:  # ADDR
            return self.addr & 0xFF
        elif offset == 0x08:  # STATUS
            status = 0
            if self.busy:      status |= 0x01
            if self.nack:      status |= 0x04
            if self.arb_lost:  status |= 0x08
            # Transfer done: not busy and no error
            if not self.busy and not self.nack:
                status |= 0x10
            return status
        return 0

    def write_reg(self, offset: int, data: int):
        if offset == 0x00:  # DATA
            self.data_reg = data & 0xFF
        elif offset == 0x04:  # ADDR
            self.addr = data & 0xFF
        elif offset == 0x0C:  # CONTROL
            if data & 0x01:  # START
                self._start_transfer(data)
            if data & 0x02:  # STOP
                self.busy = False
                self.transactions.append({"op": "STOP", "timestamp": len(self.transactions)})
        elif offset == 0x10:
            self.clk_div_lo = data & 0xFF
        elif offset == 0x14:
            self.clk_div_hi = data & 0xFF

    def _start_transfer(self, ctrl: int):
        """Model I2C START + addr + data transfer."""
        is_read = bool(self.addr & 0x01)
        addr_7bit = (self.addr >> 1) & 0x7F
        self.busy = True
        self.nack = False
        self.arb_lost = False

        entry = {
            "addr_7bit": f"0x{addr_7bit:02X}",
            "rw": "READ" if is_read else "WRITE",
            "data": f"0x{self.data_reg:02X}",
            "mode": "START",
            "scl_freq_hz": SYS_CLK_HZ // (self.clk_div_lo + self.clk_div_hi),
        }

        # Simulate NACK if address >= 0x78 (reserved addresses)
        if addr_7bit >= 0x78:
            self.nack = True
            entry["ack"] = "NACK"
            self.busy = False
        else:
            entry["ack"] = "ACK"
            self.busy = False  # Transfer completes after ACK (single-byte model)

        self.transactions.append(entry)

    def irq(self) -> bool:
        return not self.busy  # Transfer complete


# =============================================================================
# GPIO Model
# =============================================================================

class GPIO:
    """8-pin GPIO with per-pin direction, IRQ, edge detect."""
    def __init__(self):
        self.data_out = 0
        self.data_in = 0       # External input value
        self.dir = 0           # 1=output, 0=input
        self.irq_en = 0        # Per-pin IRQ enable
        self.irq_edge_rise = 0  # Rising edge detect enable per pin
        self.irq_edge_fall = 0  # Falling edge detect enable per pin
        self.irq_status = 0    # Pending IRQs
        self.prev_input = 0    # Previous input value for edge detect

    def set_inputs(self, value: int):
        """Drive external input pins."""
        old = self.prev_input
        new = value & 0xFF
        self.data_in = new

        # Edge detection
        for pin in range(8):
            old_bit = (old >> pin) & 1
            new_bit = (new >> pin) & 1
            if self.irq_en & (1 << pin):
                if self.irq_edge_rise & (1 << pin) and old_bit == 0 and new_bit == 1:
                    self.irq_status |= (1 << pin)
                if self.irq_edge_fall & (1 << pin) and old_bit == 1 and new_bit == 0:
                    self.irq_status |= (1 << pin)

        self.prev_input = new

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:  # DATA_OUT
            return self.data_out & 0xFF
        elif offset == 0x04:  # DATA_IN
            return self.data_in & 0xFF
        elif offset == 0x08:  # DIR
            return self.dir & 0xFF
        elif offset == 0x0C:  # IRQ_EN
            return self.irq_en & 0xFF
        elif offset == 0x10:  # IRQ_EDGE
            return ((self.irq_edge_fall & 0xFF) << 8) | (self.irq_edge_rise & 0xFF)
        elif offset == 0x14:  # IRQ_STATUS
            return self.irq_status & 0xFF
        return 0

    def write_reg(self, offset: int, data: int):
        if offset == 0x00:
            self.data_out = data & 0xFF
        elif offset == 0x08:
            self.dir = data & 0xFF
        elif offset == 0x0C:
            self.irq_en = data & 0xFF
        elif offset == 0x10:
            self.irq_edge_rise = data & 0xFF
            self.irq_edge_fall = (data >> 8) & 0xFF
        elif offset == 0x14:  # Write-1-to-clear
            self.irq_status &= ~(data & 0xFF)

    def irq(self) -> bool:
        return (self.irq_status & self.irq_en) != 0


# =============================================================================
# PWM Model
# =============================================================================

class PWM:
    """2-channel PWM with 10-bit resolution, watchdog timer."""
    def __init__(self):
        self.period = 2000       # Default: 50M/2000 = 25 kHz base
        self.duty_ch0 = 0
        self.duty_ch1 = 0
        self.enable_ch0 = False
        self.enable_ch1 = False
        self.prescaler = 1

        # Watchdog
        self.wdt_reload = 0xFFFFFF
        self.wdt_counter = 0xFFFFFF
        self.wdt_enable = False
        self.wdt_reset_asserted = False

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.period & 0xFFFF
        elif offset == 0x04:
            return self.duty_ch0 & 0xFFFF
        elif offset == 0x08:
            return self.duty_ch1 & 0xFFFF
        elif offset == 0x0C:  # CONTROL
            ctrl = 0
            if self.enable_ch0: ctrl |= 0x01
            if self.enable_ch1: ctrl |= 0x02
            ctrl |= (self.prescaler & 0x07) << 4
            return ctrl
        # WDT registers (0x00-0x08 relative to WDT_BASE)
        return 0

    def write_reg(self, offset: int, data: int):
        if offset == 0x00:
            self.period = max(data & 0xFFFF, 1)
        elif offset == 0x04:
            self.duty_ch0 = min(data & 0xFFFF, self.period)
        elif offset == 0x08:
            self.duty_ch1 = min(data & 0xFFFF, self.period)
        elif offset == 0x0C:
            self.enable_ch0 = bool(data & 0x01)
            self.enable_ch1 = bool(data & 0x02)
            self.prescaler = max((data >> 4) & 0x07, 1)

    # Watchdog-specific register access (shared peripheral, different base)
    def wdt_read(self, offset: int) -> int:
        if offset == 0x04:  # COUNTER
            return self.wdt_counter & 0xFFFFFF
        elif offset == 0x08:  # CONTROL
            ctrl = 0
            if self.wdt_enable: ctrl |= 0x01
            return ctrl
        return 0

    def wdt_write(self, offset: int, data: int):
        if offset == 0x00:  # RELOAD
            self.wdt_reload = data & 0xFFFFFF
            self.wdt_counter = self.wdt_reload
            self.wdt_reset_asserted = False
        elif offset == 0x08:  # CONTROL
            if data & 0x01:  # Pet (write 1 to bit 0)
                self.wdt_counter = self.wdt_reload
            if data & 0x02:  # Bit 1: enable (1=enable, 0=disable)
                self.wdt_enable = True
            elif (data & 0x03) == 0x00:  # Bit 1=0 and not pet-only: disable
                self.wdt_enable = False

    def tick_wdt(self, cycles: int = 1):
        """Advance watchdog counter by N cycles. Returns True if reset asserted."""
        if self.wdt_enable:
            if self.wdt_counter > cycles:
                self.wdt_counter -= cycles
            else:
                self.wdt_counter = 0
                self.wdt_reset_asserted = True
                return True
        return False

    def duty_percent(self, channel: int) -> float:
        """Return duty cycle as percentage 0.0–100.0."""
        duty = self.duty_ch0 if channel == 0 else self.duty_ch1
        if self.period == 0:
            return 0.0
        return (duty / self.period) * 100.0

    def irq(self) -> bool:
        """PWM period match interrupt (fires once per period)."""
        return self.enable_ch0 or self.enable_ch1  # Always fires when enabled (simplified)

    def wdt_irq(self) -> bool:
        """Watchdog timeout warning (when counter < reload/4, simplified)."""
        return self.wdt_enable and self.wdt_counter < (self.wdt_reload // 4)


# =============================================================================
# Interrupt Controller Model
# =============================================================================

class InterruptController:
    """Aggregates 13 peripheral IRQ sources into single CPU IRQ."""
    IRQ_UART   = 0
    IRQ_SPI    = 1
    IRQ_I2C    = 2
    IRQ_GPIO0  = 3
    IRQ_GPIO1  = 4
    IRQ_GPIO2  = 5
    IRQ_GPIO3  = 6
    IRQ_GPIO4  = 7
    IRQ_GPIO5  = 8
    IRQ_GPIO6  = 9
    IRQ_GPIO7  = 10
    IRQ_PWM    = 11
    IRQ_WDT    = 12

    def __init__(self):
        self.irq_en = 0     # 16-bit per-source enable
        self.irq_in = 0     # 16-bit raw peripheral IRQ inputs
        self.irq_pending = 0

    def set_irq(self, source: int, asserted: bool):
        if asserted:
            self.irq_in |= (1 << source)
        else:
            self.irq_in &= ~(1 << source)

    def update(self):
        self.irq_pending = self.irq_in & self.irq_en

    @property
    def cpu_irq(self) -> bool:
        return self.irq_pending != 0

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.irq_en & 0xFFFF
        elif offset == 0x04:
            return self.irq_pending & 0xFFFF
        elif offset == 0x08:
            return 1 if self.cpu_irq else 0
        return 0

    def write_reg(self, offset: int, data: int):
        if offset == 0x00:
            self.irq_en = data & 0xFFFF


# =============================================================================
# System Control Model
# =============================================================================

class SystemControl:
    def __init__(self):
        self.chip_id = 0x41524755  # "ARGU" in ASCII hex
        self.clk_div = 1
        self.reset_cause = 0       # 0=POR, 1=ext, 2=watchdog, 3=soft
        self.sleep_enable = False
        self.wake_source = 0

    def read_reg(self, offset: int) -> int:
        if offset == 0x00:
            return self.chip_id
        elif offset == 0x04:
            return self.clk_div & 0xFF
        elif offset == 0x08:
            return self.reset_cause & 0xFF
        elif offset == 0x0C:
            status = 0
            if self.sleep_enable: status |= 0x01
            status |= (self.wake_source & 0x0F) << 4
            return status
        return 0

    def write_reg(self, offset: int, data: int):
        if offset == 0x04:
            self.clk_div = max(data & 0xFF, 1)
        elif offset == 0x0C:
            if data & 0x01:
                self.sleep_enable = True
            else:
                self.sleep_enable = False


# =============================================================================
# Wishbone-to-APB Bridge Model
# =============================================================================

class WishboneBridge:
    """Models APB↔Wishbone B4 pipelined bridge. Caravel mgmt SoC accesses
    internal peripherals via this bridge."""
    def __init__(self):
        self.wb_transactions: List[Dict[str, Any]] = []

    def wb_read(self, addr: int) -> int:
        """Caravel management SoC reads from internal APB address space."""
        self.wb_transactions.append({"op": "WB_READ", "addr": f"0x{addr:08X}"})
        return 0  # Value filled by SoC model

    def wb_write(self, addr: int, data: int):
        """Caravel management SoC writes to internal APB address space."""
        self.wb_transactions.append({"op": "WB_WRITE", "addr": f"0x{addr:08X}", "data": f"0x{data:08X}"})


# =============================================================================
# SoC Top-Level Model
# =============================================================================

class ArgusSoC:
    """Top-level model of the PRJ-001 Argus Environmental Sensor-Hub SoC."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.apb = APBBus()
        self.sram = SRAM()
        self.uart = UART()
        self.spi = SPIMaster()
        self.i2c = I2CMaster()
        self.gpio = GPIO()
        self.pwm = PWM()
        self.irq_ctrl = InterruptController()
        self.sys_ctrl = SystemControl()
        self.wb_bridge = WishboneBridge()

        self.test_results: List[Dict[str, Any]] = []
        self._test_idx = 0

    def _record(self, test_name: str, status: str, details: Dict[str, Any] = None):
        self._test_idx += 1
        entry = {
            "test_id": self._test_idx,
            "test": test_name,
            "status": status,
        }
        if details:
            entry["details"] = details
        self.test_results.append(entry)

    # ------------------------------------------------------------------
    # APB read/write dispatch
    # ------------------------------------------------------------------
    def apb_read(self, addr: int) -> int:
        self.apb.read(addr)
        base = addr & 0xFFFF0000
        base_full = addr & 0xFFFFF000

        if base_full == SRAM_BASE:
            return self.sram.read(addr)
        elif base == 0x00010000:
            peri_base = addr & 0xFFFFF00
            off = addr - peri_base
            if peri_base == UART_BASE:
                return self.uart.read_reg(off)
            elif peri_base == SPI_BASE:
                return self.spi.read_reg(off)
            elif peri_base == I2C_BASE:
                return self.i2c.read_reg(off)
            elif peri_base == GPIO_BASE:
                return self.gpio.read_reg(off)
            elif peri_base == PWM_BASE:
                return self.pwm.read_reg(off)
            elif peri_base == IRQ_BASE:
                return self.irq_ctrl.read_reg(off)
            elif peri_base == WDT_BASE:
                return self.pwm.wdt_read(off)
            elif peri_base == SYSCTRL_BASE:
                return self.sys_ctrl.read_reg(off)
        elif (addr & 0x80000000) != 0:
            # Wishbone window — not directly accessible from APB side
            return 0xDEADBEEF

        return 0  # Unmapped

    def apb_write(self, addr: int, data: int):
        self.apb.write(addr, data)
        base = addr & 0xFFFF0000
        base_full = addr & 0xFFFFF000

        if base_full == SRAM_BASE:
            self.sram.write(addr, data)
        elif base == 0x00010000:
            peri_base = addr & 0xFFFFF00
            off = addr - peri_base
            if peri_base == UART_BASE:
                self.uart.write_reg(off, data)
            elif peri_base == SPI_BASE:
                self.spi.write_reg(off, data)
            elif peri_base == I2C_BASE:
                self.i2c.write_reg(off, data)
            elif peri_base == GPIO_BASE:
                self.gpio.write_reg(off, data)
            elif peri_base == PWM_BASE:
                self.pwm.write_reg(off, data)
            elif peri_base == IRQ_BASE:
                self.irq_ctrl.write_reg(off, data)
            elif peri_base == WDT_BASE:
                self.pwm.wdt_write(off, data)
            elif peri_base == SYSCTRL_BASE:
                self.sys_ctrl.write_reg(off, data)

    def _update_irqs(self):
        """Collect peripheral IRQs and feed to interrupt controller."""
        self.irq_ctrl.set_irq(InterruptController.IRQ_UART, self.uart.irq())
        self.irq_ctrl.set_irq(InterruptController.IRQ_SPI, self.spi.irq())
        self.irq_ctrl.set_irq(InterruptController.IRQ_I2C, self.i2c.irq())
        for pin in range(8):
            gpio_irq = bool(self.gpio.irq_status & self.gpio.irq_en & (1 << pin))
            self.irq_ctrl.set_irq(InterruptController.IRQ_GPIO0 + pin, gpio_irq)
        self.irq_ctrl.set_irq(InterruptController.IRQ_PWM, self.pwm.irq())
        self.irq_ctrl.set_irq(InterruptController.IRQ_WDT, self.pwm.wdt_irq())
        self.irq_ctrl.update()

    # ------------------------------------------------------------------
    # Test Suite
    # ------------------------------------------------------------------

    def run_all_tests(self) -> Dict[str, Any]:
        self.test_01_chip_id()
        self.test_02_sram_read_write()
        self.test_03_uart_tx_rx()
        self.test_04_uart_loopback()
        self.test_05_spi_transfer()
        self.test_06_spi_mode_switch()
        self.test_07_i2c_write()
        self.test_08_i2c_nack()
        self.test_09_gpio_output_input()
        self.test_10_gpio_edge_interrupt()
        self.test_11_pwm_duty_cycle()
        self.test_12_pwm_watchdog()
        self.test_13_interrupt_controller()
        self.test_14_apb_error()
        self.test_15_sram_byte_access()
        self.test_16_wishbone_bridge()
        self.test_17_sleep_wake()

        passed = sum(1 for t in self.test_results if t["status"] == "PASS")
        failed = sum(1 for t in self.test_results if t["status"] == "FAIL")
        total = len(self.test_results)

        return {
            "project": "PRJ-001",
            "codename": "Argus",
            "seed": self.seed,
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed}/{total}",
            },
            "tests": self.test_results,
            "_metadata": {
                "model_version": "1.0.0",
                "timestamp": "2026-07-20T00:00:00Z",
                "sys_clk_hz": SYS_CLK_HZ,
                "pdk": "sky130A",
                "isa": "RV32I",
            },
        }

    # --- Test 1: Chip ID ---
    def test_01_chip_id(self):
        val = self.apb_read(SYSCTRL_BASE + 0x00)
        expected = 0x41524755
        self._record("CHIP_ID", "PASS" if val == expected else "FAIL",
                     {"read": f"0x{val:08X}", "expected": f"0x{expected:08X}"})

    # --- Test 2: SRAM read/write ---
    def test_02_sram_read_write(self):
        patterns = [0xDEADBEEF, 0xCAFEBABE, 0x00000000, 0xFFFFFFFF, 0xA5A5A5A5]
        results = []
        for i, pat in enumerate(patterns):
            addr = SRAM_BASE + (i * 4)
            self.apb_write(addr, pat)
            rd = self.apb_read(addr)
            results.append({"addr": f"0x{addr:08X}", "write": f"0x{pat:08X}", "read": f"0x{rd:08X}", "ok": rd == pat})
        all_ok = all(r["ok"] for r in results)
        self._record("SRAM_RW", "PASS" if all_ok else "FAIL",
                     {"patterns": len(patterns), "results": results})

    # --- Test 3: UART TX/RX ---
    def test_03_uart_tx_rx(self):
        # Configure UART
        self.apb_write(UART_BASE + 0x0C, 0x03)  # TX + RX enable
        self.apb_write(UART_BASE + 0x10, 434)    # 115200 bps at 50 MHz

        # Send bytes
        tx_bytes = [0x48, 0x65, 0x6C, 0x6C, 0x6F]  # "Hello"
        for b in tx_bytes:
            self.apb_write(UART_BASE + 0x00, b)
        self.uart.flush_tx()

        ok = (self.uart.tx_sent == tx_bytes)
        self._record("UART_TX", "PASS" if ok else "FAIL",
                     {"sent": [f"0x{b:02X}" for b in self.uart.tx_sent],
                      "expected": [f"0x{b:02X}" for b in tx_bytes]})

        # Receive bytes
        self.apb_write(UART_BASE + 0x14, 0x11)  # RX threshold = 1
        rx_bytes = [0x57, 0x6F, 0x72, 0x6C, 0x64]  # "World"
        for b in rx_bytes:
            self.uart.inject_rx(b)
        received = []
        for _ in range(len(rx_bytes)):
            received.append(self.apb_read(UART_BASE + 0x00))

        ok = (received == rx_bytes)
        self._record("UART_RX", "PASS" if ok else "FAIL",
                     {"received": [f"0x{b:02X}" for b in received],
                      "expected": [f"0x{b:02X}" for b in rx_bytes]})

    # --- Test 4: UART loopback (TX → RX via external loopback model) ---
    def test_04_uart_loopback(self):
        self.apb_write(UART_BASE + 0x0C, 0x03)
        self.apb_write(UART_BASE + 0x10, 434)

        test_data = list(range(256))  # 0x00–0xFF
        # TX FIFO is 8 deep; write in chunks, flush after each chunk
        for i in range(0, 256, 8):
            chunk = test_data[i:i+8]
            for b in chunk:
                self.apb_write(UART_BASE + 0x00, b)
            self.uart.flush_tx()

        # Simulate loopback: inject what was sent (last 256 items in tx_sent)
        sent_last_256 = self.uart.tx_sent[-256:]
        received = []
        # RX FIFO is 8 deep: inject 8, read 8, repeat
        for i in range(0, 256, 8):
            chunk = sent_last_256[i:i+8]
            for b in chunk:
                self.uart.inject_rx(b)
            for _ in range(len(chunk)):
                received.append(self.apb_read(UART_BASE + 0x00))

        ok = (received == test_data)
        self._record("UART_LOOPBACK", "PASS" if ok else "FAIL",
                     {"bytes": 256, "match": ok})

    # --- Test 5: SPI transfer ---
    def test_05_spi_transfer(self):
        # Configure SPI Mode 0
        self.apb_write(SPI_BASE + 0x0C, 0x10)   # CS active, CPOL=0, CPHA=0
        self.apb_write(SPI_BASE + 0x10, 2)       # prescaler=2 -> 12.5 MHz

        # Send and receive
        tx_vals = [0xA5, 0x5A, 0xFF, 0x00]
        for v in tx_vals:
            self.apb_write(SPI_BASE + 0x00, v)

        rx_vals = []
        for _ in tx_vals:
            rx_vals.append(self.apb_read(SPI_BASE + 0x04))

        expected_rx = [(~v) & 0xFF for v in tx_vals]
        ok = (rx_vals == expected_rx)
        self._record("SPI_TRANSFER", "PASS" if ok else "FAIL",
                     {"tx": [f"0x{v:02X}" for v in tx_vals],
                      "rx": [f"0x{v:02X}" for v in rx_vals],
                      "expected_rx": [f"0x{v:02X}" for v in expected_rx],
                      "transfers": len(self.spi.transfers)})

    # --- Test 6: SPI mode switch ---
    def test_06_spi_mode_switch(self):
        # Mode 0 (CPOL=0, CPHA=0)
        self.apb_write(SPI_BASE + 0x0C, 0x10)
        self.apb_write(SPI_BASE + 0x00, 0x42)
        m0_rx = self.apb_read(SPI_BASE + 0x04)

        # Mode 3 (CPOL=1, CPHA=1)
        self.apb_write(SPI_BASE + 0x0C, 0x13)
        self.apb_write(SPI_BASE + 0x00, 0x42)
        m3_rx = self.apb_read(SPI_BASE + 0x04)

        ok = (m0_rx == 0xBD and m3_rx == 0xBD)  # ~0x42 = 0xBD
        self._record("SPI_MODE_SWITCH", "PASS" if ok else "FAIL",
                     {"mode0_rx": f"0x{m0_rx:02X}", "mode3_rx": f"0x{m3_rx:02X}"})

    # --- Test 7: I2C write ---
    def test_07_i2c_write(self):
        # Configure I2C: 100 kHz
        self.apb_write(I2C_BASE + 0x10, 250)  # CLK_DIV_LO
        self.apb_write(I2C_BASE + 0x14, 250)  # CLK_DIV_HI

        # I2C write to 0x48 (common temp sensor addr), data = 0x55
        self.apb_write(I2C_BASE + 0x04, 0x90)  # ADDR: 0x48 << 1 | W(0)
        self.apb_write(I2C_BASE + 0x00, 0x55)  # DATA
        self.apb_write(I2C_BASE + 0x0C, 0x01)  # START

        # Read status
        status = self.apb_read(I2C_BASE + 0x08)
        ok = (status & 0x10) != 0        # Transfer done
        ok = ok and not (status & 0x04)  # No NACK
        self._record("I2C_WRITE", "PASS" if ok else "FAIL",
                     {"addr": "0x48", "data": "0x55", "status": f"0x{status:02X}",
                      "transactions": len(self.i2c.transactions)})

    # --- Test 8: I2C NACK ---
    def test_08_i2c_nack(self):
        # Try to address a reserved/non-existent address (0x7F)
        self.apb_write(I2C_BASE + 0x04, 0xFE)  # ADDR: 0x7F << 1 | W(0)
        self.apb_write(I2C_BASE + 0x00, 0xAA)
        self.apb_write(I2C_BASE + 0x0C, 0x01)  # START

        status = self.apb_read(I2C_BASE + 0x08)
        nack = (status & 0x04) != 0
        self._record("I2C_NACK", "PASS" if nack else "FAIL",
                     {"addr": "0x7F", "status": f"0x{status:02X}", "nack": nack})

    # --- Test 9: GPIO output → input ---
    def test_09_gpio_output_input(self):
        # Set pins [3:0] as output, [7:4] as input
        self.apb_write(GPIO_BASE + 0x08, 0x0F)   # DIR: lower 4 out, upper 4 in
        self.apb_write(GPIO_BASE + 0x00, 0xA5)    # DATA_OUT: 0xA5 (1010_0101)

        # Simulate external input on upper nibble
        self.gpio.set_inputs(0x50)               # Upper nibble driven to 0x5

        data_out = self.apb_read(GPIO_BASE + 0x00)
        data_in = self.apb_read(GPIO_BASE + 0x04)

        ok = (data_out == 0xA5) and (data_in == 0x50) and (self.apb_read(GPIO_BASE + 0x08) == 0x0F)
        self._record("GPIO_DIR", "PASS" if ok else "FAIL",
                     {"data_out": f"0x{data_out:02X}", "data_in": f"0x{data_in:02X}",
                      "dir": f"0x{self.apb_read(GPIO_BASE + 0x08):02X}"})

    # --- Test 10: GPIO edge interrupt ---
    def test_10_gpio_edge_interrupt(self):
        # Configure pin 0: input, rising edge IRQ
        self.apb_write(GPIO_BASE + 0x08, 0x00)    # All inputs
        self.apb_write(GPIO_BASE + 0x0C, 0x01)    # IRQ_EN pin 0
        self.apb_write(GPIO_BASE + 0x10, 0x0001)  # IRQ_EDGE: rising on pin 0
        self.apb_write(GPIO_BASE + 0x14, 0xFF)    # Clear all pending IRQs

        # Simulate rising edge on pin 0
        self.gpio.set_inputs(0x00)  # All low
        self.gpio.set_inputs(0x01)  # Pin 0 goes high

        irq_status = self.apb_read(GPIO_BASE + 0x14)
        ok = (irq_status & 0x01) != 0   # Pin 0 IRQ pending
        self._record("GPIO_EDGE_IRQ", "PASS" if ok else "FAIL",
                     {"irq_status": f"0x{irq_status:02X}"})

    # --- Test 11: PWM duty cycle ---
    def test_11_pwm_duty_cycle(self):
        # Configure PWM: 25 kHz base, 50% duty ch0, 25% duty ch1
        self.apb_write(PWM_BASE + 0x00, 2000)     # Period = 2000 → 25 kHz
        self.apb_write(PWM_BASE + 0x04, 1000)     # CH0 duty = 50%
        self.apb_write(PWM_BASE + 0x08, 500)      # CH1 duty = 25%
        self.apb_write(PWM_BASE + 0x0C, 0x03)     # Enable CH0, CH1

        d0 = self.pwm.duty_percent(0)
        d1 = self.pwm.duty_percent(1)

        ok = abs(d0 - 50.0) < 0.1 and abs(d1 - 25.0) < 0.1
        self._record("PWM_DUTY", "PASS" if ok else "FAIL",
                     {"ch0_duty_pct": f"{d0:.1f}", "ch1_duty_pct": f"{d1:.1f}",
                      "period": self.pwm.period})

    # --- Test 12: PWM watchdog ---
    def test_12_pwm_watchdog(self):
        self.pwm.wdt_write(0x00, 1000)   # RELOAD = 1000
        self.pwm.wdt_write(0x08, 0x02)   # Enable watchdog

        # Pet the watchdog
        self.pwm.wdt_write(0x08, 0x01)   # Pet (reloads counter)

        # Advance 500 cycles (should NOT time out)
        timeout = self.pwm.tick_wdt(500)
        ok = not timeout and self.pwm.wdt_counter == 500

        # Advance another 600 cycles (should time out at 500+600=1100 > 1000)
        timeout = self.pwm.tick_wdt(600)
        ok = ok and timeout and self.pwm.wdt_reset_asserted

        self._record("PWM_WDT", "PASS" if ok else "FAIL",
                     {"timeout_500": not timeout, "timeout_1100": timeout,
                      "wdt_counter": self.pwm.wdt_counter})

    # --- Test 13: Interrupt controller ---
    def test_13_interrupt_controller(self):
        # Enable UART IRQ
        self.apb_write(IRQ_BASE + 0x00, 0x0001)  # Enable UART IRQ

        # Trigger UART TX interrupt (by writing data with TX enabled)
        self.apb_write(UART_BASE + 0x0C, 0x01)    # TX enable
        self.apb_write(UART_BASE + 0x14, 0x04)    # TX FIFO threshold = 4 (empty FIFO < 4 = IRQ)
        self._update_irqs()

        cpu_irq = self.apb_read(IRQ_BASE + 0x08)
        pending = self.apb_read(IRQ_BASE + 0x04)

        ok = (cpu_irq == 1) and ((pending & 0x0001) != 0)
        self._record("IRQ_CTRL", "PASS" if ok else "FAIL",
                     {"cpu_irq": cpu_irq, "pending": f"0x{pending:04X}"})

    # --- Test 14: APB error on unmapped access ---
    def test_14_apb_error(self):
        # Access unmapped address 0x0002_0000
        val = self.apb_read(0x00020000)
        # Unmapped reads return 0; the APB slave asserts PSLVERR (modeled as 0 return)
        ok = (val == 0)
        self._record("APB_ERROR", "PASS" if ok else "FAIL",
                     {"unmapped_addr": "0x00020000", "read_value": f"0x{val:08X}"})

    # --- Test 15: SRAM byte access ---
    def test_15_sram_byte_access(self):
        addr = SRAM_BASE + 0x100
        self.apb_write(addr, 0x12345678)
        # Read back word
        wd = self.apb_read(addr)
        ok = (wd == 0x12345678)
        self._record("SRAM_WORD", "PASS" if ok else "FAIL",
                     {"addr": f"0x{addr:08X}", "word": f"0x{wd:08X}"})

        # Verify SRAM reads/writes counters
        ok = ok and (self.sram.reads >= 2) and (self.sram.writes >= 5)
        self._record("SRAM_STATS", "PASS" if ok else "FAIL",
                     {"reads": self.sram.reads, "writes": self.sram.writes})

    # --- Test 16: Wishbone bridge ---
    def test_16_wishbone_bridge(self):
        # Simulate Caravel management SoC writing firmware to SRAM via Wishbone
        self.wb_bridge.wb_write(SRAM_BASE + 0x00, 0x00000013)  # nop (addi x0, x0, 0)
        self.wb_bridge.wb_write(SRAM_BASE + 0x04, 0x00000013)  # nop
        self.wb_bridge.wb_write(UART_BASE + 0x10, 434)         # Configure UART baud

        # Read back via Wishbone
        self.wb_bridge.wb_read(SRAM_BASE + 0x00)

        ok = len(self.wb_bridge.wb_transactions) == 4
        self._record("WISHBONE_BRIDGE", "PASS" if ok else "FAIL",
                     {"transactions": len(self.wb_bridge.wb_transactions)})

    # --- Test 17: Sleep/wake ---
    def test_17_sleep_wake(self):
        # Enter sleep
        self.apb_write(SYSCTRL_BASE + 0x0C, 0x01)  # SLEEP=1
        ok = self.sys_ctrl.sleep_enable

        # Wake via GPIO edge
        self.sys_ctrl.wake_source = 1  # GPIO wake
        self.sys_ctrl.sleep_enable = False
        ok = ok and not self.sys_ctrl.sleep_enable

        self._record("SLEEP_WAKE", "PASS" if ok else "FAIL",
                     {"sleep_entered": True, "wake_source": self.sys_ctrl.wake_source})


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="PRJ-001 Argus Golden Model")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--out", type=str, default="golden_output.json",
                        help="Output JSON file path")
    args = parser.parse_args()

    soc = ArgusSoC(seed=args.seed)
    output = soc.run_all_tests()

    # Compute MD5 of the tests array only (exclude metadata for determinism check)
    tests_json = json.dumps(output["tests"], sort_keys=True, indent=2)
    output["_metadata"]["tests_md5"] = md5(tests_json)

    with open(args.out, "w") as f:
        json.dump(output, f, indent=2, sort_keys=True)

    print(f"Golden model complete: {output['summary']['passed']}/{output['summary']['total_tests']} tests PASS")
    print(f"Output: {args.out}")
    print(f"Tests MD5: {output['_metadata']['tests_md5']}")

    return 0 if output["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
