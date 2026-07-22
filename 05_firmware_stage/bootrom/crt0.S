/* crt0.S — PRJ-001 (Argus) Ibex RV32I boot/startup code
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * Performs:
 *   1. Initialize stack pointer to _stack_top
 *   2. Clear BSS section (_bss_start → _bss_end)
 *   3. Set up trap vector (mtvec → _trap_handler)
 *   4. Jump to main()
 *
 * Boots from SRAM at 0x00000000 (no ROM — firmware loaded by Caravel
 * management SoC via Wishbone bridge before reset deassertion).
 */

.section .text._start
.globl _start
.type _start, @function
_start:
    /* 1. Initialize stack pointer */
    la sp, _stack_top

    /* 2. Clear BSS */
    la t0, _bss_start
    la t1, _bss_end
    bgeu t0, t1, 2f
1:
    sw zero, 0(t0)
    addi t0, t0, 4
    bltu t0, t1, 1b
2:

    /* 3. Set up trap vector (direct mode, mtvec[1:0] = 0b00) */
    la t0, _trap_handler
    csrw mtvec, t0

    /* 4. Jump to main */
    call main

    /* main() returned — infinite loop */
halt:
    wfi
    j halt

/* ── Trap / Interrupt Handler ──────────────────────
 *
 * This is a unified handler for all exceptions and interrupts on Ibex RV32I.
 * The core has one external interrupt line (irq_external_i) from the
 * 13-source interrupt controller (M09). All traps land here.
 *
 * For exceptions (mcause[31] == 0):
 *   - Save context, loop indefinitely (debug halt).
 *
 * For interrupts (mcause[31] == 1):
 *   - Read INTCTRL_IRQ_PENDING to identify source(s)
 *   - Dispatch to per-source handler stub
 *   - Interrupt remains asserted until peripheral condition clears
 */
.section .text
.globl _trap_handler
.type _trap_handler, @function
_trap_handler:
    /* Save caller-saved registers (simplified — save all x1-x31 for safety) */
    addi sp, sp, -128
    sw ra, 0(sp)
    sw t0, 4(sp)
    sw t1, 8(sp)
    sw t2, 12(sp)
    sw t3, 16(sp)
    sw t4, 20(sp)
    sw t5, 24(sp)
    sw t6, 28(sp)
    sw a0, 32(sp)
    sw a1, 36(sp)
    sw a2, 40(sp)
    sw a3, 44(sp)
    sw a4, 48(sp)
    sw a5, 52(sp)
    sw a6, 56(sp)
    sw a7, 60(sp)

    /* Check mcause[31] — 1 = interrupt, 0 = exception */
    csrr t0, mcause
    bltz t0, irq_handler

exception_handler:
    /* Exception — we don't handle these in MVP, just halt */
    /* Stash mepc + mcause for debug */
    csrr t1, mepc
    csrr t2, mcause
    j exception_halt

exception_halt:
    wfi
    j exception_halt

irq_handler:
    /* External interrupt: read INTCTRL_IRQ_PENDING */
    /* INTCTRL_BASE = 0x00010500, IRQ_PENDING offset = 0x04 */
    li t0, 0x00010504
    lhu t1, 0(t0)          /* t1 = pending bits (16-bit, unsigned) */

    /* Dispatch: check each source in priority order */

    /* UART IRQ (bit 0) */
    andi t2, t1, 0x0001
    beqz t2, 1f
    call isr_uart
1:
    /* SPI IRQ (bit 1) */
    andi t2, t1, 0x0002
    beqz t2, 2f
    call isr_spi
2:
    /* I2C IRQ (bit 2) */
    andi t2, t1, 0x0004
    beqz t2, 3f
    call isr_i2c
3:
    /* GPIO[7:0] IRQs (bits 3-10) */
    andi t2, t1, 0x07F8
    beqz t2, 4f
    call isr_gpio
4:
    /* PWM IRQ (bit 11) */
    li t2, 0x0800
    and t2, t2, t1
    beqz t2, 5f
    call isr_pwm
5:
    /* WDT IRQ (bit 12) */
    li t2, 0x1000
    and t2, t2, t1
    beqz t2, irq_done
    call isr_wdt

irq_done:
    /* Restore caller-saved registers */
    lw ra, 0(sp)
    lw t0, 4(sp)
    lw t1, 8(sp)
    lw t2, 12(sp)
    lw t3, 16(sp)
    lw t4, 20(sp)
    lw t5, 24(sp)
    lw t6, 28(sp)
    lw a0, 32(sp)
    lw a1, 36(sp)
    lw a2, 40(sp)
    lw a3, 44(sp)
    lw a4, 48(sp)
    lw a5, 52(sp)
    lw a6, 56(sp)
    lw a7, 60(sp)
    addi sp, sp, 128

    mret

/* ── Weak ISR stubs — overridable by drivers ───── */
.weak isr_uart
isr_uart:
    ret

.weak isr_spi
isr_spi:
    ret

.weak isr_i2c
isr_i2c:
    ret

.weak isr_gpio
isr_gpio:
    ret

.weak isr_pwm
isr_pwm:
    ret

.weak isr_wdt
isr_wdt:
    ret
