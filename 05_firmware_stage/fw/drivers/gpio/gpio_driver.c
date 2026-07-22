/* gpio_driver.c — PRJ-001 GPIO driver (minimal) */

#include "gpio_driver.h"

void gpio_init(void) {
    *(volatile uint32_t *)GPIO_DATA_OUT   = 0x00;
    *(volatile uint32_t *)GPIO_DIR        = 0x00;
    *(volatile uint32_t *)GPIO_IRQ_EN     = 0x00;
    *(volatile uint32_t *)GPIO_IRQ_EDGE   = 0x0000;
    *(volatile uint32_t *)GPIO_IRQ_STATUS = 0xFF;
}

void gpio_set_direction(int pin, int is_output) {
    volatile uint32_t *dir = (volatile uint32_t *)GPIO_DIR;
    if (is_output) *dir |= (1 << pin);
    else           *dir &= ~(1 << pin);
}

void gpio_write(int pin, int value) {
    volatile uint32_t *out = (volatile uint32_t *)GPIO_DATA_OUT;
    if (value) *out |= (1 << pin);
    else       *out &= ~(1 << pin);
}

int gpio_read(int pin) {
    return (*(volatile uint32_t *)GPIO_DATA_IN >> pin) & 0x01;
}

void gpio_irq_configure(int pin, int edge) {
    volatile uint32_t *reg = (volatile uint32_t *)GPIO_IRQ_EDGE;
    uint32_t v = *reg;
    v &= ~((1 << pin) | (1 << (pin + 8)));
    if (edge & 0x01) v |= (1 << pin);
    if (edge & 0x02) v |= (1 << (pin + 8));
    *reg = v;
}

void gpio_irq_enable(int pin, int enable) {
    volatile uint32_t *reg = (volatile uint32_t *)GPIO_IRQ_EN;
    if (enable) *reg |= (1 << pin);
    else        *reg &= ~(1 << pin);
}

uint8_t gpio_irq_status(void) {
    return *(volatile uint32_t *)GPIO_IRQ_STATUS & 0xFF;
}

void gpio_irq_clear(int pin) {
    *(volatile uint32_t *)GPIO_IRQ_STATUS = (1 << pin);
}

void isr_gpio(void) {
    uint8_t p = gpio_irq_status();
    *(volatile uint32_t *)GPIO_IRQ_STATUS = p;
}
