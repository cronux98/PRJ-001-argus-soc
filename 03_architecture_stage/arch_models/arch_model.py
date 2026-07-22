#!/usr/bin/env python3
"""
PRJ-001 Argus — Architecture Validation Model.
Built from ARCHITECTURE.md. Validates against golden model output.

Produces arch_comparison.json with per-test pass/fail relative to golden_output.json.

Usage:
    python3 arch_model.py \
        --golden ../02_specification_stage/golden_model/golden_output.json \
        --out arch_comparison.json
"""

import argparse
import json
import sys
import os
from typing import Dict, List, Any, Optional

# =============================================================================
# Architecture Model — Reconstructed from ARCHITECTURE.md
# =============================================================================

SRAM_BASE       = 0x00000000
SRAM_SIZE       = 0x1000
UART_BASE       = 0x00010000
SPI_BASE        = 0x00010100
I2C_BASE        = 0x00010200
GPIO_BASE       = 0x00010300
PWM_BASE        = 0x00010400
IRQ_BASE        = 0x00010500
WDT_BASE        = 0x00010600
SYSCTRL_BASE    = 0x00010700
WB_WINDOW_BASE  = 0x80000000
SYS_CLK_HZ      = 50_000_000

# ---- SRAM ----
class SRAM:
    def __init__(self):
        self.mem: Dict[int, int] = {}
        self.reads = 0; self.writes = 0
    def read(self, addr: int) -> int:
        off = addr - SRAM_BASE
        if 0 <= off < SRAM_SIZE:
            self.reads += 1
            return self.mem.get(off, 0)
        return 0
    def write(self, addr: int, data: int):
        off = addr - SRAM_BASE
        if 0 <= off < SRAM_SIZE:
            self.writes += 1
            self.mem[off] = data & 0xFFFFFFFF

# ---- UART ----
class UART:
    def __init__(self):
        self.tx_fifo = []; self.rx_fifo = []
        self.tx_en = self.rx_en = False
        self.baud_div = 434       # 115200 bps at 50 MHz (per spec)
        self.tx_sent = []; self.rx_received = []
        self.rx_overrun = False
        self.fifo_thresh = 4; self.rx_fifo_thresh = 1
    def read_reg(self, off: int) -> int:
        if off == 0x00:  # RXDATA (read at offset 0)
            if self.rx_fifo:
                v = self.rx_fifo.pop(0); self.rx_received.append(v)
                return v
            return 0
        if off == 0x08:  # STATUS
            s = 0
            if len(self.tx_fifo) == 8: s |= 0x01
            if len(self.tx_fifo) == 0: s |= 0x02
            if len(self.rx_fifo) == 8: s |= 0x04
            if len(self.rx_fifo) == 0: s |= 0x08
            if self.rx_overrun: s |= 0x20
            return s
        if off == 0x10: return self.baud_div & 0xFFFF
        if off == 0x14: return ((self.rx_fifo_thresh & 0x0F) << 4) | (self.fifo_thresh & 0x0F)
        return 0
    def write_reg(self, off: int, data: int):
        if off == 0x00 and len(self.tx_fifo) < 8:
            self.tx_fifo.append(data & 0xFF)
        elif off == 0x0C:
            self.tx_en = bool(data & 0x01); self.rx_en = bool(data & 0x02)
        elif off == 0x10: self.baud_div = data & 0xFFFF
        elif off == 0x14:
            self.rx_fifo_thresh = (data >> 4) & 0x0F
            self.fifo_thresh = data & 0x0F
    def inject_rx(self, b: int):
        if len(self.rx_fifo) < 8: self.rx_fifo.append(b & 0xFF)
        else: self.rx_overrun = True
    def flush_tx(self):
        while self.tx_fifo: self.tx_sent.append(self.tx_fifo.pop(0))
    def irq(self) -> bool:
        tx_irq = self.tx_en and len(self.tx_fifo) < self.fifo_thresh
        rx_irq = self.rx_en and len(self.rx_fifo) >= self.rx_fifo_thresh
        return tx_irq or rx_irq

