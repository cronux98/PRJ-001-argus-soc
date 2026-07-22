/* pwm_driver.c — PRJ-001 PWM driver (minimal) */

#include "pwm_driver.h"

void pwm_init(uint16_t period) {
    *(volatile uint32_t *)PWM_PERIOD  = period;
    *(volatile uint32_t *)PWM_CONTROL = 0x00;
}

void pwm_set_duty(int channel, uint16_t duty) {
    if (channel == 0) {
        *(volatile uint32_t *)PWM_DUTY_CH0 = (duty > PWM_MAX_DUTY) ? PWM_MAX_DUTY : duty;
    } else {
        *(volatile uint32_t *)PWM_DUTY_CH1 = (duty > PWM_MAX_DUTY) ? PWM_MAX_DUTY : duty;
    }
}

void pwm_enable(int channel, int enable) {
    volatile uint32_t *ctrl = (volatile uint32_t *)PWM_CONTROL;
    uint32_t mask = (channel == 0) ? PWM_CONTROL_CH0_ENABLE : PWM_CONTROL_CH1_ENABLE;
    if (enable) *ctrl |= mask;
    else        *ctrl &= ~mask;
}

void isr_pwm(void) {}
