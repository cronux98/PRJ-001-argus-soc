/* GENERATED-FROM: memory_map.json — DO NOT HAND-EDIT */
/* I2C Register Map — 0x00010200 */

#ifndef I2C_REG_H
#define I2C_REG_H

#include "soc.h"

/* Register Offsets */
#define I2C_DATA_OFFSET         0x00
#define I2C_ADDR_OFFSET         0x04
#define I2C_STATUS_OFFSET       0x08
#define I2C_CONTROL_OFFSET      0x0C
#define I2C_CLK_DIV_LO_OFFSET   0x10
#define I2C_CLK_DIV_HI_OFFSET   0x14

/* Register Addresses */
#define I2C_DATA          ((uintptr_t)(I2C_BASE + I2C_DATA_OFFSET))
#define I2C_ADDR          ((uintptr_t)(I2C_BASE + I2C_ADDR_OFFSET))
#define I2C_STATUS        ((uintptr_t)(I2C_BASE + I2C_STATUS_OFFSET))
#define I2C_CONTROL       ((uintptr_t)(I2C_BASE + I2C_CONTROL_OFFSET))
#define I2C_CLK_DIV_LO    ((uintptr_t)(I2C_BASE + I2C_CLK_DIV_LO_OFFSET))
#define I2C_CLK_DIV_HI    ((uintptr_t)(I2C_BASE + I2C_CLK_DIV_HI_OFFSET))

/* STATUS bit definitions */
#define I2C_STATUS_TRANSFER_DONE  (1 << 4)
#define I2C_STATUS_ARB_LOST       (1 << 3)
#define I2C_STATUS_NACK           (1 << 2)
#define I2C_STATUS_BUSY           (1 << 0)

/* CONTROL bit definitions */
#define I2C_CONTROL_IRQ_EN        (1 << 3)
#define I2C_CONTROL_REPEATED_START (1 << 2)
#define I2C_CONTROL_STOP          (1 << 1)
#define I2C_CONTROL_START         (1 << 0)

/* ADDR bit definitions */
#define I2C_ADDR_RW_BIT           0  /* 0=write, 1=read */

/* Clock dividers for standard/fast mode at 50 MHz */
/* f_SCL = f_sys / (CLK_DIV_LO + CLK_DIV_HI + 2) */
/* 100 kHz: div = 50000000/100000 - 2 = 498 → LO=249, HI=249 */
#define I2C_CLK_100K_LO          249
#define I2C_CLK_100K_HI          249
/* 400 kHz: div = 50000000/400000 - 2 = 123 → LO=61, HI=62 */
#define I2C_CLK_400K_LO          61
#define I2C_CLK_400K_HI          62

#endif /* I2C_REG_H */
