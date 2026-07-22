/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* PRJ-001 (Argus) — Ibex RV32I, 50 MHz, 4KB SRAM */

#ifndef SOC_H
#define SOC_H

#include <stdint.h>

/* ── Core ─────────────────────────────── */
#define CPU_ISA           "rv32i"
#define CLOCK_MHZ         50
#define MTIME_FREQ_HZ     50000000u

/* ── Memory Regions ───────────────────── */
#define SRAM_BASE          0x00000000
#define SRAM_SIZE          4096

#define UART_BASE          0x00010000
#define UART_SIZE          256

#define SPI_BASE           0x00010100
#define SPI_SIZE           256

#define I2C_BASE           0x00010200
#define I2C_SIZE           256

#define GPIO_BASE          0x00010300
#define GPIO_SIZE          256

#define PWM_BASE           0x00010400
#define PWM_SIZE           256

#define INTERRUPT_CTRL_BASE  0x00010500
#define INTERRUPT_CTRL_SIZE  256

#define WATCHDOG_BASE      0x00010600
#define WATCHDOG_SIZE      256

#define SYS_CTRL_BASE      0x00010700
#define SYS_CTRL_SIZE      256

/* ── Peripheral Register Accessors ────── */
#define REG_READ(addr)     (*(volatile uint32_t*)((uintptr_t)(addr)))
#define REG_WRITE(addr,v)  (*(volatile uint32_t*)((uintptr_t)(addr)) = (v))
#define REG_READ8(addr)    (*(volatile uint8_t*)((uintptr_t)(addr)))
#define REG_WRITE8(addr,v) (*(volatile uint8_t*)((uintptr_t)(addr)) = (v))
#define REG_READ16(addr)   (*(volatile uint16_t*)((uintptr_t)(addr)))
#define REG_WRITE16(addr,v) (*(volatile uint16_t*)((uintptr_t)(addr)) = (v))

/* ── Interrupt Sources ────────────────── */
#define IRQ_UART            0
#define IRQ_SPI             1
#define IRQ_I2C             2
#define IRQ_GPIO0           3
#define IRQ_GPIO1           4
#define IRQ_GPIO2           5
#define IRQ_GPIO3           6
#define IRQ_GPIO4           7
#define IRQ_GPIO5           8
#define IRQ_GPIO6           9
#define IRQ_GPIO7           10
#define IRQ_PWM             11
#define IRQ_WDT             12
#define IRQ_COUNT           13

/* ── Bit Manipulation ─────────────────── */
static inline void reg_set(volatile uint32_t *reg, uint32_t mask) {
    REG_WRITE(reg, REG_READ(reg) | mask);
}
static inline void reg_clear(volatile uint32_t *reg, uint32_t mask) {
    REG_WRITE(reg, REG_READ(reg) & ~mask);
}
static inline int reg_field_get(volatile uint32_t *reg, uint32_t mask, int lo) {
    return (REG_READ(reg) & mask) >> lo;
}

#endif /* SOC_H */
