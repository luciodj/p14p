#undef __FILE_ID__
#define __FILE_ID__ 0x0A
/**
 * PyMite usr native function file
 *
 * automatically created by pmImgCreator.py
 * on Thu Mar 12 07:22:14 2020
 *
 * DO NOT EDIT THIS FILE.
 * ANY CHANGES WILL BE LOST.
 *
 * @file    main_nat.c
 */

#define __IN_LIBNATIVE_C__
#include "pm.h"

/* From: avr.py */
#include <avr/io.h>
#define __DELAY_BACKWARD_COMPATIBLE__
#include <util/delay.h>

PmReturn_t
nat_placeholder_func(pPmFrame_t *ppframe)
{

    /*
     * Use placeholder because an index 
     * value of zero denotes the stdlib.
     * This function should not be called.
     */
    PmReturn_t retval;
    PM_RAISE(retval, PM_RET_EX_SYS);
    return retval;

}

PmReturn_t
nat_01_avr__pin(pPmFrame_t *ppframe)
{

    uint8_t *port;
    uint8_t pin;
    pPmObj_t pa;
    PmReturn_t retval = PM_RET_OK;

    if ( (NATIVE_GET_NUM_ARGS() < 1) || (NATIVE_GET_NUM_ARGS() > 2) ) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    /* get the pin number */
    pa = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    /* Check pin is in range 0-47 (A-F) */
    if ( ((pPmInt_t)pa)->val < 0 || ((pPmInt_t)pa)->val > 48 ) {
        PM_RAISE(retval, PM_RET_EX_VAL);
        return retval;
    }
    pin = ((pPmInt_t)pa)->val;

    /* split in port and pin */
    port = (uint8_t*) (&PORTA + (pin >> 3)); 
    pin &= 0x7;

    /* if assigned a value */
    if (NATIVE_GET_NUM_ARGS() == 2) {
        // get the pin value 
        pa = NATIVE_GET_LOCAL(1); 
        /* If the arg is not an integer or boolean, raise TypeError */
        if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT && OBJ_GET_TYPE(pa) != OBJ_TYPE_BOOL ) { 
            PM_RAISE(retval, PM_RET_EX_TYPE);
            return retval;
        }

        *(port+1) = 1<<pin; // Set pin DIRSET to output
        
        if ( ((pPmInt_t)pa)->val )
            *(port+5) = 1<<pin;     // OUT set
        else
            *(port+6) = 1<<pin;     // OUT clear
    }

    pa = ( *(port+8) & (1<<pin)) ? PM_TRUE : PM_FALSE;
    NATIVE_SET_TOS(pa); // Push our result object onto the stack

    return retval;
    
}

PmReturn_t
nat_02_avr__pin_config(pPmFrame_t *ppframe)
{

    uint8_t *port;
    uint8_t pin, config, ctrl;
    pPmObj_t pa;
    PmReturn_t retval = PM_RET_OK;

    if ( NATIVE_GET_NUM_ARGS() != 2 ) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    /* get the pin number */
    pa = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    /* Check pin is in range 0-47 (A-F) */
    if ( ((pPmInt_t)pa)->val < 0 || ((pPmInt_t)pa)->val > 48 ) {
        PM_RAISE(retval, PM_RET_EX_VAL);
        return retval;
    }
    pin = ((pPmInt_t)pa)->val;

    /* split in port and pin */
    port = (uint8_t*) (&PORTA + (pin >> 3)); 
    pin &= 0x7;

    // get the config value 
    pa = NATIVE_GET_LOCAL(1); 
    /* If the arg is not an integer , raise TypeError */
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT ) { 
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    config = ((pPmInt_t)pa)->val;
    if ( config & 1 ) 
        *(port+1) = 1<<pin; // Set  DIRSET to output
    else 
        *(port+2) = 1<<pin; // Set  DIRCLR to input
    

/*  
    INVERT     = 1<<2
    PULL_UP    = 1<<3 
    IOC        = 1<<4 
*/
    ctrl = 0;
    if ( config & 1<<2)         // INVERT
        ctrl += 1<<7;     
    if ( config & 1<<3)         // PULLUP
        ctrl += 1<<3;     
    if ( config & 1<<4)         // IOC 
        ctrl += 3;              // falling edge
    *(port+16+pin) = ctrl;

    NATIVE_SET_TOS(PM_NONE);
    return retval;
    
}

