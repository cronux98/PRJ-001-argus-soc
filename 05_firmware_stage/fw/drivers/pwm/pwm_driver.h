/* pwm_driver.h — PRJ-001 PWM driver
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * 2-channel PWM, 10-bit resolution, 1-25 kHz base frequency.
 * Derived from fossi-ef-tmr32.
 */

#ifndef PWM_DRIVER_H
#define PWM_DRIVER_H

#include <stdint.h>
#include "pwm_reg.h"

/* ── Initialization ──────────────────────────── */
/* period: clock cycles per PWM period (2000 → 25 kHz at 50 MHz) */
void pwm_init(uint16_t period);

/* ── Set duty cycle for channel ──────────────── */
/* duty: 0-1023 (10-bit), 0=always low, 1023=always high */
void pwm_set_duty(int channel, uint16_t duty);

/* ── Enable/disable channel ──────────────────── */
void pwm_enable(int channel, int enable);

/* ── ISR (called from trap handler) ──────────── */
void isr_pwm(void);

#endif /* PWM_DRIVER_H */
