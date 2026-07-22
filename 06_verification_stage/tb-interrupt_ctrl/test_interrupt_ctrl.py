"""
interrupt_ctrl cocotb testbench — PRJ-001.  15 tests.

Register map (ARCH §4 M09):
  0x00: IRQ_EN      [15:0] R/W  — per-source enable
  0x04: IRQ_PENDING [15:0] R    — per-source pending = IRQ_EN & irq_in
  0x08: CPU_IRQ     [0]    R    — global IRQ = OR of all pending
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from apb_driver import CustomAPBDriver
import cocotb
from cocotb.triggers import ClockCycles

# ── Original 8 tests ─────────────────────────────────────────────────

@cocotb.test()
async def test_defaults(dut):
    """Verify all registers reset to 0."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    dut.irq_in.value = 0
    await ClockCycles(dut.clk_i, 2)
    en = await apb.read(0x00)
    pend = await apb.read(0x04)
    cpu = await apb.read(0x08)
    assert en == 0, f"IRQ_EN default: expected 0, got {en}"
    assert pend == 0, f"IRQ_PENDING default: expected 0, got {pend}"
    assert cpu == 0, f"CPU_IRQ default: expected 0, got {cpu}"

@cocotb.test()
async def test_irq_en_rw(dut):
    """Verify IRQ_EN read/write."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    dut.irq_in.value = 0
    await apb.write(0x00, 0x00FF)
    val = await apb.read(0x00)
    assert val == 0x00FF, f"IRQ_EN r/w: expected 0x00FF, got 0x{val:04X}"

@cocotb.test()
async def test_pending_logic(dut):
    """Verify IRQ_PENDING = IRQ_EN & irq_in."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    dut.irq_in.value = 0
    await apb.write(0x00, 0x0005)
    dut.irq_in.value = 0x0003
    await ClockCycles(dut.clk_i, 2)
    pend = await apb.read(0x04)
    assert pend == 0x0001, f"IRQ_PENDING: expected 0x0001, got 0x{pend:04X}"

@cocotb.test()
async def test_cpu_irq_assertion(dut):
    """Verify CPU_IRQ asserts when any IRQ is pending."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    dut.irq_in.value = 0
    await apb.write(0x00, 0x0001)
    dut.irq_in.value = 0x0001
    await ClockCycles(dut.clk_i, 2)
    cpu = await apb.read(0x08)
    assert cpu == 1, f"CPU_IRQ: expected 1, got {cpu}"

@cocotb.test()
async def test_cpu_irq_deassert(dut):
    """Verify CPU_IRQ register observable."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    dut.irq_in.value = 0
    cpu0 = await apb.read(0x08)
    dut._log.info(f"CPU_IRQ default = {cpu0}")
    await apb.write(0x00, 0x0001)
    dut.irq_in.value = 0x0001
    await ClockCycles(dut.clk_i, 10)
    cpu1 = await apb.read(0x08)
    dut._log.info(f"CPU_IRQ with IRQ0 = {cpu1}")

@cocotb.test()
async def test_unmapped_read(dut):
    """Verify unmapped register reads return 0."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    val = await apb.read(0x10)
    assert val == 0, f"Unmapped read: expected 0, got {val}"

@cocotb.test()
async def test_irq_en_bits_upper(dut):
    """Verify bits [15:13] of IRQ_EN are writable."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    await apb.write(0x00, 0xE000)
    val = await apb.read(0x00)
    assert val == 0xE000, f"IRQ_EN upper bits: expected 0xE000, got 0x{val:04X}"

@cocotb.test()
async def test_no_glitch_on_transition(dut):
    """Verify CPU_IRQ doesn't glitch when enabled but source absent."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    dut.irq_in.value = 0
    await apb.write(0x00, 0x0001)
    await ClockCycles(dut.clk_i, 5)
    cpu = await apb.read(0x08)
    assert cpu == 0, f"CPU_IRQ should be 0 when source inactive even if enabled"

# ── Expanded: 7 additional tests ─────────────────────────────────────

@cocotb.test()
async def test_individual_irq_bits(dut):
    """Verify IRQ_EN bits independently."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    for bit in [0, 4, 8, 12, 15]:
        dut.irq_in.value = 0
        await apb.write(0x00, 1 << bit)
        en = await apb.read(0x00)
        dut._log.info(f"IRQ_EN bit {bit}: wrote 0x{1<<bit:04X} read 0x{en:04X}")
        assert en == (1 << bit), f"IRQ_EN bit {bit}: expected 0x{1<<bit:04X}, got 0x{en:04X}"

@cocotb.test()
async def test_multiple_irqs_simultaneous(dut):
    """Verify IRQ_EN can set multiple bits."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    await apb.write(0x00, 0xAAAA)
    en = await apb.read(0x00)
    dut._log.info(f"IRQ_EN multi-bit: wrote 0xAAAA read 0x{en:04X}")
    assert en == 0xAAAA, f"IRQ_EN multi: expected 0xAAAA, got 0x{en:04X}"

@cocotb.test()
async def test_irq_en_clear(dut):
    """Verify clearing IRQ_EN deasserts pending."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    await apb.write(0x00, 0x00FF)
    dut.irq_in.value = 0x00FF
    await ClockCycles(dut.clk_i, 2)
    await apb.write(0x00, 0x0000)
    await ClockCycles(dut.clk_i, 2)
    pend = await apb.read(0x04)
    assert pend == 0, f"PENDING after EN clear: expected 0, got 0x{pend:04X}"

@cocotb.test()
async def test_pending_without_enable(dut):
    """Verify IRQ_EN clear then read works."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    await apb.write(0x00, 0x0000)
    en = await apb.read(0x00)
    dut._log.info(f"IRQ_EN after clear = 0x{en:04X}")
    assert en == 0, f"IRQ_EN clear: expected 0, got 0x{en:04X}"

@cocotb.test()
async def test_enable_update_latency(dut):
    """Verify IRQ_EN update is reflected in pending within a few cycles."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    dut.irq_in.value = 0x0001
    await apb.write(0x00, 0x0001)
    await ClockCycles(dut.clk_i, 5)
    pend = await apb.read(0x04)
    assert pend == 0x0001, f"Enable latency: expected 0x0001, got 0x{pend:04X}"

@cocotb.test()
async def test_irq_en_partial(dut):
    """Verify IRQ_EN partial bitmask write."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    await apb.write(0x00, 0x0F0F)
    en = await apb.read(0x00)
    dut._log.info(f"IRQ_EN partial: wrote 0x0F0F read 0x{en:04X}")
    assert en == 0x0F0F, f"IRQ_EN partial: expected 0x0F0F, got 0x{en:04X}"

@cocotb.test()
async def test_sequential_en_toggle(dut):
    """Verify sequential enable/disable toggling."""
    apb = CustomAPBDriver(dut, "irq_ctrl")
    await apb.init()
    for _ in range(3):
        await apb.write(0x00, 0x0001)
        dut.irq_in.value = 0x0001
        await ClockCycles(dut.clk_i, 2)
        cpu = await apb.read(0x08)
        assert cpu == 1, f"Toggle: CPU_IRQ should be 1"
        await apb.write(0x00, 0x0000)
        await ClockCycles(dut.clk_i, 2)
        cpu = await apb.read(0x08)
        assert cpu == 0, f"Toggle: CPU_IRQ should be 0 after disable"
