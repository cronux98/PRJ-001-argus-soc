/* uart_driver.h — PRJ-001 UART polled-mode driver
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * Full-duplex UART at 115200 bps 8N1, 8-byte TX/RX FIFOs.
 * Polled mode (no interrupts) by default; ISR stub in crt0.S
 * for interrupt-driven operation.
 */

#ifndef UART_DRIVER_H
#define UART_DRIVER_H

#include <stdint.h>
#include "uart_reg.h"

/* ── Initialization ──────────────────────────── */
void uart_init(void);

/* ── Polled TX (blocking) ────────────────────── */
void uart_putc(char c);

/* ── Polled TX string (blocking) ─────────────── */
void uart_puts(const char *s);

/* ── Polled RX (non-blocking) ────────────────── */
/* Returns 1 if byte available, stores in *c. Returns 0 if empty. */
int uart_getc(char *c);

/* ── Polled RX (blocking) ────────────────────── */
char uart_getc_blocking(void);

/* ── TX hex byte (debug) ─────────────────────── */
void uart_puthex8(uint8_t val);

/* ── TX hex 16-bit word (debug) ──────────────── */
void uart_puthex16(uint16_t val);

/* ── TX hex 32-bit word (debug) ──────────────── */
void uart_puthex32(uint32_t val);

/* ── ISR (called from trap handler) ──────────── */
void isr_uart(void);

#endif /* UART_DRIVER_H */
