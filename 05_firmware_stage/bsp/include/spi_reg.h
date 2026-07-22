/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* SPI Register Map — 0x00010100 */

#ifndef SPI_REG_H
#define SPI_REG_H

#include "soc.h"

/* Register Offsets */
#define SPI_TXDATA_OFFSET   0x00
#define SPI_RXDATA_OFFSET   0x04
#define SPI_STATUS_OFFSET   0x08
#define SPI_CONTROL_OFFSET  0x0C
#define SPI_CLK_DIV_OFFSET  0x10

/* Register Addresses */
#define SPI_TXDATA      ((uintptr_t)(SPI_BASE + SPI_TXDATA_OFFSET))
#define SPI_RXDATA      ((uintptr_t)(SPI_BASE + SPI_RXDATA_OFFSET))
#define SPI_STATUS      ((uintptr_t)(SPI_BASE + SPI_STATUS_OFFSET))
#define SPI_CONTROL     ((uintptr_t)(SPI_BASE + SPI_CONTROL_OFFSET))
#define SPI_CLK_DIV     ((uintptr_t)(SPI_BASE + SPI_CLK_DIV_OFFSET))

/* STATUS bit definitions */
#define SPI_STATUS_CPHA     (1 << 5)
#define SPI_STATUS_CPOL     (1 << 4)
#define SPI_STATUS_RX_FULL  (1 << 1)
#define SPI_STATUS_TX_EMPTY (1 << 0)

/* CONTROL bit definitions */
#define SPI_CONTROL_CS_EN   (1 << 4)
#define SPI_CONTROL_CPHA    (1 << 1)
#define SPI_CONTROL_CPOL    (1 << 0)

/* CLK_DIV: minimum 2, SCLK = f_sys / (2 * CLK_DIV) */
#define SPI_CLK_DIV_MIN     2
#define SPI_CLK_DIV_12M5    2   /* 50MHz/(2*2) = 12.5 MHz */
#define SPI_CLK_DIV_1M      25  /* 50MHz/(2*25) = 1 MHz */

#endif /* SPI_REG_H */
