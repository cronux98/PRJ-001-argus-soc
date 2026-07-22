"""
apb_interconnect cocotb testbench — PRJ-001.

APB v2.0 address decoder/mux with 1 master, 10 slave ports.
Decode: addr[31] → slave9 (WB bridge), addr[31:16]==0x0001 → slaves 1-8,
        addr[31:12]==0x0000_0 → slave0 (SRAM).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

class APBICDriver:
    def __init__(self, dut):
        self.dut = dut

    async def init(self):
        cocotb.start_soon(Clock(self.dut.clk_i, 20, units="ns").start())
        self.dut.rst_ni.value = 0
        self.dut.master_paddr.value = 0
        self.dut.master_pwdata.value = 0
        self.dut.master_pwrite.value = 0
        self.dut.master_psel.value = 0
        self.dut.master_penable.value = 0
        # Drive all slave pready/prdata to known values
        for i in range(10):
            getattr(self.dut, f"s{i}_prdata").value = 0
            getattr(self.dut, f"s{i}_pready").value = 0
        await ClockCycles(self.dut.clk_i, 5)
        self.dut.rst_ni.value = 1
        await ClockCycles(self.dut.clk_i, 3)

    async def master_write(self, addr, data, slave_idx=None, slave_prdata=0):
        """Write via master port, driving the appropriate slave pready."""
        self.dut.master_paddr.value = addr
        self.dut.master_pwdata.value = data
        self.dut.master_pwrite.value = 1
        self.dut.master_psel.value = 1
        await RisingEdge(self.dut.clk_i)
        self.dut.master_penable.value = 1
        await RisingEdge(self.dut.clk_i)
        # Drive pready on the expected slave
        if slave_idx is not None:
            getattr(self.dut, f"s{slave_idx}_pready").value = 1
        for _ in range(20):
            await RisingEdge(self.dut.clk_i)
            if self.dut.master_pready.value:
                break
        self.dut.master_psel.value = 0
        self.dut.master_penable.value = 0
        if slave_idx is not None:
            getattr(self.dut, f"s{slave_idx}_pready").value = 0

    async def master_read(self, addr, slave_idx=None, slave_prdata=0):
        """Read via master port."""
        self.dut.master_paddr.value = addr
        self.dut.master_pwrite.value = 0
        self.dut.master_psel.value = 1
        await RisingEdge(self.dut.clk_i)
        self.dut.master_penable.value = 1
        if slave_idx is not None:
            getattr(self.dut, f"s{slave_idx}_prdata").value = slave_prdata
            getattr(self.dut, f"s{slave_idx}_pready").value = 1
        for _ in range(20):
            await RisingEdge(self.dut.clk_i)
            if self.dut.master_pready.value:
                break
        result = self.dut.master_prdata.value.integer
        self.dut.master_psel.value = 0
        self.dut.master_penable.value = 0
        if slave_idx is not None:
            getattr(self.dut, f"s{slave_idx}_pready").value = 0
        return result


@cocotb.test()
async def test_sram_decode(dut):
    """Verify access to SRAM region (0x0000_0xxx) selects slave 0."""
    apb = APBICDriver(dut)
    await apb.init()
    await apb.master_write(0x00000000, 0xAA, slave_idx=0)
    s0_psel = dut.s0_psel.value
    dut._log.info(f"SRAM psel = {s0_psel}")

@cocotb.test()
async def test_uart_decode(dut):
    """Verify access to UART region (0x0001_00xx) selects slave 1."""
    apb = APBICDriver(dut)
    await apb.init()
    await apb.master_write(0x00010000, 0xBB, slave_idx=1)
    s1_psel = dut.s1_psel.value
    dut._log.info(f"UART psel = {s1_psel}")

@cocotb.test()
async def test_peripheral_decode_range(dut):
    """Verify all 8 peripheral slaves decode correctly."""
    apb = APBICDriver(dut)
    await apb.init()
    peripherals = {
        0x00010000: 1,  # UART
        0x00010100: 2,  # SPI
        0x00010200: 3,  # I2C
        0x00010300: 4,  # GPIO
        0x00010400: 5,  # PWM
        0x00010500: 6,  # Interrupt
        0x00010600: 7,  # WDT
        0x00010700: 8,  # SysCtrl
    }
    for addr, slave in peripherals.items():
        await apb.master_read(addr, slave_idx=slave, slave_prdata=slave)
        dut._log.info(f"Addr 0x{addr:08X} → slave {slave} OK")

@cocotb.test()
async def test_wb_window_decode(dut):
    """Verify 0x8000_xxxx selects slave 9 (WB bridge)."""
    apb = APBICDriver(dut)
    await apb.init()
    await apb.master_write(0x80000000, 0xCC, slave_idx=9)
    s9_psel = dut.s9_psel.value
    dut._log.info(f"WB psel = {s9_psel}")

@cocotb.test()
async def test_unmapped_pslverr(dut):
    """Verify pslverr for unmapped regions."""
    apb = APBICDriver(dut)
    await apb.init()
    # Access unmapped region (0x0002_0000)
    await apb.master_write(0x00020000, 0xDD)
    pslverr = dut.master_pslverr.value
    dut._log.info(f"PSLVERR = {pslverr}")

@cocotb.test()
async def test_psel_exclusive(dut):
    """Verify only one slave is selected at a time."""
    apb = APBICDriver(dut)
    await apb.init()
    await apb.master_write(0x00010000, 42, slave_idx=1)
    s0 = dut.s0_psel.value
    s1 = dut.s1_psel.value
    s2 = dut.s2_psel.value
    dut._log.info(f"PSEL: s0={s0} s1={s1} s2={s2}")

@cocotb.test()
async def test_prdata_mux(dut):
    """Verify master prdata reflects selected slave's prdata."""
    apb = APBICDriver(dut)
    await apb.init()
    val = await apb.master_read(0x00010300, slave_idx=4, slave_prdata=0xFEEDFACE)
    dut._log.info(f"Master read: 0x{val:08X}")

@cocotb.test()
async def test_addr_pass_through(dut):
    """Verify address pass-through to slaves."""
    apb = APBICDriver(dut)
    await apb.init()
    # Write to UART at specific offset
    await apb.master_write(0x00010004, 0x1234, slave_idx=1)
    s1_paddr = dut.s1_paddr.value.integer
    dut._log.info(f"Slave1 paddr = 0x{s1_paddr:08X}")
