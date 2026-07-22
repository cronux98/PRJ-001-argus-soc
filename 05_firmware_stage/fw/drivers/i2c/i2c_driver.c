/* i2c_driver.c — PRJ-001 I2C master driver (minimal)
 *
 * EF_I2C, byte-level master, 100/400 kHz.
 */

#include "i2c_driver.h"

static i2c_result_t i2c_wait_done(void) {
    volatile uint32_t *st = (volatile uint32_t *)I2C_STATUS;
    while (1) {
        uint32_t s = *st;
        if (s & I2C_STATUS_NACK) return I2C_ERR_NACK_DATA;
        if (s & I2C_STATUS_ARB_LOST) return I2C_ERR_ARB_LOST;
        if (s & I2C_STATUS_TRANSFER_DONE) return I2C_OK;
    }
}

void i2c_init(uint32_t speed) {
    volatile uint32_t *lo = (volatile uint32_t *)I2C_CLK_DIV_LO;
    volatile uint32_t *hi = (volatile uint32_t *)I2C_CLK_DIV_HI;
    if (speed >= I2C_FAST) { *lo = I2C_CLK_400K_LO; *hi = I2C_CLK_400K_HI; }
    else                   { *lo = I2C_CLK_100K_LO; *hi = I2C_CLK_100K_HI; }
}

static i2c_result_t i2c_start(uint8_t addr, int is_read) {
    volatile uint32_t *a = (volatile uint32_t *)I2C_ADDR;
    volatile uint32_t *c = (volatile uint32_t *)I2C_CONTROL;
    *a = (addr << 1) | (is_read ? 1 : 0);
    *c = I2C_CONTROL_START;
    return i2c_wait_done();
}

static void i2c_stop(void) {
    *(volatile uint32_t *)I2C_CONTROL = I2C_CONTROL_STOP;
}

i2c_result_t i2c_write_reg(uint8_t addr, uint8_t reg, uint8_t data) {
    volatile uint32_t *d = (volatile uint32_t *)I2C_DATA;
    volatile uint32_t *c = (volatile uint32_t *)I2C_CONTROL;
    i2c_result_t r;
    r = i2c_start(addr, 0);
    if (r != I2C_OK) { i2c_stop(); return r; }
    *d = reg; *c = I2C_CONTROL_START;
    r = i2c_wait_done();
    if (r != I2C_OK) { i2c_stop(); return I2C_ERR_NACK_DATA; }
    *d = data; *c = I2C_CONTROL_START;
    r = i2c_wait_done();
    i2c_stop();
    return r;
}

i2c_result_t i2c_read_reg(uint8_t addr, uint8_t reg, uint8_t *data) {
    volatile uint32_t *d = (volatile uint32_t *)I2C_DATA;
    volatile uint32_t *c = (volatile uint32_t *)I2C_CONTROL;
    i2c_result_t r;
    r = i2c_start(addr, 0);
    if (r != I2C_OK) { i2c_stop(); return r; }
    *d = reg; *c = I2C_CONTROL_START;
    r = i2c_wait_done();
    if (r != I2C_OK) { i2c_stop(); return r; }
    r = i2c_start(addr, 1);
    if (r != I2C_OK) { i2c_stop(); return r; }
    *c = I2C_CONTROL_START;
    i2c_wait_done();
    *data = (uint8_t)*d;
    i2c_stop();
    return I2C_OK;
}

i2c_result_t i2c_read_burst(uint8_t addr, uint8_t start_reg, uint8_t *buf, int len) {
    for (int i = 0; i < len; i++) {
        i2c_result_t r = i2c_read_reg(addr, start_reg + i, &buf[i]);
        if (r != I2C_OK) return r;
    }
    return I2C_OK;
}

void isr_i2c(void) {}
