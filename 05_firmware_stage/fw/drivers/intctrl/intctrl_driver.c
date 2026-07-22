/* intctrl_driver.c — PRJ-001 Interrupt Controller driver (minimal) */

#include "intctrl_driver.h"

void intctrl_irq_enable(int irq_num, int enable) {
    if (irq_num < 0 || irq_num >= IRQ_COUNT) return;
    volatile uint32_t *reg = (volatile uint32_t *)INTCTRL_IRQ_EN;
    if (enable) *reg |= (1 << irq_num);
    else        *reg &= ~(1 << irq_num);
}

uint16_t intctrl_irq_pending(void) {
    return *(volatile uint32_t *)INTCTRL_IRQ_PENDING & 0xFFFF;
}

int intctrl_cpu_irq(void) {
    return *(volatile uint32_t *)INTCTRL_CPU_IRQ & 0x01;
}
