/* sensor_poll.c — PRJ-001 Sensor Polling Template (minimal)
 *
 * I2C/SPI sensor read, UART reporting, PWM fan control.
 * Optimized for 4KB SRAM budget.
 */

#include "sensor_poll.h"
#include "uart_driver.h"
#include "i2c_driver.h"
#include "spi_driver.h"
#include "gpio_driver.h"
#include "pwm_driver.h"
#include "watchdog_driver.h"

/* Simple delay using busy loop (~50000 cycles/ms at 50 MHz) */
static void delay_ms(uint32_t ms) {
    for (uint32_t i = 0; i < ms; i++) {
        for (volatile uint32_t j = 0; j < 50000; j++) {
            __asm__ volatile("nop");
        }
    }
}

void sensor_init(void) {
    uart_puts("INIT\r\n");
    i2c_init(I2C_FAST);
    spi_init(SPI_MODE_0, SPI_CLK_DIV_1M);
    gpio_init();
    pwm_init(PWM_PERIOD_DEFAULT);
    pwm_enable(0, 1);
}

void sensor_poll(sensor_data_t *data) {
    uint8_t buf[6];

    /* I2C: read 3 bytes from addr 0x76 reg 0xFA (temperature) */
    i2c_result_t res = i2c_read_burst(0x76, 0xFA, buf, 3);
    if (res == I2C_OK) {
        data->temperature = ((uint16_t)buf[0] << 8) | buf[1];
        data->flags |= 0x01;
    }

    /* I2C: read 2 bytes from addr 0x76 reg 0xFD (humidity) */
    res = i2c_read_burst(0x76, 0xFD, buf, 2);
    if (res == I2C_OK) {
        data->humidity = ((uint16_t)buf[0] << 8) | buf[1];
        data->flags |= 0x02;
    }

    /* I2C: read 3 bytes from addr 0x76 reg 0xF7 (pressure) */
    res = i2c_read_burst(0x76, 0xF7, buf, 3);
    if (res == I2C_OK) {
        data->pressure = ((uint16_t)buf[0] << 8) | buf[1];
        data->flags |= 0x04;
    }

    /* SPI: dummy read */
    (void)spi_transfer(0x00);

    /* GPIO alert check */
    if (gpio_read(0)) data->flags |= 0x08;
}

void sensor_report(const sensor_data_t *data) {
    if (data->flags & 0x01) {
        uart_puts("T=");
        uart_puthex16(data->temperature);
        uart_putc(' ');
    }
    if (data->flags & 0x02) {
        uart_puts("H=");
        uart_puthex16(data->humidity);
        uart_putc(' ');
    }
    if (data->flags & 0x04) {
        uart_puts("P=");
        uart_puthex16(data->pressure);
        uart_putc(' ');
    }
    uart_puts("\r\n");

    /* Fan control from temperature */
    if (data->flags & 0x01) {
        uint16_t duty = 0;
        if (data->temperature > 0x8000) {
            duty = (data->temperature - 0x8000) / 32;
            if (duty > PWM_MAX_DUTY) duty = PWM_MAX_DUTY;
        }
        pwm_set_duty(0, duty);
    }
}

void sensor_loop(uint32_t poll_interval_ms) {
    sensor_data_t data;
    while (1) {
        data.temperature = 0;
        data.humidity = 0;
        data.pressure = 0;
        data.flags = 0;
        sensor_poll(&data);
        sensor_report(&data);
        wdt_pet();
        delay_ms(poll_interval_ms);
    }
}
