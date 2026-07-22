/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* UART Register Map — 0x00010000 */

#ifndef UART_REG_H
#define UART_REG_H

#include "soc.h"

/* Register Offsets */
#define UART_TXDATA_OFFSET      0x00
#define UART_RXDATA_OFFSET      0x04
#define UART_STATUS_OFFSET      0x08
#define UART_CONTROL_OFFSET     0x0C
#define UART_BAUD_DIV_OFFSET    0x10
#define UART_FIFO_THRESH_OFFSET 0x14

/* Register Addresses */
#define UART_TXDATA      ((uintptr_t)(UART_BASE + UART_TXDATA_OFFSET))
#define UART_RXDATA      ((uintptr_t)(UART_BASE + UART_RXDATA_OFFSET))
#define UART_STATUS      ((uintptr_t)(UART_BASE + UART_STATUS_OFFSET))
#define UART_CONTROL     ((uintptr_t)(UART_BASE + UART_CONTROL_OFFSET))
#define UART_BAUD_DIV    ((uintptr_t)(UART_BASE + UART_BAUD_DIV_OFFSET))
#define UART_FIFO_THRESH ((uintptr_t)(UART_BASE + UART_FIFO_THRESH_OFFSET))

/* STATUS bit definitions */
#define UART_STATUS_RX_OVERRUN  (1 << 4)
#define UART_STATUS_RX_EMPTY    (1 << 3)
#define UART_STATUS_RX_FULL     (1 << 2)
#define UART_STATUS_TX_EMPTY    (1 << 1)
#define UART_STATUS_TX_FULL     (1 << 0)

/* CONTROL bit definitions */
#define UART_CONTROL_RX_ENABLE  (1 << 1)
#define UART_CONTROL_TX_ENABLE  (1 << 0)

/* FIFO_THRESH bit definitions */
#define UART_FIFO_RX_THRESH_SHIFT  4
#define UART_FIFO_TX_THRESH_SHIFT  0
#define UART_FIFO_RX_THRESH_MASK   0xF0
#define UART_FIFO_TX_THRESH_MASK   0x0F

/* BAUD_DIV: 434 for 115200 at 50 MHz = 50000000 / 115200 */
#define UART_BAUD_115200    434

#endif /* UART_REG_H */
