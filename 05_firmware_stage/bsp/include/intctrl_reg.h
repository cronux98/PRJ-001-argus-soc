/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* Interrupt Controller Register Map — 0x00010500 */

#ifndef INTCTRL_REG_H
#define INTCTRL_REG_H

#include "soc.h"

/* Register Offsets */
#define INTCTRL_IRQ_EN_OFFSET       0x00
#define INTCTRL_IRQ_PENDING_OFFSET  0x04
#define INTCTRL_CPU_IRQ_OFFSET      0x08

/* Register Addresses */
#define INTCTRL_IRQ_EN       ((uintptr_t)(INTERRUPT_CTRL_BASE + INTCTRL_IRQ_EN_OFFSET))
#define INTCTRL_IRQ_PENDING  ((uintptr_t)(INTERRUPT_CTRL_BASE + INTCTRL_IRQ_PENDING_OFFSET))
#define INTCTRL_CPU_IRQ      ((uintptr_t)(INTERRUPT_CTRL_BASE + INTCTRL_CPU_IRQ_OFFSET))

/* IRQ_EN / IRQ_PENDING bit definitions */
#define INTCTRL_IRQ_UART    (1 << 0)
#define INTCTRL_IRQ_SPI     (1 << 1)
#define INTCTRL_IRQ_I2C     (1 << 2)
#define INTCTRL_IRQ_GPIO0   (1 << 3)
#define INTCTRL_IRQ_GPIO1   (1 << 4)
#define INTCTRL_IRQ_GPIO2   (1 << 5)
#define INTCTRL_IRQ_GPIO3   (1 << 6)
#define INTCTRL_IRQ_GPIO4   (1 << 7)
#define INTCTRL_IRQ_GPIO5   (1 << 8)
#define INTCTRL_IRQ_GPIO6   (1 << 9)
#define INTCTRL_IRQ_GPIO7   (1 << 10)
#define INTCTRL_IRQ_PWM     (1 << 11)
#define INTCTRL_IRQ_WDT     (1 << 12)

#endif /* INTCTRL_REG_H */
