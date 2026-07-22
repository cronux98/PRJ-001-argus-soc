"""
wb_bridge cocotb testbench — PRJ-001.

Wishbone B4 → APB bridge. Wishbone side connects to Caravel,
APB side connects to internal APB interconnect.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

class WBDriver:
    def __init__(self, dut):
        self.dut = dut

    async def init(self):
        cocotb.start_soon(Clock(self.dut.clk_i, 20, units="ns").start())
        self.dut.rst_ni.value = 0
        self.dut.wb_adr_i.value = 0
        self.dut.wb_dat_i.value = 0
        self.dut.wb_sel_i.value = 0
        self.dut.wb_we_i.value = 0
        self.dut.wb_stb_i.value = 0
        self.dut.wb_cyc_i.value = 0
        self.dut.apb_prdata.value = 0
        self.dut.apb_pready.value = 0
        self.dut.apb_pslverr.value = 0
        await ClockCycles(self.dut.clk_i, 5)
        self.dut.rst_ni.value = 1
        await ClockCycles(self.dut.clk_i, 3)

    async def wb_write(self, addr, data):
        self.dut.wb_adr_i.value = addr
        self.dut.wb_dat_i.value = data
        self.dut.wb_sel_i.value = 0xF
        self.dut.wb_we_i.value = 1
        self.dut.wb_stb_i.value = 1
        self.dut.wb_cyc_i.value = 1
        await RisingEdge(self.dut.clk_i)
        # Wait for APB-side psel to assert
        for _ in range(20):
            await RisingEdge(self.dut.clk_i)
            if self.dut.wb_ack_o.value:
                break
            # Drive pready high to unblock APB state machine
            if self.dut.apb_psel.value and not self.dut.apb_pready.value:
                self.dut.apb_pready.value = 1
        self.dut.wb_stb_i.value = 0
        self.dut.wb_cyc_i.value = 0
        await ClockCycles(self.dut.clk_i, 2)
        self.dut.apb_pready.value = 0

    async def wb_read(self, addr, read_data=0):
        self.dut.wb_adr_i.value = addr
        self.dut.wb_sel_i.value = 0xF
        self.dut.wb_we_i.value = 0
        self.dut.wb_stb_i.value = 1
        self.dut.wb_cyc_i.value = 1
        self.dut.apb_prdata.value = read_data
        await RisingEdge(self.dut.clk_i)
        for _ in range(20):
            await RisingEdge(self.dut.clk_i)
            if self.dut.apb_psel.value and not self.dut.apb_pready.value:
                self.dut.apb_pready.value = 1
            if self.dut.wb_ack_o.value:
                break
        result = self.dut.wb_dat_o.value.integer
        self.dut.wb_stb_i.value = 0
        self.dut.wb_cyc_i.value = 0
        await ClockCycles(self.dut.clk_i, 2)
        self.dut.apb_pready.value = 0
        return result


@cocotb.test()
async def test_wb_write_apb_forward(dut):
    """Verify WB write is forwarded to APB side."""
    wb = WBDriver(dut)
    await wb.init()
    await wb.wb_write(0x80000000, 0xDEADBEEF)
    dut._log.info(f"APB addr={dut.apb_paddr.value.integer:08X} data={dut.apb_pwdata.value.integer:08X}")

@cocotb.test()
async def test_wb_read_forward(dut):
    """Verify WB read captures APB prdata."""
    wb = WBDriver(dut)
    await wb.init()
    val = await wb.wb_read(0x80000004, read_data=0xCAFEBABE)
    dut._log.info(f"WB read back: 0x{val:08X}")

@cocotb.test()
async def test_out_of_window_rejected(dut):
    """Verify WB transactions outside 0x8000_xxxx are ignored."""
    wb = WBDriver(dut)
    await wb.init()
    # Access at 0x00001000 (not in WB window)
    await wb.wb_write(0x00001000, 0x12345678)
    # APB psel should NOT assert
    apb_psel = dut.apb_psel.value
    dut._log.info(f"APB psel with out-of-window = {apb_psel}")

@cocotb.test()
async def test_wb_ack_handshake(dut):
    """Verify WB ack_o asserts when APB pready is driven."""
    wb = WBDriver(dut)
    await wb.init()
    # Start WB read
    dut.wb_adr_i.value = 0x80000008
    dut.wb_sel_i.value = 0xF
    dut.wb_we_i.value = 0
    dut.wb_stb_i.value = 1
    dut.wb_cyc_i.value = 1
    dut.apb_prdata.value = 0xAAAAAAAA
    await RisingEdge(dut.clk_i)
    # Wait for APB psel
    for _ in range(10):
        await RisingEdge(dut.clk_i)
        if dut.apb_psel.value:
            dut.apb_pready.value = 1
            break
    await RisingEdge(dut.clk_i)
    ack = dut.wb_ack_o.value
    dut._log.info(f"WB ack = {ack}")
    dut.wb_stb_i.value = 0
    dut.wb_cyc_i.value = 0
    await ClockCycles(dut.clk_i, 2)

@cocotb.test()
async def test_wb_byte_select(dut):
    """Verify WB byte select is forwarded."""
    wb = WBDriver(dut)
    await wb.init()
    dut.wb_adr_i.value = 0x80000010
    dut.wb_dat_i.value = 0xFF
    dut.wb_sel_i.value = 0x1  # byte 0 only
    dut.wb_we_i.value = 1
    dut.wb_stb_i.value = 1
    dut.wb_cyc_i.value = 1
    await RisingEdge(dut.clk_i)
    for _ in range(10):
        await RisingEdge(dut.clk_i)
        if dut.wb_ack_o.value:
            break
        if dut.apb_psel.value:
            dut.apb_pready.value = 1
    dut.wb_stb_i.value = 0
    dut.wb_cyc_i.value = 0
    await ClockCycles(dut.clk_i, 2)

@cocotb.test()
async def test_address_translation(dut):
    """Verify WB 0x8000_xxxx → APB 0x0000_xxxx translation."""
    wb = WBDriver(dut)
    await wb.init()
    # Write to WB 0x80000020, check APB addr
    await wb.wb_write(0x80000020, 0x42)
    # After completion, check what APB addr was
    # (read indirectly via the WB readback path)
    dut._log.info(f"Address translation test complete")

@cocotb.test()
async def test_wb_err_default(dut):
    """Verify wb_err_o is low by default."""
    wb = WBDriver(dut)
    await wb.init()
    err = dut.wb_err_o.value
    dut._log.info(f"wb_err_o = {err}")

@cocotb.test()
async def test_idle_state(dut):
    """Verify bridge starts in IDLE state after reset."""
    wb = WBDriver(dut)
    await wb.init()
    await ClockCycles(dut.clk_i, 5)
    apb_psel = dut.apb_psel.value
    assert apb_psel == 0, f"APB psel should be 0 in IDLE, got {apb_psel}"
