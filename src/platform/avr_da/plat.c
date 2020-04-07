/*
# This file is Copyright 2010 Dean Hall.
#
# This file is part of the Python-on-a-Chip program.
# Python-on-a-Chip is free software: you can redistribute it and/or modify
# it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE Version 2.1.
#
# Python-on-a-Chip is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# A copy of the GNU LESSER GENERAL PUBLIC LICENSE Version 2.1
# is seen in the file COPYING up one directory from this.
*/


#undef __FILE_ID__
#define __FILE_ID__ 0x70


/** PyMite platform-specific routines for AVR target */


#include <stdio.h>
#include <string.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <avr/eeprom.h>
#include <stdbool.h>

#define __DELAY_BACKWARD_COMPATIBLE__
#include <util/delay.h>

#include "pm.h"
extern unsigned char const usrlib_img[];

/* adjust depending on RTC-PIT oscillator selected and prescaler applied
 */
#define PLAT_TIME_PER_TICK_USEC (975) // micro seconds between interrupts


/* Configure stdin, stdout, stderr */
static int uart_putc(char c, FILE *stream);
static int uart_getc(FILE *stream);
FILE avr_uart = FDEV_SETUP_STREAM(uart_putc, uart_getc, _FDEV_SETUP_RW);

/* Peripheral definitions - CURIOSITY AVR-DA rev 2 */
#define LED_PIN             PIN_PF5
#define SW0_PIN             PIN_PF6
#define CDC_RX_PIN          PIN_PB1
#define CDC_TX_PIN          PIN_PB0

/* nEDBG CDC Gateway USART interface definitions */
#define CDC_BAUD                9600
#define CDC_UART                USART3      

/*
 * AVR target shall use stdio for I/O routines.
 * The UART or USART must be configured for the interactive interface to work.
 */
PmReturn_t
plat_init(void)
{
    /* CDC UART */
    PORTB.OUTSET = 1<<0; /* RB0 start high */
    PORTB.DIRSET = 1<<0; /* RB0 output */
    PORTB.DIRCLR = 1<<1; /* RB1 input */

    /* unlock Configuration Change Protection */
    CPU_CCP = CCP_IOREG_gc; 
    /* Set the clock speed */
    CLKCTRL.OSCHFCTRLA = 9 << 2; /* 24MHz */

    /* Assign I/Os, direction */
    /* Set LED pin as output */
    PORTF.DIRSET = 1<<5;   /* out */
    PORTF.OUTCLR = 0<<5;   /* LED = on */

	/* Set up the rev 2 SW pin as well */
	PORTF.DIRCLR = 1<<6;    /* in */
    PORTF.PIN6CTRL |= PORT_PULLUPEN_bm; /* pull up */
    // PORTF.PIN6CTRL = PORT_ISC_FALLING_gc | PORT_PULLUPEN_bm; /* enable interrupt on pin */

    /* Set the baud rate register */
	uint32_t cdc_baud = F_CPU * 4;
	cdc_baud = cdc_baud / CDC_BAUD;
	CDC_UART.BAUDH = (cdc_baud>>8) & 0xFF;
	CDC_UART.BAUDL = (cdc_baud) & 0xFF;;
    /* Set mode Async, 8-N-1 */
	CDC_UART.CTRLC = USART_CMODE_ASYNCHRONOUS_gc | USART_PMODE_DISABLED_gc | USART_CHSIZE_8BIT_gc;
    /* Enable the transmit and receive pins */
	CDC_UART.CTRLB = USART_RXEN_bm | USART_TXEN_bm;

    stdin = stdout = stderr = &avr_uart;

    //RTC_SetPITIsrCallback(timeout_isr);
    // Wait for RTC register synchronization
    while (RTC.STATUS > 0);
    RTC.CTRLA &= ~RTC_RTCEN_bm;         // Disable the RTC module

    // Wait for PIT register synchronization
    while (RTC.PITSTATUS > 0);
    RTC.PITCTRLA &= ~RTC_PITEN_bm;      // Disable the PIT module

    // Wait for OSCULP32K to be stable (just in case)
    while (!(CLKCTRL.MCLKSTATUS & CLKCTRL_OSC32KS_bm)); // use internal 32k clock
    // CLKCTRL.XOSC32KCTRLA = CLKCTRL_ENABLE_bm; // enable external 32K clock and mux I/O pins
    // while (!(CLKCTRL.MCLKSTATUS & CLKCTRL_XOSC32KS_bm)); // use external 32k clock

    // Wait for RTC register synchronization
    while (RTC.STATUS > 0);
    RTC.CLKSEL = RTC_CLKSEL_OSC32K_gc;   // select 32kHz mode

    // Wait for PIT register synchronization
    while (RTC.PITSTATUS > 0);
    RTC.PITINTCTRL |= RTC_PI_bm;        

    // Wait for PIT register synchronization
    while (RTC.PITSTATUS > 0);
    RTC.PITCTRLA = RTC_PERIOD_CYC32_gc;  // 4 msec match SCHEDULER_BASE_PERIOD

    // Wait for PIT register synchronization
	while (RTC.PITSTATUS > 0);
    RTC.PITCTRLA |= RTC_PITEN_bm;       // enable PIT function

    /* Global interrupt enable */
    sei();
    return PM_RET_OK;
}


