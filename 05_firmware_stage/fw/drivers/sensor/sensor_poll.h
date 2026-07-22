/* sensor_poll.h — PRJ-001 Sensor Polling Template
 *
 * Reads environmental sensors over I2C/SPI, buffers data, reports via UART.
 * Configurable polling intervals. Demonstrates all peripheral drivers working.
 */

#ifndef SENSOR_POLL_H
#define SENSOR_POLL_H

#include <stdint.h>

/* Maximum number of sensor readings to buffer before reporting */
#define SENSOR_BUFFER_SIZE  16

/* Sensor data structure */
typedef struct {
    uint16_t temperature;   /* raw ADC or degC*100 */
    uint16_t humidity;      /* raw ADC or %RH*100 */
    uint16_t pressure;      /* raw ADC or hPa*100 */
    uint8_t  flags;         /* sensor status / validity flags */
} sensor_data_t;

/* Initialize sensor drivers */
void sensor_init(void);

/* Poll all sensors once, store data */
void sensor_poll(sensor_data_t *data);

/* Report buffered sensor data over UART */
void sensor_report(const sensor_data_t *data);

/* Main sensor polling loop (blocking, at configured intervals) */
void sensor_loop(uint32_t poll_interval_ms);

#endif /* SENSOR_POLL_H */
