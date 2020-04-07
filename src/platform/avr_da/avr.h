/**
 *  \file avr.h
 *  
 *  \brief This file implements C functions for peripheral control used in avr.py
 */

#include <stdbool.h>

#define PINCFG_OUTPUT       1
#define PINCFG_START_HIGH   2
#define PINCFG_INVERT       4
#define PINCFG_PULLUP       8
#define PINCFG_IOC         16


void avr_pin_config(uint8_t pin_no, uint8_t config);
void avr_pin_set(uint8_t pin_no, uint8_t value);
bool avr_pin_get(uint8_t pin_no); 

uint32_t avr_spi_config(uint8_t instance, uint8_t mode, uint32_t frequency);
void avr_spi_xfer(uint8_t instance, uint8_t size, uint8_t *pb);

void avr_adc_config(void);
uint16_t avr_adc_get(uint8_t channel);

void avr_tca_set(uint8_t instance, uint16_t duty_us);
void avr_tca_init(uint16_t period_us, bool out0, bool out1, bool out2);