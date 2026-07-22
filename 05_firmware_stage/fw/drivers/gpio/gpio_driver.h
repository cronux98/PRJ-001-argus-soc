/* gpio_driver.h — PRJ-001 GPIO driver
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * 8-pin GPIO with per-pin direction, interrupt enable/edge/status.
 */

#ifndef GPIO_DRIVER_H
#define GPIO_DRIVER_H

#include <stdint.h>
#include "gpio_reg.h"

/* ── Initialization ──────────────────────────── */
void gpio_init(void);

/* ── Set pin direction (0=input, 1=output) ───── */
void gpio_set_direction(int pin, int is_output);

/* ── Write output pin ────────────────────────── */
void gpio_write(int pin, int value);

/* ── Read input pin ──────────────────────────── */
int gpio_read(int pin);

/* ── Configure interrupt edge ────────────────── */
/* edge: 0=none, 1=rising, 2=falling, 3=both */
void gpio_irq_configure(int pin, int edge);

/* ── Enable/disable interrupt ────────────────── */
void gpio_irq_enable(int pin, int enable);

/* ── Get and clear interrupt status ──────────── */
/* Returns bitmask of pending IRQs. Write 1 to clear bits. */
uint8_t gpio_irq_status(void);

/* ── Clear specific IRQ ──────────────────────── */
void gpio_irq_clear(int pin);

/* ── ISR (called from trap handler) ──────────── */
void isr_gpio(void);

#endif /* GPIO_DRIVER_H */
