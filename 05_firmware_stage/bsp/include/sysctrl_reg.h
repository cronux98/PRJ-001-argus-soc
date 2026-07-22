/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* System Control Register Map — 0x00010700 */

#ifndef SYSCTRL_REG_H
#define SYSCTRL_REG_H

#include "soc.h"

/* Register Offsets */
#define SYSCTRL_CHIP_ID_OFFSET      0x00
#define SYSCTRL_CLK_DIV_OFFSET      0x04
#define SYSCTRL_RESET_CAUSE_OFFSET  0x08
#define SYSCTRL_SLEEP_CTRL_OFFSET   0x0C

/* Register Addresses */
#define SYSCTRL_CHIP_ID      ((uintptr_t)(SYS_CTRL_BASE + SYSCTRL_CHIP_ID_OFFSET))
#define SYSCTRL_CLK_DIV      ((uintptr_t)(SYS_CTRL_BASE + SYSCTRL_CLK_DIV_OFFSET))
#define SYSCTRL_RESET_CAUSE  ((uintptr_t)(SYS_CTRL_BASE + SYSCTRL_RESET_CAUSE_OFFSET))
#define SYSCTRL_SLEEP_CTRL   ((uintptr_t)(SYS_CTRL_BASE + SYSCTRL_SLEEP_CTRL_OFFSET))

/* SLEEP_CTRL bit definitions */
#define SYSCTRL_SLEEP_ENABLE    (1 << 0)
#define SYSCTRL_WAKE_GPIO       (1 << 1)
#define SYSCTRL_WAKE_TIMER      (1 << 2)

/* Reset cause values */
#define RESET_CAUSE_POR         0
#define RESET_CAUSE_EXTERNAL    1
#define RESET_CAUSE_WATCHDOG    2
#define RESET_CAUSE_SOFTWARE    3

/* Expected CHIP_ID: 'ARGU' in ASCII = 0x41524755 */
#define CHIP_ID_PRJ001         0x41524755

#endif /* SYSCTRL_REG_H */