PmReturn_t
plat_deinit(void)
{
    /* Disable UART */
    // UCSR0B &= ~(_BV(TXEN0) | _BV(RXEN0));
	// CDC_UART.CTRLB = USART_RXEN_bm | USART_TXEN_bm;

    /* Disable Timer (clear clock source) */
    // TCCR0B &= ~(_BV(CS02) | _BV(CS01) | _BV(CS00));

    return PM_RET_OK;
}


ISR(TCA0_OVF_vect)
{
    /* TODO Find a clever way to handle bad return code, maybe use
     * PM_REPORT_IF_ERROR(retval) when that works on AVR inside an
     * interrupt.
     */
    pm_vmPeriodic(PLAT_TIME_PER_TICK_USEC);
    TCA0.SINGLE.INTFLAGS = 1; /* clear interrupt flag */
}

ISR(RTC_PIT_vect)
{
    pm_vmPeriodic(PLAT_TIME_PER_TICK_USEC);
    RTC.PITINTFLAGS = RTC_PI_bm; /* clear interrupt flag */
}

/*
 * Gets a byte from the address in the designated memory space
 * Post-increments *paddr.
 */
uint8_t
plat_memGetByte(PmMemSpace_t memspace, uint8_t const **paddr)
{
    uint8_t b = 0;

    switch (memspace)
    {
        case MEMSPACE_RAM:
            b = **paddr;
            *paddr += 1;
            return b;

        case MEMSPACE_PROG:
            b = pgm_read_byte(*paddr);
            *paddr += 1;
            return b;

        case MEMSPACE_EEPROM:
            b = eeprom_read_byte(*paddr);
            *paddr += 1;
            return b;

        case MEMSPACE_SEEPROM:
        case MEMSPACE_OTHER0:
        case MEMSPACE_OTHER1:
        case MEMSPACE_OTHER2:
        case MEMSPACE_OTHER3:
        default:
            return 0;
    }
}

bool uart_is_rx_ready(void)
{
	return (CDC_UART.STATUS & USART_RXCIF_bm) != 0;
}

bool uart_is_tx_ready(void)
{
	return (CDC_UART.STATUS & USART_DREIF_bm) != 0;
}

static int
uart_getc(FILE *stream)
{
    char c;

    /* Wait for reception of a byte */
    while (!uart_is_rx_ready())
        ;
    c = CDC_UART.RXDATAL;

    /* Return errors for Framing error or Overrun */
    // if (UCSR0A & _BV(FE0)) return _FDEV_EOF;
    // if (UCSR0A & _BV(DOR0)) return _FDEV_ERR;

    return c;
}


static int
uart_putc(char c, FILE *stream)
{
    /* Wait until UART can accept the byte */
 	/* Check if the transmitter is ready */
	while (!uart_is_tx_ready())
		;

	/* Send character */
	CDC_UART.TXDATAL = c;

    return 0;
}


