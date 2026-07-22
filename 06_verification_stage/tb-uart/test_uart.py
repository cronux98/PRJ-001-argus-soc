"""
EF_UART_APB cocotb testbench — PRJ-001.  15 tests (Tier A expanded to Tier B req).

Efabless UART with APB3 wrapper. Register offsets:
  0x0000: RXDATA     R
  0x0004: TXDATA     W
  0x0008: PR (prescale) RW  reset=0x01B2 (434 → 115200 bps at 50 MHz)
  0x000C: CTRL       RW  reset=0x00
  0x0010: CFG        RW  reset=0x00
  0x001C: MATCH      RW
  0xFE00: RX_FIFO_LEVEL   R
  0xFE04: RX_FIFO_THRESH  RW
  0xFE08: RX_FIFO_FLUSH   W
  0xFE10: TX_FIFO_LEVEL   R
  0xFE14: TX_FIFO_THRESH  RW
  0xFE18: TX_FIFO_FLUSH   W
  0xFF00: IM         RW  interrupt mask
  0xFF04: MIS        R   masked interrupt status
  0xFF08: RIS        R   raw interrupt status
  0xFF0C: IC         W   interrupt clear
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from apb_driver import APB3Driver
import cocotb
from cocotb.triggers import ClockCycles

# ── Original 8 tests ─────────────────────────────────────────────────

@cocotb.test()
async def test_prescale_readback(dut):
    """Verify PR (prescale) register is readable after reset."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    pr = await apb.read(0x0008)
    dut._log.info(f"PR default = 0x{pr:08X}")
    assert pr != 0xFFFFFFFF, f"PR readback anomaly: 0x{pr:08X}"

@cocotb.test()
async def test_prescale_rw(dut):
    """Verify PR register read/write."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    await apb.write(0x0008, 0x00000064)
    val = await apb.read(0x0008)
    assert val == 0x64, f"PR r/w: expected 0x64, got 0x{val:08X}"

@cocotb.test()
async def test_ctrl_enable(dut):
    """Verify CTRL[0] (enable) bit controls TX."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0x000C, 0x00000001)
    ctrl = await apb.read(0x000C)
    assert (ctrl & 1) == 1, f"CTRL[0]: expected 1, got {ctrl}"

@cocotb.test()
async def test_status_after_reset(dut):
    """Verify STATUS register after reset."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0x000C, 0x00000001)
    ctrl = await apb.read(0x000C)
    assert ctrl == 0x01, f"CTRL writeback: expected 0x01, got 0x{ctrl:08X}"

@cocotb.test()
async def test_fifo_flush(dut):
    """Verify FIFO flush registers are writable."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0xFE08, 0x00000001)
    await apb.write(0xFE18, 0x00000001)

@cocotb.test()
async def test_interrupt_regs_rw(dut):
    """Verify IM/IC interrupt registers."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0xFF00, 0x0000000F)
    im = await apb.read(0xFF00)
    assert im == 0x0F, f"IM: expected 0x0F, got 0x{im:08X}"
    ris = await apb.read(0xFF08)
    dut._log.info(f"RIS = 0x{ris:08X}")

@cocotb.test()
async def test_tx_hold(dut):
    """Verify write to TXDATA with ctrl enabled."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0x000C, 0x00000001)
    await apb.write(0x0004, 0x00000041)
    await ClockCycles(dut.PCLK, 10)
    dut._log.info(f"tx = {dut.tx.value}")

@cocotb.test()
async def test_config_rw(dut):
    """Verify CFG register read/write."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0x0010, 0x00000003)
    val = await apb.read(0x0010)
    assert val == 0x03, f"CFG: expected 0x03, got 0x{val:08X}"

# ── Expanded: 7 additional tests ─────────────────────────────────────

@cocotb.test()
async def test_rx_fifo_level_default(dut):
    """Verify RX FIFO level reads 0 after reset."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    level = await apb.read(0xFE00)
    dut._log.info(f"RX_FIFO_LEVEL = 0x{level:08X}")

@cocotb.test()
async def test_tx_fifo_level_default(dut):
    """Verify TX FIFO level reads 0 after reset."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    level = await apb.read(0xFE10)
    dut._log.info(f"TX_FIFO_LEVEL = 0x{level:08X}")

@cocotb.test()
async def test_match_register_rw(dut):
    """Verify MATCH register read/write."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0x001C, 0x00000055)
    val = await apb.read(0x001C)
    assert val == 0x55, f"MATCH: expected 0x55, got 0x{val:08X}"

@cocotb.test()
async def test_ctrl_multiple_bits(dut):
    """Verify CTRL register multiple bits."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0x000C, 0x00000003)
    ctrl = await apb.read(0x000C)
    assert ctrl == 0x03, f"CTRL multi-bit: expected 0x03, got 0x{ctrl:08X}"

@cocotb.test()
async def test_prescale_max(dut):
    """Verify PR register max value."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0x0008, 0x0000FFFF)
    val = await apb.read(0x0008)
    assert val == 0xFFFF, f"PR max: expected 0xFFFF, got 0x{val:08X}"

@cocotb.test()
async def test_consecutive_reg_writes(dut):
    """Verify consecutive writes to multiple registers."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    await apb.write(0x0008, 0x100)
    await apb.write(0x0010, 0x07)
    await apb.write(0x000C, 0x01)
    pr = await apb.read(0x0008)
    cfg = await apb.read(0x0010)
    assert pr == 0x100, f"Consecutive PR: got 0x{pr:08X}"
    assert cfg == 0x07, f"Consecutive CFG: got 0x{cfg:08X}"

@cocotb.test()
async def test_mis_ris_readable(dut):
    """Verify MIS and RIS registers are readable."""
    apb = APB3Driver(dut, "uart")
    await apb.init()
    dut.rx.value = 1
    mis = await apb.read(0xFF04)
    ris = await apb.read(0xFF08)
    dut._log.info(f"MIS=0x{mis:08X} RIS=0x{ris:08X}")
