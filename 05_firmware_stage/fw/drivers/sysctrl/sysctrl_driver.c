/* sysctrl_driver.c — PRJ-001 System Control driver (minimal) */

#include "sysctrl_driver.h"

uint32_t sysctrl_chip_id(void) {
    return *(volatile uint32_t *)SYSCTRL_CHIP_ID;
}

uint8_t sysctrl_reset_cause(void) {
    return *(volatile uint32_t *)SYSCTRL_RESET_CAUSE & 0xFF;
}

void sysctrl_set_clk_div(uint8_t div) {
    *(volatile uint32_t *)SYSCTRL_CLK_DIV = div;
}

void sysctrl_sleep(void) {
    *(volatile uint32_t *)SYSCTRL_SLEEP_CTRL = SYSCTRL_SLEEP_ENABLE;
    __asm__ volatile("wfi");
}
