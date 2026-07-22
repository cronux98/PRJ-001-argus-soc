/* spi_driver.h — PRJ-001 SPI master polled-mode driver
 *
 * GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT
 *
 * SPI master Mode 0 (CPOL=0, CPHA=0) and Mode 3 (CPOL=1, CPHA=1).
 * Up to 12.5 MHz SCLK (f_sys/4 at 50 MHz).
 */

#ifndef SPI_DRIVER_H
#define SPI_DRIVER_H

#include <stdint.h>
#include "spi_reg.h"

/* SPI modes */
#define SPI_MODE_0  0x00  /* CPOL=0, CPHA=0 */
#define SPI_MODE_3  0x03  /* CPOL=1, CPHA=1 */

/* ── Initialization ──────────────────────────── */
void spi_init(uint8_t mode, uint8_t clk_div);

/* ── Transfer (full-duplex, blocking) ────────── */
/* Sends byte, returns received byte. Asserts CS before, deasserts after. */
uint8_t spi_transfer(uint8_t tx_byte);

/* ── Burst transfer ──────────────────────────── */
/* Sends tx_buf, stores received data in rx_buf. CS held low for entire burst. */
void spi_transfer_burst(const uint8_t *tx_buf, uint8_t *rx_buf, int len);

/* ── ISR (called from trap handler) ──────────── */
void isr_spi(void);

#endif /* SPI_DRIVER_H */
