/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* Watchdog Register Map — 0x00010600 */

#ifndef WATCHDOG_REG_H
#define WATCHDOG_REG_H

#include "soc.h"

/* Register Offsets */
#define WDT_RELOAD_OFFSET   0x00
#define WDT_COUNTER_OFFSET  0x04
#define WDT_CONTROL_OFFSET  0x08

/* Register Addresses */
#define WDT_RELOAD      ((uintptr_t)(WATCHDOG_BASE + WDT_RELOAD_OFFSET))
#define WDT_COUNTER     ((uintptr_t)(WATCHDOG_BASE + WDT_COUNTER_OFFSET))
#define WDT_CONTROL     ((uintptr_t)(WATCHDOG_BASE + WDT_CONTROL_OFFSET))

/* CONTROL bit definitions */
#define WDT_CONTROL_ENABLE      (1 << 0)
#define WDT_CONTROL_PET         (1 << 1)  /* Write 1 to pet/reset counter */

/* Default reload for ~1 second timeout at 50 MHz */
#define WDT_RELOAD_1S  50000000

#endif /* WATCHDOG_REG_H */
