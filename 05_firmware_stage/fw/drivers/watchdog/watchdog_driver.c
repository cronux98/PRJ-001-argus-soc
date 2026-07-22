/* watchdog_driver.c — PRJ-001 Watchdog driver (minimal) */

#include "watchdog_driver.h"

void wdt_init(uint32_t reload) {
    *(volatile uint32_t *)WDT_RELOAD = reload;
}

void wdt_pet(void) {
    volatile uint32_t *ctrl = (volatile uint32_t *)WDT_CONTROL;
    *ctrl |= WDT_CONTROL_PET;
    *ctrl &= ~WDT_CONTROL_PET;
}

void wdt_enable(void) {
    *(volatile uint32_t *)WDT_CONTROL |= WDT_CONTROL_ENABLE;
}

void wdt_disable(void) {
    *(volatile uint32_t *)WDT_CONTROL &= ~WDT_CONTROL_ENABLE;
}

void isr_wdt(void) { wdt_pet(); }
