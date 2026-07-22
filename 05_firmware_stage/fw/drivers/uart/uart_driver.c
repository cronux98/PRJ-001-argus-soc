/* uart_driver.c — PRJ-001 UART polled-mode driver
 *
 * EF_UART with 8-byte TX/RX FIFOs, 115200 bps 8N1 at 50 MHz.
 * Minimal implementation for 4KB SRAM budget.
 */

#include "uart_driver.h"

static const char hex_chars[] = "0123456789ABCDEF";

void uart_init(void) {
    volatile uint32_t *ctrl = (volatile uint32_t *)UART_CONTROL;
    volatile uint32_t *baud = (volatile uint32_t *)UART_BAUD_DIV;
    *ctrl = UART_CONTROL_TX_ENABLE | UART_CONTROL_RX_ENABLE;
    *baud = UART_BAUD_115200;
}

void uart_putc(char c) {
    volatile uint32_t *status = (volatile uint32_t *)UART_STATUS;
    volatile uint8_t *txdata = (volatile uint8_t *)UART_TXDATA;
    while (*status & UART_STATUS_TX_FULL) {}
    *txdata = (uint8_t)c;
}

void uart_puts(const char *s) {
    while (*s) uart_putc(*s++);
}

int uart_getc(char *c) {
    volatile uint32_t *status = (volatile uint32_t *)UART_STATUS;
    if (*status & UART_STATUS_RX_EMPTY) return 0;
    *c = (char)*(volatile uint8_t *)UART_RXDATA;
    return 1;
}

char uart_getc_blocking(void) {
    volatile uint32_t *status = (volatile uint32_t *)UART_STATUS;
    while (*status & UART_STATUS_RX_EMPTY) {}
    return (char)*(volatile uint8_t *)UART_RXDATA;
}

void uart_puthex8(uint8_t val) {
    uart_putc(hex_chars[(val >> 4) & 0xF]);
    uart_putc(hex_chars[val & 0xF]);
}

void uart_puthex16(uint16_t val) {
    uart_putc(hex_chars[(val >> 12) & 0xF]);
    uart_putc(hex_chars[(val >> 8) & 0xF]);
    uart_putc(hex_chars[(val >> 4) & 0xF]);
    uart_putc(hex_chars[val & 0xF]);
}

void isr_uart(void) {}
