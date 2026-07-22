/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* GPIO Register Map — 0x00010300 */

#ifndef GPIO_REG_H
#define GPIO_REG_H

#include "soc.h"

/* Register Offsets */
#define GPIO_DATA_OUT_OFFSET    0x00
#define GPIO_DATA_IN_OFFSET     0x04
#define GPIO_DIR_OFFSET         0x08
#define GPIO_IRQ_EN_OFFSET      0x0C
#define GPIO_IRQ_EDGE_OFFSET    0x10
#define GPIO_IRQ_STATUS_OFFSET  0x14

/* Register Addresses */
#define GPIO_DATA_OUT     ((uintptr_t)(GPIO_BASE + GPIO_DATA_OUT_OFFSET))
#define GPIO_DATA_IN      ((uintptr_t)(GPIO_BASE + GPIO_DATA_IN_OFFSET))
#define GPIO_DIR          ((uintptr_t)(GPIO_BASE + GPIO_DIR_OFFSET))
#define GPIO_IRQ_EN       ((uintptr_t)(GPIO_BASE + GPIO_IRQ_EN_OFFSET))
#define GPIO_IRQ_EDGE     ((uintptr_t)(GPIO_BASE + GPIO_IRQ_EDGE_OFFSET))
#define GPIO_IRQ_STATUS   ((uintptr_t)(GPIO_BASE + GPIO_IRQ_STATUS_OFFSET))

/* IRQ_EDGE bit definitions */
#define GPIO_IRQ_EDGE_FALLING_SHIFT  8
#define GPIO_IRQ_EDGE_RISING_MASK    0x00FF
#define GPIO_IRQ_EDGE_FALLING_MASK   0xFF00

/* DIR: 1=output, 0=input */
#define GPIO_DIR_OUTPUT(pin)  (1 << (pin))
#define GPIO_DIR_INPUT        0

#endif /* GPIO_REG_H */
