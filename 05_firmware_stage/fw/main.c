/* main.c — PRJ-001 (Argus) Environmental Sensor-Hub SoC
 *
 * Minimal firmware entry point. Initializes peripherals, runs a brief
 * register-readback self-test, then enters the sensor polling loop.
 * Targets 4KB SRAM budget.
 */

#include "uart_driver.h"
#include "i2c_driver.h"
#include "spi_driver.h"
#include "gpio_driver.h"
#include "pwm_driver.h"
#include "watchdog_driver.h"
#include "sysctrl_driver.h"
#include "intctrl_driver.h"
#include "sensor_poll.h"

/* Quick self-test: verify chip ID and key peripheral registers */
static int quick_test(void) {
    uint32_t id = sysctrl_chip_id();
    if (id != CHIP_ID_PRJ001) return -1;

    /* Verify UART STATUS register has TX_EMPTY bit set */
    volatile uint32_t *uart_st = (volatile uint32_t *)UART_STATUS;
    if (!(*uart_st & 0x02)) return -2;

    /* Verify INTCTRL_IRQ_EN is writable */
    volatile uint32_t *irq_en = (volatile uint32_t *)INTCTRL_IRQ_EN;
    *irq_en = 0x0001;
    if ((*irq_en & 0x0001) != 0x0001) return -3;
    *irq_en = 0x0000;

    return 0;
}

int main(void) {
    /* Boot banner (minimal) */
    uart_puts("ARGUS v1\r\n");

    /* Initialize peripherals */
    spi_init(SPI_MODE_0, SPI_CLK_DIV_1M);
    i2c_init(I2C_FAST);
    gpio_init();
    pwm_init(PWM_PERIOD_DEFAULT);
    pwm_enable(0, 1);
    wdt_init(WDT_RELOAD_1S);
    wdt_enable();

    /* Run quick self-test — blink LED pattern on failure */
    int res = quick_test();
    if (res == 0) {
        uart_puts("OK\r\n");
    } else {
        uart_puts("ERR\r\n");
    }

    /* Enable interrupts */
    intctrl_global_enable();
    intctrl_irq_enable(IRQ_UART, 1);
    intctrl_irq_enable(IRQ_GPIO0, 1);
    gpio_irq_configure(0, 1);
    gpio_irq_enable(0, 1);

    /* Enter sensor polling loop */
    sensor_loop(100);
    return 0;
}