/*
 * UART receive char routine MUST return exactly and only the received char;
 * it should not translate \n to \r\n.
 * This is because the interactive interface uses binary transfers.
 */
PmReturn_t
plat_getByte(uint8_t *b)
{
    PmReturn_t retval = PM_RET_OK;

    /* Loop until serial receive is complete */
    while (!uart_is_rx_ready())
        ;

    /* If a framing error or data overrun occur, raise an IOException */
    if (CDC_UART.RXDATAH & (USART_FERR_bm | USART_BUFOVF_bm))
    {
        PM_RAISE(retval, PM_RET_EX_IO);
        return retval;
    }
    char c = CDC_UART.RXDATAL;
    *b = c;
    // CDC_UART.TXDATAL = c; /* echo */

    return retval;
}


/*
 * UART send char routine MUST send exactly and only the given char;
 * it should not translate \n to \r\n.
 * This is because the interactive interface uses binary transfers.
 */
PmReturn_t
plat_putByte(uint8_t b)
{
    /* Loop until serial data reg is empty (from previous transfer) */
     while (!uart_is_tx_ready())
        ;

    /* Put the byte to send into the serial data register */
    CDC_UART.TXDATAL = b;

    return PM_RET_OK;
}


/*
 * This operation is made atomic by temporarily disabling
 * the interrupts. The old state is restored afterwards.
 */
PmReturn_t
plat_getMsTicks(uint32_t *r_ticks)
{
    /* Critical section start */
    unsigned char _sreg = SREG;
    cli();
    *r_ticks = pm_timerMsTicks;
    SREG = _sreg;
    /* Critical section end */
    return PM_RET_OK;
}


#ifdef HAVE_DEBUG_INFO
#define LEN_FNLOOKUP 26
#define LEN_EXNLOOKUP 18
#define FN_MAX_LEN 15
#define EXN_MAX_LEN 18
#ifndef MAX
#define MAX(a,b) (((a) >= (b)) ? (a) : (b))
#endif

/* This table should match src/vm/fileid.txt */
static char const fnstr_00[] PROGMEM = "<no file>";
static char const fnstr_01[] PROGMEM = "codeobj.c";
static char const fnstr_02[] PROGMEM = "dict.c";
static char const fnstr_03[] PROGMEM = "frame.c";
static char const fnstr_04[] PROGMEM = "func.c";
static char const fnstr_05[] PROGMEM = "global.c";
static char const fnstr_06[] PROGMEM = "heap.c";
static char const fnstr_07[] PROGMEM = "img.c";
static char const fnstr_08[] PROGMEM = "int.c";
static char const fnstr_09[] PROGMEM = "interp.c";
static char const fnstr_10[] PROGMEM = "pmstdlib_nat.c";
static char const fnstr_11[] PROGMEM = "list.c";
static char const fnstr_12[] PROGMEM = "main.c";
static char const fnstr_13[] PROGMEM = "mem.c";
static char const fnstr_14[] PROGMEM = "module.c";
static char const fnstr_15[] PROGMEM = "obj.c";
static char const fnstr_16[] PROGMEM = "seglist.c";
static char const fnstr_17[] PROGMEM = "sli.c";
static char const fnstr_18[] PROGMEM = "strobj.c";
static char const fnstr_19[] PROGMEM = "tuple.c";
static char const fnstr_20[] PROGMEM = "seq.c";
static char const fnstr_21[] PROGMEM = "pm.c";
static char const fnstr_22[] PROGMEM = "thread.c";
static char const fnstr_23[] PROGMEM = "float.c";
static char const fnstr_24[] PROGMEM = "class.c";
static char const fnstr_25[] PROGMEM = "bytearray.c";

static PGM_P const fnlookup[LEN_FNLOOKUP] PROGMEM =
{
    fnstr_00, fnstr_01, fnstr_02, fnstr_03,
    fnstr_04, fnstr_05, fnstr_06, fnstr_07,
    fnstr_08, fnstr_09, fnstr_10, fnstr_11,
    fnstr_12, fnstr_13, fnstr_14, fnstr_15,
    fnstr_16, fnstr_17, fnstr_18, fnstr_19,
    fnstr_20, fnstr_21, fnstr_22, fnstr_23,
    fnstr_24, fnstr_25
};

