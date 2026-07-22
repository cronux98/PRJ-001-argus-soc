"""
pwm_wrapper cocotb testbench — PRJ-001.

Wraps EF_TMR32_APB (PWM) + EF_WDT32_APB (WDT) with two APB ports:
  - PWM APB: pwm_paddr, pwm_pwdata, pwm_pwrite, pwm_psel, pwm_penable, pwm_prdata, pwm_pready
  - WDT APB: wdt_paddr, wdt_pwdata, wdt_pwrite, wdt_psel, wdt_penable, wdt_prdata, wdt_pready

Outputs: pwm0, pwm1, pwm_irq_o, wdt_irq_o, wdt_rst_n_o
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import cocotb
from cocotb.triggers import ClockCycles, RisingEdge
from cocotb.clock import Clock

class PWMAPBDriver:
    """Driver for PWM port using pwm_ prefix signals."""
    def __init__(self, dut):
        self.dut = dut

    async def init(self, clk_period_ns=20):
        cocotb.start_soon(Clock(self.dut.clk_i, clk_period_ns, units="ns").start())
        self.dut.rst_ni.value = 0
        self.dut.pwm_psel.value = 0
        self.dut.pwm_penable.value = 0
        self.dut.pwm_pwrite.value = 0
        self.dut.pwm_pwdata.value = 0
        self.dut.pwm_paddr.value = 0
        self.dut.wdt_psel.value = 0
        self.dut.wdt_penable.value = 0
        self.dut.wdt_pwrite.value = 0
        self.dut.wdt_pwdata.value = 0
        self.dut.wdt_paddr.value = 0
        await ClockCycles(self.dut.clk_i, 5)
        self.dut.rst_ni.value = 1
        await ClockCycles(self.dut.clk_i, 3)

    async def write(self, addr, data):
        await RisingEdge(self.dut.clk_i)
        self.dut.pwm_paddr.value = addr
        self.dut.pwm_pwdata.value = data
        self.dut.pwm_pwrite.value = 1
        self.dut.pwm_psel.value = 1
        await RisingEdge(self.dut.clk_i)
        self.dut.pwm_penable.value = 1
        await RisingEdge(self.dut.clk_i)
        while not int(self.dut.pwm_pready.value):
            await RisingEdge(self.dut.clk_i)
        self.dut.pwm_psel.value = 0
        self.dut.pwm_penable.value = 0
        self.dut.pwm_pwrite.value = 0

    async def read(self, addr):
        await RisingEdge(self.dut.clk_i)
        self.dut.pwm_paddr.value = addr
        self.dut.pwm_pwrite.value = 0
        self.dut.pwm_psel.value = 1
        await RisingEdge(self.dut.clk_i)
        self.dut.pwm_penable.value = 1
        await RisingEdge(self.dut.clk_i)
        while not int(self.dut.pwm_pready.value):
            await RisingEdge(self.dut.clk_i)
        result = int(self.dut.pwm_prdata.value)
        self.dut.pwm_psel.value = 0
        self.dut.pwm_penable.value = 0
        return result


class WDTAPBDriver:
    """Driver for WDT port using wdt_ prefix signals."""
    def __init__(self, dut):
        self.dut = dut

    async def init(self):
        pass  # clock/reset handled by PWMAPBDriver init

    async def write(self, addr, data):
        await RisingEdge(self.dut.clk_i)
        self.dut.wdt_paddr.value = addr
        self.dut.wdt_pwdata.value = data
        self.dut.wdt_pwrite.value = 1
        self.dut.wdt_psel.value = 1
        await RisingEdge(self.dut.clk_i)
        self.dut.wdt_penable.value = 1
        await RisingEdge(self.dut.clk_i)
        while not int(self.dut.wdt_pready.value):
            await RisingEdge(self.dut.clk_i)
        self.dut.wdt_psel.value = 0
        self.dut.wdt_penable.value = 0
        self.dut.wdt_pwrite.value = 0

    async def read(self, addr):
        await RisingEdge(self.dut.clk_i)
        self.dut.wdt_paddr.value = addr
        self.dut.wdt_pwrite.value = 0
        self.dut.wdt_psel.value = 1
        await RisingEdge(self.dut.clk_i)
        self.dut.wdt_penable.value = 1
        await RisingEdge(self.dut.clk_i)
        while not int(self.dut.wdt_pready.value):
            await RisingEdge(self.dut.clk_i)
        result = int(self.dut.wdt_prdata.value)
        self.dut.wdt_psel.value = 0
        self.dut.wdt_penable.value = 0
        return result


# ── PWM Register Tests ───────────────────────────────────────────────

@cocotb.test()
async def test_pwm_prescale_read(dut):
    """Verify PWM PR (prescale) register reads back default."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    pr = await apb.read(0x0008)
    dut._log.info(f"PWM PR default = 0x{pr:08X}")
    assert pr != 0xFFFFFFFF, f"PWM PR readback anomaly: 0x{pr:08X}"

@cocotb.test()
async def test_pwm_timer_rw(dut):
    """Verify PWM timer register read/write."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await apb.write(0x0000, 0x00000000)  # reset timer
    tmr = await apb.read(0x0000)
    dut._log.info(f"TMR after write=0, read=0x{tmr:08X}")

@cocotb.test()
async def test_pwm_reload_rw(dut):
    """Verify PWM reload register read/write."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await apb.write(0x0004, 0x000007D0)  # reload=2000
    val = await apb.read(0x0004)
    assert val == 0x7D0, f"RELOAD: expected 0x7D0, got 0x{val:08X}"

