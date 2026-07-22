"""
Shared APB driver for PRJ-001 cocotb testbenches.

Supports two APB signal conventions:
  - APB3 Std:  PCLK, PRESETn, PWRITE, PWDATA[31:0], PADDR[31:0],
                PENABLE, PSEL, PREADY, PRDATA[31:0]
  - Custom APB: clk_i, rst_ni, pwrite, pwdata[31:0], paddr[7:0]|31:0,
                psel, penable, pready, prdata[31:0]

Usage:
    from apb_driver import APB3Driver, CustomAPBDriver
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
from cocotb.clock import Clock


class APB3Driver:
    """Driver for Efabless/FOSSi APB3 peripherals (capitalized signal names)."""

    def __init__(self, dut, name=""):
        self.dut = dut
        self.name = name or "APB3"
        self.log = dut._log

    async def init(self, clk_period_ns=20):
        """Start clock and apply reset."""
        cocotb.start_soon(Clock(self.dut.PCLK, clk_period_ns, units="ns").start())
        self.dut.PRESETn.value = 0
        self.dut.PSEL.value = 0
        self.dut.PENABLE.value = 0
        self.dut.PWRITE.value = 0
        self.dut.PWDATA.value = 0
        self.dut.PADDR.value = 0
        await ClockCycles(self.dut.PCLK, 5)
        self.dut.PRESETn.value = 1
        await ClockCycles(self.dut.PCLK, 3)

    async def write(self, addr, data):
        """APB write: PSEL→PENABLE→wait PREADY→deassert."""
        await RisingEdge(self.dut.PCLK)
        self.dut.PADDR.value = addr
        self.dut.PWDATA.value = data
        self.dut.PWRITE.value = 1
        self.dut.PSEL.value = 1
        await RisingEdge(self.dut.PCLK)
        self.dut.PENABLE.value = 1
        await RisingEdge(self.dut.PCLK)
        while not self.dut.PREADY.value:
            await RisingEdge(self.dut.PCLK)
        self.dut.PSEL.value = 0
        self.dut.PENABLE.value = 0
        self.dut.PWRITE.value = 0

    async def read(self, addr):
        """APB read: PSEL→PENABLE→wait PREADY→capture PRDATA→deassert."""
        await RisingEdge(self.dut.PCLK)
        self.dut.PADDR.value = addr
        self.dut.PWRITE.value = 0
        self.dut.PSEL.value = 1
        await RisingEdge(self.dut.PCLK)
        self.dut.PENABLE.value = 1
        await RisingEdge(self.dut.PCLK)
        while not self.dut.PREADY.value:
            await RisingEdge(self.dut.PCLK)
        result = self.dut.PRDATA.value.integer
        self.dut.PSEL.value = 0
        self.dut.PENABLE.value = 0
        return result


class CustomAPBDriver:
    """Driver for custom CREATE modules with lowercase APB signal names."""

    def __init__(self, dut, name="", addr_width=8, clk_signal="clk_i", rst_signal="rst_ni"):
        self.dut = dut
        self.name = name or "CustomAPB"
        self.addr_width = addr_width
        self.clk_signal = clk_signal
        self.rst_signal = rst_signal
        self.log = dut._log

    async def init(self, clk_period_ns=20):
        clk = getattr(self.dut, self.clk_signal)
        rst = getattr(self.dut, self.rst_signal)
        cocotb.start_soon(Clock(clk, clk_period_ns, units="ns").start())
        rst.value = 0
        self.dut.psel.value = 0
        self.dut.penable.value = 0
        self.dut.pwrite.value = 0
        self.dut.pwdata.value = 0
        self.dut.paddr.value = 0
        await ClockCycles(clk, 5)
        rst.value = 1
        await ClockCycles(clk, 3)

    async def write(self, addr, data):
        clk = getattr(self.dut, self.clk_signal)
        await RisingEdge(clk)
        self.dut.paddr.value = addr
        self.dut.pwdata.value = data
        self.dut.pwrite.value = 1
        self.dut.psel.value = 1
        await RisingEdge(clk)
        self.dut.penable.value = 1
        await RisingEdge(clk)
        ready = self.dut.pready.value
        while not ready:
            await RisingEdge(clk)
            ready = self.dut.pready.value
        self.dut.psel.value = 0
        self.dut.penable.value = 0
        self.dut.pwrite.value = 0

    async def read(self, addr):
        clk = getattr(self.dut, self.clk_signal)
        await RisingEdge(clk)
        self.dut.paddr.value = addr
        self.dut.pwrite.value = 0
        self.dut.psel.value = 1
        await RisingEdge(clk)
        self.dut.penable.value = 1
        await RisingEdge(clk)
        ready = self.dut.pready.value
        while not ready:
            await RisingEdge(clk)
            ready = self.dut.pready.value
        result = self.dut.prdata.value.integer
        self.dut.psel.value = 0
        self.dut.penable.value = 0
        return result
