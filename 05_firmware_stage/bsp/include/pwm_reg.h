/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* PWM Register Map — 0x00010400 */

#ifndef PWM_REG_H
#define PWM_REG_H

#include "soc.h"

/* Register Offsets */
#define PWM_PERIOD_OFFSET    0x00
#define PWM_DUTY_CH0_OFFSET  0x04
#define PWM_DUTY_CH1_OFFSET  0x08
#define PWM_CONTROL_OFFSET   0x0C

/* Register Addresses */
#define PWM_PERIOD      ((uintptr_t)(PWM_BASE + PWM_PERIOD_OFFSET))
#define PWM_DUTY_CH0    ((uintptr_t)(PWM_BASE + PWM_DUTY_CH0_OFFSET))
#define PWM_DUTY_CH1    ((uintptr_t)(PWM_BASE + PWM_DUTY_CH1_OFFSET))
#define PWM_CONTROL     ((uintptr_t)(PWM_BASE + PWM_CONTROL_OFFSET))

/* CONTROL bit definitions */
#define PWM_CONTROL_CH0_ENABLE  (1 << 0)
#define PWM_CONTROL_CH1_ENABLE  (1 << 1)

/* Default period for 25 kHz at 50 MHz: 50M/25000 = 2000 */
#define PWM_PERIOD_DEFAULT  2000
#define PWM_MAX_DUTY        1023

#endif /* PWM_REG_H */
