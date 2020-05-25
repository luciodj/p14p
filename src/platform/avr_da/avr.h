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

uint32_t avr_spi_config(uint8_t inst, uint8_t mode, uint32_t frequency);
void avr_spi_xfer(uint8_t inst, uint8_t size, uint8_t *pb);

void avr_adc_config(void);
uint16_t avr_adc_get(uint8_t channel);

void avr_tca_set(uint8_t inst, uint8_t chan, uint16_t duty_us);
void avr_tca_config(uint8_t inst, uint16_t period_us, bool out0, bool out1, bool out2);

void avr_twi_config(uint8_t inst, uint8_t mode, uint8_t alt);
uint8_t avr_twi_write(uint8_t inst, uint8_t address, uint8_t *buffer, uint8_t len);
uint8_t avr_twi_read(uint8_t inst, uint8_t address, uint8_t *buffer, uint8_t len);
uint8_t avr_smb_read(uint8_t inst, uint8_t address, uint8_t reg, uint8_t *value, uint8_t len);
uint8_t avr_smb_write(uint8_t inst, uint8_t address, uint8_t reg, uint8_t *value, uint8_t len);