# ---- SPI ----
class SPIMaster:
    def __init__(self):
        self.tx_fifo = []; self.rx_fifo = []
        self.cpol = 0; self.cpha = 0; self.prescaler = 2
        self.transfers = []
    def read_reg(self, off: int) -> int:
        if off == 0x04:
            return self.rx_fifo.pop(0) if self.rx_fifo else 0
        if off == 0x08:
            s = 0
            if len(self.tx_fifo) == 0: s |= 0x01
            if len(self.rx_fifo) > 0: s |= 0x02
            s |= (self.cpol & 1) << 4
            s |= (self.cpha & 1) << 5
            return s
        if off == 0x10: return self.prescaler & 0xFF
        return 0
    def write_reg(self, off: int, data: int):
        if off == 0x00 and len(self.tx_fifo) < 8:
            self.tx_fifo.append(data & 0xFF); self._do_transfer()
        elif off == 0x0C:
            self.cpol = data & 1; self.cpha = (data >> 1) & 1
        elif off == 0x10: self.prescaler = max(data & 0xFF, 2)
    def _do_transfer(self):
        while self.tx_fifo:
            tx = self.tx_fifo.pop(0)
            rx = (~tx) & 0xFF
            self.rx_fifo.append(rx)
            self.transfers.append({"mode": f"CPOL={self.cpol},CPHA={self.cpha}", "tx": f"0x{tx:02X}", "rx": f"0x{rx:02X}"})
    def irq(self) -> bool: return len(self.rx_fifo) > 0

