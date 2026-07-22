/* spi_driver.c — PRJ-001 SPI master driver (minimal)
 *
 * EF_SPI, Mode 0/3, SCLK = f_sys / (2 * CLK_DIV).
 */

#include "spi_driver.h"

void spi_init(uint8_t mode, uint8_t clk_div) {
    volatile uint32_t *ctrl    = (volatile uint32_t *)SPI_CONTROL;
    volatile uint32_t *clk_reg = (volatile uint32_t *)SPI_CLK_DIV;
    *clk_reg = (clk_div < SPI_CLK_DIV_MIN) ? SPI_CLK_DIV_MIN : clk_div;
    uint32_t v = SPI_CONTROL_CS_EN;
    if (mode & 0x01) v |= SPI_CONTROL_CPHA;
    if (mode & 0x02) v |= SPI_CONTROL_CPOL;
    *ctrl = v;
}

uint8_t spi_transfer(uint8_t tx_byte) {
    volatile uint32_t *st = (volatile uint32_t *)SPI_STATUS;
    while (!(*st & SPI_STATUS_TX_EMPTY)) {}
    *(volatile uint8_t *)SPI_TXDATA = tx_byte;
    while (!(*st & SPI_STATUS_RX_FULL)) {}
    return *(volatile uint8_t *)SPI_RXDATA;
}

void spi_transfer_burst(const uint8_t *tx_buf, uint8_t *rx_buf, int len) {
    for (int i = 0; i < len; i++) {
        uint8_t rx = spi_transfer(tx_buf ? tx_buf[i] : 0x00);
        if (rx_buf) rx_buf[i] = rx;
    }
}

void isr_spi(void) {}