/* This table should match src/vm/pm.h PmReturn_t */
static char const exnstr_00[] PROGMEM = "Exception";
static char const exnstr_01[] PROGMEM = "SystemExit";
static char const exnstr_02[] PROGMEM = "IoError";
static char const exnstr_03[] PROGMEM = "ZeroDivisionError";
static char const exnstr_04[] PROGMEM = "AssertionError";
static char const exnstr_05[] PROGMEM = "AttributeError";
static char const exnstr_06[] PROGMEM = "ImportError";
static char const exnstr_07[] PROGMEM = "IndexError";
static char const exnstr_08[] PROGMEM = "KeyError";
static char const exnstr_09[] PROGMEM = "MemoryError";
static char const exnstr_10[] PROGMEM = "NameError";
static char const exnstr_11[] PROGMEM = "SyntaxError";
static char const exnstr_12[] PROGMEM = "SystemError";
static char const exnstr_13[] PROGMEM = "TypeError";
static char const exnstr_14[] PROGMEM = "ValueError";
static char const exnstr_15[] PROGMEM = "StopIteration";
static char const exnstr_16[] PROGMEM = "Warning";
static char const exnstr_17[] PROGMEM = "OverflowError";

static  PGM_P const exnlookup[LEN_EXNLOOKUP] PROGMEM =
{
    exnstr_00, exnstr_01, exnstr_02, exnstr_03,
    exnstr_04, exnstr_05, exnstr_06, exnstr_07,
    exnstr_08, exnstr_09, exnstr_10, exnstr_11,
    exnstr_12, exnstr_13, exnstr_14, exnstr_15,
    exnstr_16, exnstr_17
};
#endif /* HAVE_DEBUG_INFO */