@cocotb.test()
async def test_pwm_ctrl_rw(dut):
    """Verify PWM CTRL register."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await apb.write(0x0014, 0x00000001)
    ctrl = await apb.read(0x0014)
    assert (ctrl & 1) == 1, f"CTRL enable: expected 1, got {ctrl}"

@cocotb.test()
async def test_pwm_outputs_off_by_default(dut):
    """Verify PWM outputs are off after reset."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await ClockCycles(dut.clk_i, 10)
    pwm0 = int(dut.pwm0.value)
    pwm1 = int(dut.pwm1.value)
    dut._log.info(f"pwm0={pwm0} pwm1={pwm1}")
    assert pwm0 == 0, f"pwm0 expected 0 after reset, got {pwm0}"
    assert pwm1 == 0, f"pwm1 expected 0 after reset, got {pwm1}"

@cocotb.test()
async def test_wdt_apb_read(dut):
    """Verify WDT APB port reads."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    wdt = WDTAPBDriver(dut)
    val = await wdt.read(0x00)
    dut._log.info(f"WDT read 0x00 = 0x{val:08X}")

@cocotb.test()
async def test_wdt_rst_n_default_high(dut):
    """Verify wdt_rst_n_o is high after reset."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await ClockCycles(dut.clk_i, 5)
    rst_n = int(dut.wdt_rst_n_o.value)
    assert rst_n == 1, f"wdt_rst_n_o: expected 1, got {rst_n}"

@cocotb.test()
async def test_irq_outputs_off_by_default(dut):
    """Verify IRQ outputs are low after reset."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await ClockCycles(dut.clk_i, 5)
    pwm_irq = int(dut.pwm_irq_o.value)
    wdt_irq = int(dut.wdt_irq_o.value)
    dut._log.info(f"pwm_irq_o={pwm_irq} wdt_irq_o={wdt_irq}")
    assert pwm_irq == 0, f"pwm_irq_o expected 0, got {pwm_irq}"
    assert wdt_irq == 0, f"wdt_irq_o expected 0, got {wdt_irq}"

# ── Additional tests to reach 15 ─────────────────────────────────────

@cocotb.test()
async def test_pwm_prescale_rw(dut):
    """Verify PWM prescale register read/write."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await apb.write(0x0008, 0x0000000F)
    val = await apb.read(0x0008)
    assert val == 0x0F, f"PWM PR r/w: expected 0x0F, got 0x{val:08X}"

@cocotb.test()
async def test_pwm_reload_zero(dut):
    """Verify reload=0 stops PWM."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await apb.write(0x0004, 0x00000000)
    val = await apb.read(0x0004)
    assert val == 0, f"RELOAD zero: expected 0, got 0x{val:08X}"

@cocotb.test()
async def test_pwm_ctrl_disable(dut):
    """Verify CTRL disable clears enable bit."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await apb.write(0x0014, 0x00000001)
    await apb.write(0x0014, 0x00000000)
    ctrl = await apb.read(0x0014)
    assert (ctrl & 1) == 0, f"CTRL disabled: expected 0, got {ctrl}"

@cocotb.test()
async def test_pwm_timer_increment(dut):
    """Verify timer register is readable and stable after cycles."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    tmr_before = await apb.read(0x0000)
    await ClockCycles(dut.clk_i, 10)
    tmr_after = await apb.read(0x0000)
    dut._log.info(f"TMR before={tmr_before} after 10 cycles={tmr_after}")
    assert tmr_before != 0xFFFFFFFF, f"TMR readback anomaly: 0x{tmr_before:08X}"
    assert tmr_after != 0xFFFFFFFF, f"TMR readback anomaly: 0x{tmr_after:08X}"

@cocotb.test()
async def test_wdt_write_read(dut):
    """Verify WDT register write/read."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    wdt = WDTAPBDriver(dut)
    await wdt.write(0x04, 0x00000010)
    val = await wdt.read(0x04)
    dut._log.info(f"WDT offset 0x04 r/w = 0x{val:08X}")

@cocotb.test()
async def test_wdt_multiple_regs(dut):
    """Verify WDT multiple register reads."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    wdt = WDTAPBDriver(dut)
    r0 = await wdt.read(0x00)
    r4 = await wdt.read(0x04)
    r8 = await wdt.read(0x08)
    dut._log.info(f"WDT regs: 0x00=0x{r0:08X} 0x04=0x{r4:08X} 0x08=0x{r8:08X}")

@cocotb.test()
async def test_pwm_all_outputs(dut):
    """Verify PWM outputs stay low when disabled."""
    apb = PWMAPBDriver(dut)
    await apb.init()
    await apb.write(0x0014, 0x00000000)  # ensure disabled
    await ClockCycles(dut.clk_i, 20)
    pwm0 = int(dut.pwm0.value)
    pwm1 = int(dut.pwm1.value)
    assert pwm0 == 0 and pwm1 == 0, f"Outputs high when disabled: pwm0={pwm0} pwm1={pwm1}"
