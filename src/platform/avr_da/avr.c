/** \file
 *  \brief This file implements C functions for peripheral control used in avr.py.
 */

#include <avr/io.h>
#define __DELAY_BACKWARD_COMPATIBLE__
#include <util/delay.h>
#include <stdio.h>
#include "avr.h"

#undef __FILE_ID__
#define __FILE_ID__ 0x71


/**
 * \brief Initialize an I/O pin
 */

 void avr_pin_config(uint8_t pin_no, uint8_t config)
 {
    /* split in port and pin */
    PORT_t* port =  &PORTA + (pin_no >> 3); 
    uint8_t pin = pin_no & 0x7;

    if ( config & PINCFG_OUTPUT) 
        port->DIRSET = 1<<pin; // Set  DIRSET to output
    else 
        port->DIRCLR = 1<<pin; // Set  DIRCLR to input
    
    uint8_t ctrl = 0;
    if ( config & PINCFG_INVERT)
        ctrl |= PORT_INVEN_bm ;     
    if ( config & PINCFG_PULLUP)
        ctrl |= PORT_PULLUPEN_bm;     
    if ( config & PINCFG_IOC) 
        ctrl += 3;      // falling edge
    *(&(port->PIN0CTRL) + pin) = ctrl;
}

void avr_pin_set(uint8_t pin_no, uint8_t value)
{
    /* split in port and pin */
    PORT_t* port =  &PORTA + (pin_no >> 3); 
    uint8_t pin = pin_no & 0x7;
    
    if ( value != 0 )
        port->OUTSET = 1<<pin;     // OUT set
    else
        port->OUTCLR = 1<<pin;     // OUT clear
}

bool avr_pin_get(uint8_t pin_no)
{
    /* split in port and pin */
    PORT_t* port =  &PORTA + (pin_no >> 3); 
    uint8_t pin = pin_no & 0x7;
    return port->IN & (1<<pin);    
}

uint32_t avr_spi_config(uint8_t instance, uint8_t mode, uint32_t frequency)
{    
    /* get pointer to SPI instance registers */
    SPI_t *spi = &SPI0+instance;

    /* find best prescaler so that spi_clock < frequency */
    uint32_t spi_clock = F_CPU/4;
    uint8_t  prescaler = 0;
 
    while (spi_clock > frequency) {
        spi_clock /= 4;
        prescaler++;
    }
    if (prescaler >= 3) { 
        prescaler = 3;  // 1:128  is really the best/slowest we can do
        spi_clock = F_CPU/128;
    }
    if (spi_clock*2 <= frequency) {
        prescaler += 8; // CLK*2 feature allows us to find middle points
        spi_clock *= 2;
    }

    spi->CTRLA = (0<<6) + (1<<5) + (prescaler<<1); // MSB, master, CLK*2|PRE, ENABLE
    spi->CTRLB = (mode & 0x03) + 4; // disable slave select in master mode (single master)
    // enable spi port
    spi->CTRLA |= 1;  

    return spi_clock;  // return best freq.  approximation achieved
}

void avr_spi_xfer(uint8_t instance, uint8_t size, uint8_t *pb)
{
    /* get pointer to SPI instance registers */
    SPI_t *spi = &SPI0+instance;

    // perform the transfer
    for(int i=0; i<size; i++) {
        spi->DATA = *pb; // write data
        while( (spi->INTFLAGS & 0x80) == 0); // wait 
        *pb++ = spi->DATA; // read back 
    }

}

/**
 * \brief configure ADC interface
 */
void avr_adc_config(void)
{
    //SAMPNUM NONE; 
	ADC0.CTRLB = 0x00;
    //PRESC DIV12; 
	ADC0.CTRLC = 0x03;
    //INITDLY DLY0; SAMPDLY 0; 
	ADC0.CTRLD = 0x00;
    //WINCM NONE; 
	ADC0.CTRLE = 0x00;
    //DBGRUN disabled; 
	ADC0.DBGCTRL = 0x00;
    //STARTEI disabled; 
	ADC0.EVCTRL = 0x00;
    //WCMP disabled; RESRDY disabled; 
	ADC0.INTCTRL = 0x00;
    //MUXPOS AIN0; 
	ADC0.MUXPOS = 0x00;
    //MUXNEG AIN0; 
	ADC0.MUXNEG = 0x00;
    //SAMPLEN 31; 
	ADC0.SAMPCTRL = 0x1F;
    // Window comparator high threshold 
	ADC0.WINHT = 0x00;
    // Window comparator low threshold 
	ADC0.WINLT = 0x00;
    //RUNSTBY disabled; CONVMODE disabled; LEFTADJ disabled; RESSEL 12BIT; FREERUN disabled; ENABLE enabled; 
	ADC0.CTRLA = 0x01;
    // activate ADC0 VRef and select the 2.048V option
    VREF.ADC0REF = 0x81;
}