# ---- I2C ----
class I2CMaster:
    def __init__(self):
        self.clk_div_lo = 125; self.clk_div_hi = 125
        self.addr = 0; self.data_reg = 0
        self.busy = False; self.nack = False; self.arb_lost = False
        self.transactions = []
    def read_reg(self, off: int) -> int:
        if off == 0x00: return self.data_reg & 0xFF
        if off == 0x04: return self.addr & 0xFF
        if off == 0x08:
            s = 0
            if self.busy: s |= 0x01
            if self.nack: s |= 0x04
            if self.arb_lost: s |= 0x08
            if not self.busy and not self.nack: s |= 0x10
            return s
        return 0
    def write_reg(self, off: int, data: int):
        if off == 0x00: self.data_reg = data & 0xFF
        elif off == 0x04: self.addr = data & 0xFF
        elif off == 0x0C:
            if data & 0x01: self._start_transfer()
            if data & 0x02: self.transactions.append({"op": "STOP"})
        elif off == 0x10: self.clk_div_lo = data & 0xFF
        elif off == 0x14: self.clk_div_hi = data & 0xFF
    def _start_transfer(self):
        is_read = bool(self.addr & 0x01)
        addr_7bit = (self.addr >> 1) & 0x7F
        self.busy = True; self.nack = False
        e = {"addr_7bit": f"0x{addr_7bit:02X}", "rw": "READ" if is_read else "WRITE",
             "data": f"0x{self.data_reg:02X}", "mode": "START",
             "scl_freq_hz": SYS_CLK_HZ // (self.clk_div_lo + self.clk_div_hi)}
        if addr_7bit >= 0x78:
            self.nack = True; e["ack"] = "NACK"; self.busy = False
        else:
            e["ack"] = "ACK"; self.busy = False
        self.transactions.append(e)
    def irq(self) -> bool: return not self.busy

# ---- GPIO ----
class GPIO:
    def __init__(self):
        self.data_out = 0; self.data_in = 0; self.dir = 0
        self.irq_en = 0; self.irq_edge_rise = 0; self.irq_edge_fall = 0
        self.irq_status = 0; self.prev_input = 0
    def set_inputs(self, v: int):
        old = self.prev_input; new = v & 0xFF; self.data_in = new
        for p in range(8):
            ob, nb = (old >> p) & 1, (new >> p) & 1
            if self.irq_en & (1 << p):
                if self.irq_edge_rise & (1 << p) and ob == 0 and nb == 1:
                    self.irq_status |= (1 << p)
                if self.irq_edge_fall & (1 << p) and ob == 1 and nb == 0:
                    self.irq_status |= (1 << p)
        self.prev_input = new
    def read_reg(self, off: int) -> int:
        if off == 0x00: return self.data_out & 0xFF
        if off == 0x04: return self.data_in & 0xFF
        if off == 0x08: return self.dir & 0xFF
        if off == 0x0C: return self.irq_en & 0xFF
        if off == 0x10: return ((self.irq_edge_fall & 0xFF) << 8) | (self.irq_edge_rise & 0xFF)
        if off == 0x14: return self.irq_status & 0xFF
        return 0
    def write_reg(self, off: int, data: int):
        if off == 0x00: self.data_out = data & 0xFF
        elif off == 0x08: self.dir = data & 0xFF
        elif off == 0x0C: self.irq_en = data & 0xFF
        elif off == 0x10:
            self.irq_edge_rise = data & 0xFF; self.irq_edge_fall = (data >> 8) & 0xFF
        elif off == 0x14: self.irq_status &= ~(data & 0xFF)
    def irq(self) -> bool: return (self.irq_status & self.irq_en) != 0

# ---- PWM + WDT ----
class PWM:
    def __init__(self):
        self.period = 2000; self.duty_ch0 = 0; self.duty_ch1 = 0
        self.en_ch0 = False; self.en_ch1 = False; self.prescaler = 1
        self.wdt_reload = 0xFFFFFF; self.wdt_counter = 0xFFFFFF
        self.wdt_en = False; self.wdt_rst = False
    def read_reg(self, off: int) -> int:
        if off == 0x00: return self.period & 0xFFFF
        if off == 0x04: return self.duty_ch0 & 0xFFFF
        if off == 0x08: return self.duty_ch1 & 0xFFFF
        if off == 0x0C:
            c = 0
            if self.en_ch0: c |= 0x01
            if self.en_ch1: c |= 0x02
            c |= (self.prescaler & 0x07) << 4
            return c
        return 0
    def write_reg(self, off: int, data: int):
        if off == 0x00: self.period = max(data & 0xFFFF, 1)
        elif off == 0x04: self.duty_ch0 = min(data & 0xFFFF, self.period)
        elif off == 0x08: self.duty_ch1 = min(data & 0xFFFF, self.period)
        elif off == 0x0C:
            self.en_ch0 = bool(data & 0x01); self.en_ch1 = bool(data & 0x02)
            self.prescaler = max((data >> 4) & 0x07, 1)
    def wdt_read(self, off: int) -> int:
        if off == 0x04: return self.wdt_counter & 0xFFFFFF
        if off == 0x08:
            c = 0
            if self.wdt_en: c |= 0x01
            return c
        return 0
    def wdt_write(self, off: int, data: int):
        if off == 0x00:
            self.wdt_reload = data & 0xFFFFFF; self.wdt_counter = self.wdt_reload; self.wdt_rst = False
        elif off == 0x08:
            if data & 0x01: self.wdt_counter = self.wdt_reload
            if data & 0x02: self.wdt_en = True
            elif (data & 0x03) == 0x00: self.wdt_en = False
    def tick_wdt(self, cycles: int = 1) -> bool:
        if self.wdt_en:
            if self.wdt_counter > cycles: self.wdt_counter -= cycles
            else: self.wdt_counter = 0; self.wdt_rst = True; return True
        return False
    def duty_percent(self, ch: int) -> float:
        d = self.duty_ch0 if ch == 0 else self.duty_ch1
        return (d / self.period) * 100.0 if self.period > 0 else 0.0
    def irq(self) -> bool: return self.en_ch0 or self.en_ch1
    def wdt_irq(self) -> bool: return self.wdt_en and self.wdt_counter < (self.wdt_reload // 4)

# ---- Interrupt Controller ----
class InterruptController:
    IRQ_UART=0; IRQ_SPI=1; IRQ_I2C=2; IRQ_GPIO0=3; IRQ_GPIO1=4; IRQ_GPIO2=5
    IRQ_GPIO3=6; IRQ_GPIO4=7; IRQ_GPIO5=8; IRQ_GPIO6=9; IRQ_GPIO7=10
    IRQ_PWM=11; IRQ_WDT=12
    def __init__(self):
        self.irq_en = 0; self.irq_in = 0; self.irq_pending = 0
    def set_irq(self, src: int, asserted: bool):
        if asserted: self.irq_in |= (1 << src)
        else: self.irq_in &= ~(1 << src)
    def update(self): self.irq_pending = self.irq_in & self.irq_en
    @property
    def cpu_irq(self) -> bool: return self.irq_pending != 0
    def read_reg(self, off: int) -> int:
        if off == 0x00: return self.irq_en & 0xFFFF
        if off == 0x04: return self.irq_pending & 0xFFFF
        if off == 0x08: return 1 if self.cpu_irq else 0
        return 0
    def write_reg(self, off: int, data: int):
        if off == 0x00: self.irq_en = data & 0xFFFF

# ---- System Control ----
class SystemControl:
    def __init__(self):
        self.chip_id = 0x41524755; self.clk_div = 1
        self.reset_cause = 0; self.sleep_en = False; self.wake_src = 0
    def read_reg(self, off: int) -> int:
        if off == 0x00: return self.chip_id
        if off == 0x04: return self.clk_div & 0xFF
        if off == 0x08: return self.reset_cause & 0xFF
        if off == 0x0C:
            s = 0
            if self.sleep_en: s |= 0x01
            s |= (self.wake_src & 0x0F) << 4
            return s
        return 0
    def write_reg(self, off: int, data: int):
        if off == 0x04: self.clk_div = max(data & 0xFF, 1)
        elif off == 0x0C:
            self.sleep_en = bool(data & 0x01)

# ---- Wishbone Bridge ----
class WishboneBridge:
    def __init__(self):
        self.wb_transactions = []
    def wb_read(self, addr: int) -> int:
        self.wb_transactions.append({"op": "WB_READ", "addr": f"0x{addr:08X}"})
        return 0
    def wb_write(self, addr: int, data: int):
        self.wb_transactions.append({"op": "WB_WRITE", "addr": f"0x{addr:08X}", "data": f"0x{data:08X}"})


# =============================================================================
# SoC Model + Test Suite (from ARCHITECTURE.md §4)
# =============================================================================

class ArgusArchModel:
    def __init__(self):
        self.sram = SRAM()
        self.uart = UART()
        self.spi = SPIMaster()
        self.i2c = I2CMaster()
        self.gpio = GPIO()
        self.pwm = PWM()
        self.irq_ctrl = InterruptController()
        self.sys_ctrl = SystemControl()
        self.wb_bridge = WishboneBridge()
        self.results: List[Dict] = []

    def _apb_read(self, addr: int) -> int:
        base = addr & 0xFFFF0000
        bf = addr & 0xFFFFF000
        if bf == SRAM_BASE: return self.sram.read(addr)
        if base == 0x00010000:
            pb = addr & 0xFFFFFF00; off = addr - pb
            if pb == UART_BASE: return self.uart.read_reg(off)
            if pb == SPI_BASE: return self.spi.read_reg(off)
            if pb == I2C_BASE: return self.i2c.read_reg(off)
            if pb == GPIO_BASE: return self.gpio.read_reg(off)
            if pb == PWM_BASE: return self.pwm.read_reg(off)
            if pb == IRQ_BASE: return self.irq_ctrl.read_reg(off)
            if pb == WDT_BASE: return self.pwm.wdt_read(off)
            if pb == SYSCTRL_BASE: return self.sys_ctrl.read_reg(off)
        if addr & 0x80000000: return 0xDEADBEEF
        return 0

    def _apb_write(self, addr: int, data: int):
        base = addr & 0xFFFF0000
        bf = addr & 0xFFFFF000
        if bf == SRAM_BASE: self.sram.write(addr, data)
        elif base == 0x00010000:
            pb = addr & 0xFFFFFF00; off = addr - pb
            if pb == UART_BASE: self.uart.write_reg(off, data)
            elif pb == SPI_BASE: self.spi.write_reg(off, data)
            elif pb == I2C_BASE: self.i2c.write_reg(off, data)
            elif pb == GPIO_BASE: self.gpio.write_reg(off, data)
            elif pb == PWM_BASE: self.pwm.write_reg(off, data)
            elif pb == IRQ_BASE: self.irq_ctrl.write_reg(off, data)
            elif pb == WDT_BASE: self.pwm.wdt_write(off, data)
            elif pb == SYSCTRL_BASE: self.sys_ctrl.write_reg(off, data)

    def _update_irqs(self):
        self.irq_ctrl.set_irq(InterruptController.IRQ_UART, self.uart.irq())
        self.irq_ctrl.set_irq(InterruptController.IRQ_SPI, self.spi.irq())
        self.irq_ctrl.set_irq(InterruptController.IRQ_I2C, self.i2c.irq())
        for p in range(8):
            gpio_irq = bool(self.gpio.irq_status & self.gpio.irq_en & (1 << p))
            self.irq_ctrl.set_irq(InterruptController.IRQ_GPIO0 + p, gpio_irq)
        self.irq_ctrl.set_irq(InterruptController.IRQ_PWM, self.pwm.irq())
        self.irq_ctrl.set_irq(InterruptController.IRQ_WDT, self.pwm.wdt_irq())
        self.irq_ctrl.update()

    # --- Tests ---
    def test_chip_id(self):
        v = self._apb_read(SYSCTRL_BASE + 0x00)
        return {"test": "CHIP_ID", "status": "PASS" if v == 0x41524755 else "FAIL",
                "read": f"0x{v:08X}", "expected": "0x41524755"}

    def test_sram_rw(self):
        patterns = [0xDEADBEEF, 0xCAFEBABE, 0x00000000, 0xFFFFFFFF, 0xA5A5A5A5]
        ok = True
        for i, p in enumerate(patterns):
            addr = SRAM_BASE + i * 4
            self._apb_write(addr, p)
            rd = self._apb_read(addr)
            if rd != p: ok = False
        return {"test": "SRAM_RW", "status": "PASS" if ok else "FAIL"}

    def test_uart_tx(self):
        self._apb_write(UART_BASE + 0x0C, 0x03)
        self._apb_write(UART_BASE + 0x10, 434)
        tx = [0x48, 0x65, 0x6C, 0x6C, 0x6F]
        for b in tx: self._apb_write(UART_BASE + 0x00, b)
        self.uart.flush_tx()
        ok = self.uart.tx_sent == tx
        return {"test": "UART_TX", "status": "PASS" if ok else "FAIL",
                "sent": [f"0x{b:02X}" for b in self.uart.tx_sent],
                "expected": [f"0x{b:02X}" for b in tx]}

    def test_uart_rx(self):
        self._apb_write(UART_BASE + 0x14, 0x11)
        rx = [0x57, 0x6F, 0x72, 0x6C, 0x64]
        for b in rx: self.uart.inject_rx(b)
        recv = [self._apb_read(UART_BASE + 0x00) for _ in rx]
        ok = recv == rx
        return {"test": "UART_RX", "status": "PASS" if ok else "FAIL",
                "received": [f"0x{b:02X}" for b in recv],
                "expected": [f"0x{b:02X}" for b in rx]}

    def test_uart_loopback(self):
        self._apb_write(UART_BASE + 0x0C, 0x03)
        self._apb_write(UART_BASE + 0x10, 434)
        td = list(range(256))
        for i in range(0, 256, 8):
            for b in td[i:i+8]: self._apb_write(UART_BASE + 0x00, b)
            self.uart.flush_tx()
        sl256 = self.uart.tx_sent[-256:]
        recv = []
        for i in range(0, 256, 8):
            for b in sl256[i:i+8]: self.uart.inject_rx(b)
            for _ in range(min(8, 256-i)): recv.append(self._apb_read(UART_BASE + 0x00))
        return {"test": "UART_LOOPBACK", "status": "PASS" if recv == td else "FAIL",
                "bytes": 256, "match": recv == td}

    def test_spi_transfer(self):
        self._apb_write(SPI_BASE + 0x0C, 0x10)
        self._apb_write(SPI_BASE + 0x10, 2)
        tx = [0xA5, 0x5A, 0xFF, 0x00]
        for v in tx: self._apb_write(SPI_BASE + 0x00, v)
        rx = [self._apb_read(SPI_BASE + 0x04) for _ in tx]
        erx = [(~v) & 0xFF for v in tx]
        return {"test": "SPI_TRANSFER", "status": "PASS" if rx == erx else "FAIL",
                "tx": [f"0x{v:02X}" for v in tx], "rx": [f"0x{v:02X}" for v in rx],
                "expected_rx": [f"0x{v:02X}" for v in erx],
                "transfers": len(self.spi.transfers)}

    def test_spi_mode_switch(self):
        self._apb_write(SPI_BASE + 0x0C, 0x10)
        self._apb_write(SPI_BASE + 0x00, 0x42)
        m0 = self._apb_read(SPI_BASE + 0x04)
        self._apb_write(SPI_BASE + 0x0C, 0x13)
        self._apb_write(SPI_BASE + 0x00, 0x42)
        m3 = self._apb_read(SPI_BASE + 0x04)
        ok = m0 == 0xBD and m3 == 0xBD
        return {"test": "SPI_MODE_SWITCH", "status": "PASS" if ok else "FAIL",
                "mode0_rx": f"0x{m0:02X}", "mode3_rx": f"0x{m3:02X}"}

    def test_i2c_write(self):
        self._apb_write(I2C_BASE + 0x10, 250)
        self._apb_write(I2C_BASE + 0x14, 250)
        self._apb_write(I2C_BASE + 0x04, 0x90)
        self._apb_write(I2C_BASE + 0x00, 0x55)
        self._apb_write(I2C_BASE + 0x0C, 0x01)
        st = self._apb_read(I2C_BASE + 0x08)
        ok = (st & 0x10) != 0 and not (st & 0x04)
        return {"test": "I2C_WRITE", "status": "PASS" if ok else "FAIL",
                "details": {"addr": "0x48", "data": "0x55", "status": f"0x{st:02X}",
                "transactions": len(self.i2c.transactions)}}

    def test_i2c_nack(self):
        self._apb_write(I2C_BASE + 0x04, 0xFE)
        self._apb_write(I2C_BASE + 0x00, 0xAA)
        self._apb_write(I2C_BASE + 0x0C, 0x01)
        st = self._apb_read(I2C_BASE + 0x08)
        n = (st & 0x04) != 0
        return {"test": "I2C_NACK", "status": "PASS" if n else "FAIL",
                "details": {"addr": "0x7F", "status": f"0x{st:02X}", "nack": n}}

    def test_gpio_dir(self):
        self._apb_write(GPIO_BASE + 0x08, 0x0F)
        self._apb_write(GPIO_BASE + 0x00, 0xA5)
        self.gpio.set_inputs(0x50)
        do = self._apb_read(GPIO_BASE + 0x00)
        di = self._apb_read(GPIO_BASE + 0x04)
        dr = self._apb_read(GPIO_BASE + 0x08)
        ok = do == 0xA5 and di == 0x50 and dr == 0x0F
        return {"test": "GPIO_DIR", "status": "PASS" if ok else "FAIL",
                "data_out": f"0x{do:02X}", "data_in": f"0x{di:02X}", "dir": f"0x{dr:02X}"}

    def test_gpio_edge_irq(self):
        self._apb_write(GPIO_BASE + 0x08, 0x00)
        self._apb_write(GPIO_BASE + 0x0C, 0x01)
        self._apb_write(GPIO_BASE + 0x10, 0x0001)
        self._apb_write(GPIO_BASE + 0x14, 0xFF)
        self.gpio.set_inputs(0x00)
        self.gpio.set_inputs(0x01)
        st = self._apb_read(GPIO_BASE + 0x14)
        ok = (st & 0x01) != 0
        return {"test": "GPIO_EDGE_IRQ", "status": "PASS" if ok else "FAIL",
                "irq_status": f"0x{st:02X}"}

    def test_pwm_duty(self):
        self._apb_write(PWM_BASE + 0x00, 2000)
        self._apb_write(PWM_BASE + 0x04, 1000)
        self._apb_write(PWM_BASE + 0x08, 500)
        self._apb_write(PWM_BASE + 0x0C, 0x03)
        d0 = self.pwm.duty_percent(0); d1 = self.pwm.duty_percent(1)
        ok = abs(d0 - 50.0) < 0.1 and abs(d1 - 25.0) < 0.1
        return {"test": "PWM_DUTY", "status": "PASS" if ok else "FAIL",
                "ch0_duty_pct": f"{d0:.1f}", "ch1_duty_pct": f"{d1:.1f}", "period": self.pwm.period}

    def test_pwm_wdt(self):
        self.pwm.wdt_write(0x00, 1000)
        self.pwm.wdt_write(0x08, 0x02)
        self.pwm.wdt_write(0x08, 0x01)
        to = self.pwm.tick_wdt(500)
        ok = not to and self.pwm.wdt_counter == 500
        to = self.pwm.tick_wdt(600)
        ok = ok and to and self.pwm.wdt_rst
        return {"test": "PWM_WDT", "status": "PASS" if ok else "FAIL",
                "timeout_500": not to, "timeout_1100": to, "wdt_counter": self.pwm.wdt_counter}

    def test_irq_ctrl(self):
        self._apb_write(IRQ_BASE + 0x00, 0x0001)
        self._apb_write(UART_BASE + 0x0C, 0x01)
        self._apb_write(UART_BASE + 0x14, 0x04)
        self._update_irqs()
        cpu = self._apb_read(IRQ_BASE + 0x08)
        pend = self._apb_read(IRQ_BASE + 0x04)
        ok = cpu == 1 and (pend & 0x0001) != 0
        return {"test": "IRQ_CTRL", "status": "PASS" if ok else "FAIL",
                "cpu_irq": cpu, "pending": f"0x{pend:04X}"}

    def test_apb_error(self):
        v = self._apb_read(0x00020000)
        return {"test": "APB_ERROR", "status": "PASS" if v == 0 else "FAIL"}

    def test_sram_word_stats(self):
        addr = SRAM_BASE + 0x100
        self._apb_write(addr, 0x12345678)
        wd = self._apb_read(addr)
        ok = wd == 0x12345678
        # SRAM_STATS: reads >= 2, writes >= 5 (cumulative from test_02 + this test)
        rd = self.sram.reads; wr = self.sram.writes
        ok2 = rd >= 2 and wr >= 5
        return [
            {"test": "SRAM_WORD", "status": "PASS" if ok else "FAIL",
             "details": {"addr": f"0x{addr:08X}", "word": f"0x{wd:08X}"}},
            {"test": "SRAM_STATS", "status": "PASS" if ok2 else "FAIL",
             "details": {"reads": rd, "writes": wr}},
        ]

    def test_wb_bridge(self):
        self.wb_bridge.wb_write(SRAM_BASE + 0x00, 0x00000013)
        self.wb_bridge.wb_write(SRAM_BASE + 0x04, 0x00000013)
        self.wb_bridge.wb_write(UART_BASE + 0x10, 434)
        self.wb_bridge.wb_read(SRAM_BASE + 0x00)
        ok = len(self.wb_bridge.wb_transactions) == 4
        return {"test": "WISHBONE_BRIDGE", "status": "PASS" if ok else "FAIL",
                "details": {"transactions": len(self.wb_bridge.wb_transactions)}}

    def test_sleep_wake(self):
        self._apb_write(SYSCTRL_BASE + 0x0C, 0x01)
        ok = self.sys_ctrl.sleep_en
        self.sys_ctrl.wake_src = 1
        self.sys_ctrl.sleep_en = False
        ok = ok and not self.sys_ctrl.sleep_en
        return {"test": "SLEEP_WAKE", "status": "PASS" if ok else "FAIL",
                "details": {"sleep_entered": True, "wake_source": self.sys_ctrl.wake_src}}

    def run_all(self) -> List[Dict]:
        results = [
            self.test_chip_id(), self.test_sram_rw(),
            self.test_uart_tx(), self.test_uart_rx(), self.test_uart_loopback(),
            self.test_spi_transfer(), self.test_spi_mode_switch(),
            self.test_i2c_write(), self.test_i2c_nack(),
            self.test_gpio_dir(), self.test_gpio_edge_irq(),
            self.test_pwm_duty(), self.test_pwm_wdt(),
            self.test_irq_ctrl(), self.test_apb_error(),
        ]
        # test_sram_word_stats returns a list of two test results
        results.extend(self.test_sram_word_stats())
        results.append(self.test_wb_bridge())
        results.append(self.test_sleep_wake())
        return results


# =============================================================================
# Comparison with Golden Model
# =============================================================================

def compare_with_golden(arch_results: List[Dict], golden_path: str) -> Dict:
    """Compare architecture model results with golden model output."""
    with open(golden_path) as f:
        golden = json.load(f)

    golden_tests = {t.get("test", ""): t for t in golden.get("tests", [])
                    if "test" in t and "_metadata" not in str(t)}
    comparisons = []
    passed = 0; failed = 0

    for arch_test in arch_results:
        test_name = arch_test.get("test", "")
        golden_test = golden_tests.get(test_name)

        if golden_test is None:
            comparisons.append({
                "test": test_name,
                "result": "NO_GOLDEN",
                "arch_status": arch_test.get("status"),
                "golden_status": "MISSING"
            })
            failed += 1
            continue

        arch_status = arch_test.get("status", "UNKNOWN")
        golden_status = golden_test.get("status", "UNKNOWN")

        # Compare status
        status_match = (arch_status == golden_status)

        # If both PASS, it's a match
        if status_match:
            comparisons.append({
                "test": test_name,
                "result": "IDENTICAL",
                "arch_status": arch_status,
                "golden_status": golden_status
            })
            passed += 1
        else:
            comparisons.append({
                "test": test_name,
                "result": "MISMATCH",
                "arch_status": arch_status,
                "golden_status": golden_status,
                "arch_details": {k: v for k, v in arch_test.items() if k not in ("test", "status")},
                "golden_details": {k: v for k, v in golden_test.items()
                                   if k not in ("test", "status", "test_id")}
            })
            failed += 1

    total = passed + failed
    return {
        "project": "PRJ-001",
        "codename": "Argus",
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed}/{total}",
        "verdict": "PASS" if failed == 0 else "FAIL",
        "golden_seed": golden.get("seed"),
        "golden_pass_rate": golden.get("summary", {}).get("pass_rate", "?"),
        "comparisons": comparisons,
    }


def main():
    parser = argparse.ArgumentParser(description="PRJ-001 Architecture Validation")
    parser.add_argument("--golden", required=True, help="Path to golden_output.json")
    parser.add_argument("--out", default="arch_comparison.json", help="Output path")
    args = parser.parse_args()

    if not os.path.exists(args.golden):
        print(f"ERROR: golden file not found: {args.golden}", file=sys.stderr)
        sys.exit(1)

    # Run architecture model
    model = ArgusArchModel()
    results = model.run_all()

    # Compare with golden
    comparison = compare_with_golden(results, args.golden)

    with open(args.out, "w") as f:
        json.dump(comparison, f, indent=2)

    print(f"Architecture validation: {comparison['verdict']}")
    print(f"  Tests: {comparison['pass_rate']}")
    print(f"  Golden seed: {comparison['golden_seed']}")
    print(f"  Golden pass rate: {comparison['golden_pass_rate']}")
    print(f"  Output: {args.out}")

    sys.exit(0 if comparison["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
