/* watchdog_driver.h — PRJ-001 Watchdog Timer driver
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * 24-bit watchdog counter. Pet to prevent timeout reset.
 */

#ifndef WATCHDOG_DRIVER_H
#define WATCHDOG_DRIVER_H

#include <stdint.h>
#include "watchdog_reg.h"

/* ── Initialization ──────────────────────────── */
/* reload: counter reload value (50M → ~1 second at 50 MHz) */
void wdt_init(uint32_t reload);

/* ── Pet / kick the watchdog ─────────────────── */
void wdt_pet(void);

/* ── Enable watchdog ─────────────────────────── */
void wdt_enable(void);

/* ── Disable watchdog ────────────────────────── */
void wdt_disable(void);

/* ── ISR (called from trap handler) ──────────── */
void isr_wdt(void);

#endif /* WATCHDOG_DRIVER_H */
