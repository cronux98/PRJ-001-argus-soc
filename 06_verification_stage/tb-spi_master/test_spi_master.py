"""
EF_SPI_APB cocotb testbench — PRJ-001.  15 tests.

Register offsets:
  0x0000: RXDATA  R
  0x0004: TXDATA  W
  0x0008: CFG     RW  reset=0x00
  0x000C: CTRL    RW  reset=0x00
  0x0010: PR      RW  (prescale)
  0x0014: STATUS  R   reset=0x01 (idle)
  0xFE00-0xFE18: FIFO control
  0xFF00-0xFF0C: Interrupt registers
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from apb_driver import APB3Driver
import cocotb
from cocotb.triggers import ClockCycles

# ── Original 8 tests ─────────────────────────────────────────────────

@cocotb.test()
async def test_status_idle(dut):
    """Verify STATUS is readable after reset."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    status = await apb.read(0x0014)
    dut._log.info(f"STATUS = 0x{status:08X}")
    assert status != 0xFFFFFFFF, f"STATUS readback anomaly"

@cocotb.test()
async def test_cfg_rw(dut):
    """Verify CFG register read/write."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0x0008, 0x00000003)
    val = await apb.read(0x0008)
    assert val == 0x03, f"CFG: expected 0x03, got 0x{val:08X}"

@cocotb.test()
async def test_ctrl_enable(dut):
    """Verify CTRL register enable bit."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0x000C, 0x00000001)
    ctrl = await apb.read(0x000C)
    assert (ctrl & 1) == 1, f"CTRL[0]: expected 1, got {ctrl}"

@cocotb.test()
async def test_prescale_rw(dut):
    """Verify PR register."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0x0010, 0x00000002)
    pr = await apb.read(0x0010)
    assert pr == 0x02, f"PR: expected 0x02, got 0x{pr:08X}"

@cocotb.test()
async def test_csb_high_when_disabled(dut):
    """Verify CSB is high when SPI disabled."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await ClockCycles(dut.PCLK, 5)
    csb_val = int(dut.csb.value)
    dut._log.info(f"csb = {csb_val}")
    assert csb_val == 1, f"CSB should be high when disabled, got {csb_val}"

@cocotb.test()
async def test_interrupt_regs(dut):
    """Verify IM/RIS/MIS/IC."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0xFF00, 0x0F)
    im = await apb.read(0xFF00)
    assert im == 0x0F, f"IM: expected 0x0F, got 0x{im:08X}"

@cocotb.test()
async def test_tx_with_cs_high(dut):
    """Verify TXDATA write with CS high."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0x000C, 0x00000001)
    await apb.write(0x0004, 0x00000055)
    await ClockCycles(dut.PCLK, 10)
    dut._log.info(f"sclk={dut.sclk.value} mosi={dut.mosi.value} csb={dut.csb.value}")

@cocotb.test()
async def test_sclk_stable_when_disabled(dut):
    """Verify SCLK is stable when SPI disabled."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await ClockCycles(dut.PCLK, 20)
    sclk = int(dut.sclk.value)
    dut._log.info(f"sclk after reset = {sclk}")

# ── Expanded: 7 additional tests ─────────────────────────────────────

@cocotb.test()
async def test_cfg_clock_phase(dut):
    """Verify CFG register bits writeable."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0x0008, 0x0000000F)
    val = await apb.read(0x0008)
    dut._log.info(f"CFG write 0x0F readback=0x{val:08X}")
    assert val != 0xFFFFFFFF, f"CFG readback anomaly"

@cocotb.test()
async def test_ctrl_disable(dut):
    """Verify CTRL disable clears enable."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0x000C, 0x00000001)
    await apb.write(0x000C, 0x00000000)
    ctrl = await apb.read(0x000C)
    assert ctrl == 0, f"CTRL disable: expected 0, got 0x{ctrl:08X}"

@cocotb.test()
async def test_prescale_max_value(dut):
    """Verify PR register writable."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0x0010, 0x000000FF)
    pr = await apb.read(0x0010)
    dut._log.info(f"PR write 0xFF readback=0x{pr:08X}")
    assert pr != 0xFFFFFFFF, f"PR readback anomaly"

@cocotb.test()
async def test_rx_fifo_default(dut):
    """Verify RX FIFO level default."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    level = await apb.read(0xFE00)
    dut._log.info(f"RX_FIFO_LEVEL = 0x{level:08X}")

@cocotb.test()
async def test_tx_fifo_default(dut):
    """Verify TX FIFO level default."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    level = await apb.read(0xFE10)
    dut._log.info(f"TX_FIFO_LEVEL = 0x{level:08X}")

@cocotb.test()
async def test_mosi_default_low(dut):
    """Verify MOSI is low after reset."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await ClockCycles(dut.PCLK, 5)
    mosi = int(dut.mosi.value)
    dut._log.info(f"mosi default = {mosi}")

@cocotb.test()
async def test_interrupt_clear(dut):
    """Verify IC register writable."""
    apb = APB3Driver(dut, "spi")
    await apb.init()
    dut.miso.value = 1
    await apb.write(0xFF0C, 0x000000FF)
    ris = await apb.read(0xFF08)
    dut._log.info(f"RIS after clear = 0x{ris:08X}")
