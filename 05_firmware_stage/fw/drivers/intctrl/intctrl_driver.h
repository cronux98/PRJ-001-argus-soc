/* intctrl_driver.h — PRJ-001 Interrupt Controller driver
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * 13-source interrupt controller. Aggregates peripheral IRQs
 * into a single CPU IRQ for the Ibex core.
 */

#ifndef INTCTRL_DRIVER_H
#define INTCTRL_DRIVER_H

#include <stdint.h>
#include "intctrl_reg.h"

/* ── Enable/disable specific IRQ source ──────── */
void intctrl_irq_enable(int irq_num, int enable);

/* ── Read pending IRQs ───────────────────────── */
/* Returns bitmask of pending+enabled interrupts */
uint16_t intctrl_irq_pending(void);

/* ── Check if CPU IRQ is asserted ────────────── */
int intctrl_cpu_irq(void);

/* ── Global interrupt enable/disable ─────────── */
static inline void intctrl_global_enable(void) {
    /* Set MIE (Machine Interrupt Enable) in mstatus */
    __asm__ volatile("csrs mstatus, 0x8");  /* mstatus.MIE */
}

static inline void intctrl_global_disable(void) {
    __asm__ volatile("csrc mstatus, 0x8");  /* clear MIE */
}

#endif /* INTCTRL_DRIVER_H */
