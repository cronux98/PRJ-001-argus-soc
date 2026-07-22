/* i2c_driver.h — PRJ-001 I2C master polled-mode driver
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * I2C master, 100/400 kHz, 7-bit addressing.
 * Multi-byte read/write with repeated start support.
 */

#ifndef I2C_DRIVER_H
#define I2C_DRIVER_H

#include <stdint.h>
#include "i2c_reg.h"

/* I2C speed modes */
#define I2C_STANDARD  100000
#define I2C_FAST      400000

typedef enum {
    I2C_OK = 0,
    I2C_ERR_NACK_ADDR = -1,
    I2C_ERR_NACK_DATA = -2,
    I2C_ERR_ARB_LOST  = -3,
    I2C_ERR_BUSY      = -4
} i2c_result_t;

/* ── Initialization ──────────────────────────── */
/* speed: I2C_STANDARD (100k) or I2C_FAST (400k) */
void i2c_init(uint32_t speed);

/* ── Write register (addr: 7-bit, reg: register address, data: value) ── */
i2c_result_t i2c_write_reg(uint8_t addr, uint8_t reg, uint8_t data);

/* ── Read register ───────────────────────────── */
i2c_result_t i2c_read_reg(uint8_t addr, uint8_t reg, uint8_t *data);

/* ── Read multiple registers (burst) ─────────── */
i2c_result_t i2c_read_burst(uint8_t addr, uint8_t start_reg, uint8_t *buf, int len);

/* ── ISR (called from trap handler) ──────────── */
void isr_i2c(void);

#endif /* I2C_DRIVER_H */