uint16_t avr_adc_get(uint8_t channel)
{
	uint16_t res;

    ADC0.CTRLA &= ~ADC_CONVMODE_bm; // single ended
	ADC0.MUXPOS  = channel;         // select channel
	ADC0.COMMAND = ADC_STCONV_bm;   // start

	while ( !(ADC0.INTFLAGS & ADC_RESRDY_bm) );

	res = ADC0.RES;                 // fetch result
	ADC0.INTFLAGS = ADC_RESRDY_bm;  // clar flag
	return res;
}

void avr_tca_config(uint8_t inst, uint16_t period_us, bool out0, bool out1, bool out2) 
{
    TCA_t *tca = &TCA0 + (inst & 1); // TCA0 or TCA1
    /* Set TCA prescaler to div8  Enable TCA interrupt */
    tca->SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV8_gc /* Clock Selection: System Clock / 8 -> 3MHz*/
                | 1 << TCA_SINGLE_ENABLE_bp; /* Module Enable: enabled */

    tca->SINGLE.CTRLB = 0 << TCA_SINGLE_ALUPD_bp /* Auto Lock Update: disabled */
                | 1 << TCA_SINGLE_CMP0EN_bp /* Compare 0 disabled */
                | 1 << TCA_SINGLE_CMP1EN_bp /* Compare 1 disabled */
                | 1 << TCA_SINGLE_CMP2EN_bp /* Compare 2 disabled */
                | TCA_SINGLE_WGMODE_SINGLESLOPE_gc; /* Waveform generation mode: single slope */
    tca->SINGLE.PER = period_us * 3 ; /* 3000 = 1ms period with clock @ 3MHz */
    // TCA0.SINGLE.INTCTRL = 1; /* enable OVF interrupt */

    /* configure TCA MUX ; TODO make mux user configurable
    TCA1 MUX (<<3)
    Value   Name    WO0 WO1 WO2 WO3 WO4 WO5
    ---------------------------------------
    0x0     PORTB   PB0 PB1 PB2 PB3 PB4 PB5
    0x1     PORTC   PC4 PC5 PC6 -   -   -
    0x2     PORTE   PE4 PE5 PE6 -   -   -
    0x3     PORTG   PG0 PG1 PG2 PG3 PG4 PG5

    TCA0 MUX (<<0)
    Value   Name    WO0 WO1 WO2 WO3 WO4 WO5
    ---------------------------------------
    0x0     PORTA   PA0 PA1 PA2 PA3 PA4 PA5
    0x1     PORTB   PB0 PB1 PB2 PB3 PB4 PB5
    0x2     PORTC   PC0 PC1 PC2 PC3 PC4 PC5
    0x3     PORTD   PD0 PD1 PD2 PD3 PD4 PD5
    0x4     PORTE   PE0 PE1 PE2 PE3 PE4 PE5
    0x5     PORTF   PF0 PF1 PF2 PF3 PF4 PF5
    0x6     PORTG   PG0 PG1 PG2 PG3 PG4 PG5
    */
    if (inst == 0) {
        PORTMUX.TCAROUTEA = (PORTMUX.TCAROUTEA & 0xf8) | 2; // TCA0-> PC0-2 
        avr_pin_config(16, PINCFG_OUTPUT);  //pin C0  
        avr_pin_config(17, PINCFG_OUTPUT);  //pin C1 
        avr_pin_config(18, PINCFG_OUTPUT);  //pin C2  
        PORTMUX.TCAROUTEA = (PORTMUX.TCAROUTEA & 0x7) | (0<<3); // TCA1-> PB0-2 
    } else {
        avr_pin_config( 8, PINCFG_OUTPUT);  //pin B0  
        avr_pin_config( 9, PINCFG_OUTPUT);  //pin B1 
        avr_pin_config(10, PINCFG_OUTPUT);  //pin B2  
    }
}

void avr_tca_set(uint8_t inst, uint8_t chan, uint16_t duty_us)
{
    TCA_t *tca = &TCA0 + (inst & 1); // TCA0 or TCA1
    if (chan == 0) tca->SINGLE.CMP0 = duty_us*3;
    if (chan == 1) tca->SINGLE.CMP1 = duty_us*3;
    if (chan == 2) tca->SINGLE.CMP2 = duty_us*3;
}