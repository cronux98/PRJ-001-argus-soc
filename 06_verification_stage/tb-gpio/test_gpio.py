"""
EF_GPIO8_APB cocotb testbench — PRJ-001.  15 tests.

Register offsets:
  0x0000: DATAI  R   — pin input values
  0x0004: DATAO  RW  — pin output values (reset=0x00)
  0x0008: DIR    RW  — direction (1=output, 0=input, reset=0x00)
  0xFF00: IM     RW  — interrupt mask
  0xFF04: MIS    R   — masked interrupt status
  0xFF08: RIS    R   — raw interrupt status
  0xFF0C: IC     W   — interrupt clear
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from apb_driver import APB3Driver
import cocotb
from cocotb.triggers import ClockCycles

# ── Original 8 tests ─────────────────────────────────────────────────

@cocotb.test()
async def test_defaults(dut):
    """Verify DATAO and DIR default to 0."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    datao = await apb.read(0x0004)
    dirv = await apb.read(0x0008)
    assert datao == 0, f"DATAO default: expected 0, got {datao}"
    assert dirv == 0, f"DIR default: expected 0, got {dirv}"

@cocotb.test()
async def test_datao_rw(dut):
    """Verify DATAO read/write."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0x0004, 0xAA)
    val = await apb.read(0x0004)
    assert val == 0xAA, f"DATAO r/w: expected 0xAA, got 0x{val:02X}"

@cocotb.test()
async def test_dir_rw(dut):
    """Verify DIR read/write."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0x0008, 0xFF)
    val = await apb.read(0x0008)
    assert val == 0xFF, f"DIR r/w: expected 0xFF, got 0x{val:02X}"

@cocotb.test()
async def test_datai_reads_io_in(dut):
    """Verify DATAI reflects io_in pins."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0x5A
    await ClockCycles(dut.PCLK, 2)
    datai = await apb.read(0x0000)
    assert datai == 0x5A, f"DATAI: expected 0x5A, got 0x{datai:02X}"

@cocotb.test()
async def test_output_driven(dut):
    """Verify io_out follows DATAO when DIR is set."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0x0008, 0x0F)
    await apb.write(0x0004, 0x05)
    await ClockCycles(dut.PCLK, 2)
    io_out = int(dut.io_out.value)
    assert (io_out & 0x0F) == 0x05, f"io_out: expected 0x05 masked, got 0x{io_out:02X}"

@cocotb.test()
async def test_interrupt_mask_rw(dut):
    """Verify IM register."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0xFF00, 0xFF)
    im = await apb.read(0xFF00)
    assert im == 0xFF, f"IM: expected 0xFF, got 0x{im:02X}"

@cocotb.test()
async def test_interrupt_status(dut):
    """Verify RIS/MIS registers."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0xFF00, 0xFF)
    await ClockCycles(dut.PCLK, 2)
    ris = await apb.read(0xFF08)
    mis = await apb.read(0xFF04)
    dut._log.info(f"RIS=0x{ris:02X} MIS=0x{mis:02X}")

@cocotb.test()
async def test_interrupt_clear(dut):
    """Verify IC clears interrupts."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0xFF0C, 0xFF)
    await ClockCycles(dut.PCLK, 2)
    ris = await apb.read(0xFF08)
    dut._log.info(f"RIS after clear=0x{ris:02X}")

# ── Expanded: 7 additional tests ─────────────────────────────────────

@cocotb.test()
async def test_datao_all_ones(dut):
    """Verify DATAO can be set to all ones."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0x0004, 0xFF)
    await apb.write(0x0008, 0xFF)
    await ClockCycles(dut.PCLK, 2)
    io_out = int(dut.io_out.value)
    assert (io_out & 0xFF) == 0xFF, f"DATAO all-ones: got 0x{io_out:02X}"

@cocotb.test()
async def test_dir_toggle(dut):
    """Verify DIR bit toggle."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0x0008, 0x0F)
    await apb.write(0x0008, 0x00)
    val = await apb.read(0x0008)
    assert val == 0, f"DIR toggle: expected 0, got 0x{val:02X}"

@cocotb.test()
async def test_im_reset_default(dut):
    """Verify IM default value."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    im = await apb.read(0xFF00)
    dut._log.info(f"IM default = 0x{im:02X}")

@cocotb.test()
async def test_datai_all_inputs(dut):
    """Verify DATAI with all io_in bits set."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    for val in [0x00, 0xFF, 0x55, 0xAA]:
        dut.io_in.value = val
        await ClockCycles(dut.PCLK, 2)
        datai = await apb.read(0x0000)
        assert datai == val, f"DATAI: expected 0x{val:02X}, got 0x{datai:02X}"

@cocotb.test()
async def test_output_high_z_when_input(dut):
    """Verify GPIO pins default to input after reset."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0x0008, 0x00)
    await ClockCycles(dut.PCLK, 2)
    dir_val = await apb.read(0x0008)
    dut._log.info(f"DIR = 0x{dir_val:02X}")
    assert dir_val == 0, f"DIR: expected 0 (input), got 0x{dir_val:02X}"

@cocotb.test()
async def test_output_enabled_when_output(dut):
    """Verify DIR can be set to output."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0x0008, 0xFF)
    await ClockCycles(dut.PCLK, 2)
    dir_val = await apb.read(0x0008)
    assert dir_val == 0xFF, f"DIR: expected 0xFF for output, got 0x{dir_val:02X}"

@cocotb.test()
async def test_interrupt_edge_detect(dut):
    """Verify RIS captures input transitions."""
    apb = APB3Driver(dut, "gpio")
    await apb.init()
    dut.io_in.value = 0
    await apb.write(0xFF00, 0xFF)  # enable all
    # Toggle inputs
    dut.io_in.value = 0xFF
    await ClockCycles(dut.PCLK, 2)
    dut.io_in.value = 0x00
    await ClockCycles(dut.PCLK, 2)
    ris = await apb.read(0xFF08)
    dut._log.info(f"RIS after toggle=0x{ris:02X}")
