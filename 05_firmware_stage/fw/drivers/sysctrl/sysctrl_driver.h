/* sysctrl_driver.h — PRJ-001 System Control driver
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * Chip ID, clock divider, reset cause, sleep control.
 */

#ifndef SYSCTRL_DRIVER_H
#define SYSCTRL_DRIVER_H

#include <stdint.h>
#include "sysctrl_reg.h"

/* ── Read Chip ID ────────────────────────────── */
uint32_t sysctrl_chip_id(void);

/* ── Read reset cause ────────────────────────── */
uint8_t sysctrl_reset_cause(void);

/* ── Set system clock divider ────────────────── */
void sysctrl_set_clk_div(uint8_t div);

/* ── Sleep control ───────────────────────────── */
void sysctrl_sleep(void);

#endif /* SYSCTRL_DRIVER_H */
