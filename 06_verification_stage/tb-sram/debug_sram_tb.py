"""Minimal debug test for SRAM - standalone, no shared driver."""
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

@cocotb.test()
async def debug_sram(dut):
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

    dut._log.info("=== Starting APB Write ===")
    # APB write addr=0, data=0xDEAD
    dut.apb_paddr.value = 0
    dut.apb_pwdata.value = 0xDEAD
    dut.apb_pwrite.value = 1
    dut.apb_psel.value = 1
    await RisingEdge(dut.clk_i)
    dut._log.info(f"After setup: psel={int(dut.apb_psel.value)} pen={int(dut.apb_penable.value)} pwrite={int(dut.apb_pwrite.value)} paddr=0x{int(dut.apb_paddr.value):X} pwdata=0x{int(dut.apb_pwdata.value):X}")
    
    dut.apb_penable.value = 1
    await RisingEdge(dut.clk_i)
    dut._log.info(f"After access: psel={int(dut.apb_psel.value)} pen={int(dut.apb_penable.value)} pready={int(dut.apb_pready.value)} prdata=0x{int(dut.apb_prdata.value):08X}")
    
    # Deassert
    dut.apb_psel.value = 0
    dut.apb_penable.value = 0
    dut.apb_pwrite.value = 0
    await ClockCycles(dut.clk_i, 2)
    dut._log.info("=== Write done, starting read ===")
    
    # APB read addr=0
    dut.apb_paddr.value = 0
    dut.apb_pwrite.value = 0
    dut.apb_psel.value = 1
    await RisingEdge(dut.clk_i)
    dut.apb_penable.value = 1
    await RisingEdge(dut.clk_i)
    dut._log.info(f"After read access: psel={int(dut.apb_psel.value)} pen={int(dut.apb_penable.value)} pready={int(dut.apb_pready.value)} prdata=0x{int(dut.apb_prdata.value):08X}")
    
    # Wait one more cycle and read again
    dut.apb_psel.value = 0
    dut.apb_penable.value = 0
    await RisingEdge(dut.clk_i)
    dut._log.info(f"After read deassert: prdata=0x{int(dut.apb_prdata.value):08X}")
    
    # Try another read with more delay
    await ClockCycles(dut.clk_i, 2)
    dut.apb_psel.value = 1
    dut.apb_pwrite.value = 0
    dut.apb_paddr.value = 0
    await RisingEdge(dut.clk_i)
    dut.apb_penable.value = 1
    await RisingEdge(dut.clk_i)
    await RisingEdge(dut.clk_i)  # wait extra cycle
    dut._log.info(f"Delayed read: prdata=0x{int(dut.apb_prdata.value):08X}")
    dut.apb_psel.value = 0
    dut.apb_penable.value = 0
    
    # Now try DMEM write then read
    dut._log.info("=== DMEM write test ===")
    dut.dmem_addr.value = 0x10
    dut.dmem_wdata.value = 0xBEEF
    dut.dmem_we.value = 1
    dut.dmem_be.value = 0xF
    await RisingEdge(dut.clk_i)
    dut.dmem_we.value = 0
    await ClockCycles(dut.clk_i, 2)
    
    # Read via APB
    dut.apb_psel.value = 1
    dut.apb_pwrite.value = 0
    dut.apb_paddr.value = 0x10
    await RisingEdge(dut.clk_i)
    dut.apb_penable.value = 1
    await RisingEdge(dut.clk_i)
    await RisingEdge(dut.clk_i)
    dut._log.info(f"APB read of DMEM addr 0x10: prdata=0x{int(dut.apb_prdata.value):08X}")
    dut.apb_psel.value = 0
    dut.apb_penable.value = 0
    
    # Read via DMEM 
    dut.dmem_addr.value = 0x10
    dut.dmem_we.value = 0
    await RisingEdge(dut.clk_i)
    await RisingEdge(dut.clk_i)
    dut._log.info(f"DMEM read addr 0x10: rdata=0x{int(dut.dmem_rdata.value):08X}")