void
plat_reportError(PmReturn_t result)
{
#ifdef HAVE_DEBUG_INFO
    uint8_t res;
    pPmFrame_t pframe;
    pPmObj_t pstr;
    PmReturn_t retval;
    uint16_t bcindex;
    uint16_t bcsum;
    uint16_t linesum;
    uint16_t len_lnotab;
    uint8_t const *plnotab;
    uint16_t i;
    char pstrbuf[MAX(FN_MAX_LEN, EXN_MAX_LEN)];

    /* Print traceback */
    puts_P(PSTR("Traceback (most recent call first):"));

    /* Get the top frame */
    pframe = gVmGlobal.pthread->pframe;

    /* If it's the native frame, print the native function name */
    if (pframe == (pPmFrame_t)&(gVmGlobal.nativeframe))
    {

        /* The last name in the names tuple of the code obj is the name */
        retval = tuple_getItem((pPmObj_t)gVmGlobal.nativeframe.nf_func->
                               f_co->co_names, -1, &pstr);
        if ((retval) != PM_RET_OK)
        {
            puts_P(PSTR("  Unable to get native func name."));
            return;
        }
        else
        {
            printf_P(PSTR("  %s() __NATIVE__\n"), ((pPmString_t)pstr)->val);
        }

        /* Get the frame that called the native frame */
        pframe = (pPmFrame_t)gVmGlobal.nativeframe.nf_back;
    }

    /* Print the remaining frame stack */
    for (; pframe != C_NULL; pframe = pframe->fo_back)
    {
        /* The last name in the names tuple of the code obj is the name */
        retval = tuple_getItem((pPmObj_t)pframe->fo_func->f_co->co_names,
                               -1,
                               &pstr);
        if ((retval) != PM_RET_OK) break;

        /*
         * Get the line number of the current bytecode. Algorithm comes from:
         * http://svn.python.org/view/python/trunk/Objects/lnotab_notes.txt?view=markup
         */
        bcindex = pframe->fo_ip - pframe->fo_func->f_co->co_codeaddr;
        plnotab = pframe->fo_func->f_co->co_lnotab;
        len_lnotab = mem_getWord(MEMSPACE_PROG, &plnotab);
        bcsum = 0;
        linesum = pframe->fo_func->f_co->co_firstlineno;
        for (i = 0; i < len_lnotab; i += 2)
        {
            bcsum += mem_getByte(MEMSPACE_PROG, &plnotab);
            if (bcsum > bcindex) break;
            linesum += mem_getByte(MEMSPACE_PROG, &plnotab);
        }

        /* Get the file name of this frame's function */
        if (pframe->fo_func->f_co->co_memspace == MEMSPACE_PROG)
        {
            strncpy_P(pstrbuf,
                      (char *)pframe->fo_func->f_co->co_filename,
                      MAX(FN_MAX_LEN, EXN_MAX_LEN));
        }
        printf_P(PSTR("  File \"%s\", line %d, in %s\n"),
                 ((pframe->fo_func->f_co->co_memspace == MEMSPACE_PROG)
                 ? pstrbuf
                 : (char *)pframe->fo_func->f_co->co_filename),
                 linesum,
                 ((pPmString_t)pstr)->val);
    }

    /* Print error */
    res = (uint8_t)result;
    if ((res > 0) && ((res - PM_RET_EX) < LEN_EXNLOOKUP))
    {
        strncpy_P(pstrbuf,
                  (PGM_P)pgm_read_word(&exnlookup[res - PM_RET_EX]),
                  EXN_MAX_LEN);
        printf_P(PSTR("%s"), pstrbuf);
    }
    else
    {
        printf_P(PSTR("Error code 0x%02X"), result);
    }
    printf_P(PSTR(" detected by "));

    if ((gVmGlobal.errFileId > 0) && (gVmGlobal.errFileId < LEN_FNLOOKUP))
    {
        strncpy_P(pstrbuf,
                  (PGM_P)pgm_read_word(&fnlookup[gVmGlobal.errFileId]),
                  FN_MAX_LEN);
        printf_P(PSTR("%s:"), pstrbuf);
    }
    else
    {
        printf_P(PSTR("FileId 0x%02X line "), gVmGlobal.errFileId);
    }
    printf_P(PSTR("%d\n"), gVmGlobal.errLineNum);

#else /* HAVE_DEBUG_INFO */

    /* Print error */
    printf_P(PSTR("Error:     0x%02X\n"), result);
    printf_P(PSTR("  Release: 0x%02X\n"), gVmGlobal.errVmRelease);
    printf_P(PSTR("  FileId:  0x%02X\n"), gVmGlobal.errFileId);
    printf_P(PSTR("  LineNum: %d\n"), gVmGlobal.errLineNum);

    /* Print traceback */
    {
        pPmObj_t pframe;
        pPmObj_t pstr;
        PmReturn_t retval;

        puts_P(PSTR("Traceback (top first):"));

        /* Get the top frame */
        pframe = (pPmObj_t)gVmGlobal.pthread->pframe;

        /* If it's the native frame, print the native function name */
        if (pframe == (pPmObj_t)&(gVmGlobal.nativeframe))
        {

            /* The last name in the names tuple of the code obj is the name */
            retval = tuple_getItem((pPmObj_t)gVmGlobal.nativeframe.nf_func->
                                   f_co->co_names, -1, &pstr);
            if ((retval) != PM_RET_OK)
            {
                puts_P(PSTR("  Unable to get native func name."));
                return;
            }
            else
            {
                printf_P(PSTR("  %s() __NATIVE__\n"), ((pPmString_t)pstr)->val);
            }

            /* Get the frame that called the native frame */
            pframe = (pPmObj_t)gVmGlobal.nativeframe.nf_back;
        }

        /* Print the remaining frame stack */
        for (;
             pframe != C_NULL;
             pframe = (pPmObj_t)((pPmFrame_t)pframe)->fo_back)
        {
            /* The last name in the names tuple of the code obj is the name */
            retval = tuple_getItem((pPmObj_t)((pPmFrame_t)pframe)->
                                   fo_func->f_co->co_names, -1, &pstr);
            if ((retval) != PM_RET_OK) break;

            printf_P(PSTR("  %s()\n"), ((pPmString_t)pstr)->val);
        }
        puts_P(PSTR("  <module>."));
    }
#endif /* HAVE_DEBUG_INFO */
}