PmReturn_t
nat_03_avr_delay(pPmFrame_t *ppframe)
{

    PmReturn_t retval = PM_RET_OK;

    if(NATIVE_GET_NUM_ARGS() != 1) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    pPmObj_t pa = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pa) == OBJ_TYPE_INT) {
        _delay_ms((double) ((pPmInt_t)pa)->val);
    }
    else if (OBJ_GET_TYPE(pa) == OBJ_TYPE_FLT) {
        _delay_ms((double) ((pPmFloat_t)pa)->val);
    }
    else {
        PM_RAISE(retval, PM_RET_EX_TYPE);
    }

    NATIVE_SET_TOS(PM_NONE);
    return retval;
    
}

PmReturn_t
nat_04_avr__spi_config(pPmFrame_t *ppframe)
{

    PmReturn_t retval = PM_RET_OK;
    uint8_t instance, mode;
    uint32_t frequency;

    if(NATIVE_GET_NUM_ARGS() != 3) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    pPmObj_t pa = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pa) == OBJ_TYPE_INT) {
        instance =  ((pPmInt_t)pa)->val);
    }
    else {
        PM_RAISE(retval, PM_RET_EX_TYPE);
    }

    pa = NATIVE_GET_LOCAL(1);
    if (OBJ_GET_TYPE(pa) == OBJ_TYPE_INT) {
        mode =  ((pPmInt_t)pa)->val);
    }
    else {
        PM_RAISE(retval, PM_RET_EX_TYPE);
    }

    pa = NATIVE_GET_LOCAL(2);
    if (OBJ_GET_TYPE(pa) == OBJ_TYPE_INT) {
        frequency =  ((pPmInt_t)pa)->val);
    }
    else {
        PM_RAISE(retval, PM_RET_EX_TYPE);
    }
    /* get pointer to SPI instance registers */
    uint8_t *spi = (uint8_t *)(SPI0+instance);

    /* find best prescaler so that spi_clock < frequency */
    uint32_t spi_clock = FCU/4;
    uint8_t  prescaler = 0;
    while (spi_clock > frequency) {
        spi_clock /= 4;
        prescaler++;
    }
    if (prescaler >= 3) { 
        prescaler = 3;  // 1:128  is really the best/slowest we can do
        spi_clock = FCU/128;
    }
    if (spi_clock*2 <= frequency) {
        prescaler += 8; // CLK*2 feature allows us to find middle points
    }
    // SPI.CTRLA
    *spi = (0<<6) + (1<<5) + (prescaler<<1) + 1; // MSB, master, CLK*2|PRE, ENABLE
    *(spi+1) = mode & 0x03;

    NATIVE_SET_TOS(PM_NONE);
    return retval;
    
}

PmReturn_t
nat_05_avr__spi_transfer(pPmFrame_t *ppframe)
{

    PmReturn_t retval = PM_RET_OK;
    uint8_t instance;
    uint8_t objid;
    pPmBytearray_t pba = C_NULL;
    pPmBytes_t pb = C_NULL;

    if(NATIVE_GET_NUM_ARGS() != 2) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pi) == OBJ_TYPE_INT) {
        instance =  ((pPmInt_t)pi)->val);
    }
    else {
        PM_RAISE(retval, PM_RET_EX_TYPE);
    }
    /* get pointer to SPI instance registers */
    uint8_t *spi = (uint8_t *)(SPI0+instance);

    pPmObj_t po = NATIVE_GET_LOCAL(1);
    if (OBJ_GET_TYPE(po) != OBJ_TYPE_BYA) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
    }

    uint8_t n = ((pPmByteArray_t)pb)->length;

    /* Allocate a result bytearray */
    retval = heap_getChunk(sizeof(PmBytearray_t), (uint8_t **)&pba);
    PM_RETURN_IF_ERROR(retval);
    OBJ_SET_TYPE(pba, OBJ_TYPE_BYA);
    pba->length = n;
    pba->val = C_NULL;

    /* Allocate the bytes container */
    heap_gcPushTempRoot((pPmObj_t)pba, &objid);
    retval = bytes_new(n, (pPmObj_t *)&pb);
    heap_gcPopTempRoot(objid);
    PM_RETURN_IF_ERROR(retval);
    pba->val = pb;

    // perform the transfer
    for(int i=0; i<n; i++) {
        bytearray_getItem(po, i, &pi);
        *(spi+4) = (pPmInt(pi))->val; // write data
        while( *(spi+3) & 0x80 == 0); // wait 
        (pPmInt(pi))->val = *(spi+4); // read back 
        bytearray_setItem(pa, i, pi);
    }

    NATIVE_SET_TOS(pa);
    return retval;
    
}

/* Native function lookup table */
pPmNativeFxn_t const usr_nat_fxn_table[] =
{
    nat_placeholder_func,
    nat_01_avr__pin,
    nat_02_avr__pin_config,
    nat_03_avr_delay,
    nat_04_avr__spi_config,
    nat_05_avr__spi_transfer,
};
