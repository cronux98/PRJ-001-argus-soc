"""Minimal debug test for SRAM."""
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

@cocotb.test()
async def debug_sram(dut):
    """Debug: write one word, read it back, dump signals."""
    cocotb.start_soon(Clock(dut.clk_i, 20, units="ns").start())
    dut.rst_ni.value = 0
    dut.imem_addr.value = 0
    dut.dmem_addr.value = 0
    dut.dmem_wdata.value = 0
    dut.dmem_we.value = 0
    dut.dmem_be.value = 0xF
    dut.apb_paddr.value = 0
    dut.apb_pwdata.value = 0
    dut.apb_pwrite.value = 0
    dut.apb_psel.value = 0
    dut.apb_penable.value = 0
    await ClockCycles(dut.clk_i, 5)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 3)

    # APB write: addr=0, data=0xDEADBEEF
    dut.apb_paddr.value = 0
    dut.apb_pwdata.value = 0xDEADBEEF
    dut.apb_pwrite.value = 1
    dut.apb_psel.value = 1
    await RisingEdge(dut.clk_i)
    dut._log.info(f"After SETUP edge: psel={dut.apb_psel.value} penable={dut.apb_penable.value} pwrite={dut.apb_pwrite.value} pready={dut.apb_pready.value}")
    
    dut.apb_penable.value = 1
    await RisingEdge(dut.clk_i)
    dut._log.info(f"After ACCESS edge: psel={dut.apb_psel.value} penable={dut.apb_penable.value} pwrite={dut.apb_pwrite.value} pready={dut.apb_pready.value} prdata=0x{int(dut.apb_prdata.value):08X}")
    
    # wait and deassert
    await RisingEdge(dut.clk_i)
    dut.apb_psel.value = 0
    dut.apb_penable.value = 0
    dut.apb_pwrite.value = 0
    dut._log.info(f"After write complete: psel={dut.apb_psel.value}")
    
    # Now APB read: addr=0
    await RisingEdge(dut.clk_i)
    dut.apb_paddr.value = 0
    dut.apb_pwrite.value = 0
    dut.apb_psel.value = 1
    await RisingEdge(dut.clk_i)
    dut.apb_penable.value = 1
    await RisingEdge(dut.clk_i)
    dut._log.info(f"READ after ACCESS: prdata=0x{int(dut.apb_prdata.value):08X}")
    
    # One more cycle to let data settle
    await RisingEdge(dut.clk_i)
    dut._log.info(f"READ next cycle: prdata=0x{int(dut.apb_prdata.value):08X}")
    dut.apb_psel.value = 0
    dut.apb_penable.value = 0
