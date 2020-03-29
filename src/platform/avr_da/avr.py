# This file is Copyright 2007 Dean Hall.
# This file is part of the Python-on-a-Chip libraries.
# This software is licensed under the MIT License.
# See the LICENSE file for details.

## @file
#  @copybrief avr
## @package avr
#  @brief AVR MCU Access Module
#
# Provides generic access to the AVR microcontroller
#
# Note that to save RAM when the module is imported, many of the
# port & ddr methods below are commented out. Uncomment and recompile
# in order to use!
#
# <b>USAGE</b>
#
# \code
# from avr import *
# LED.set(LED.ON)
# LED.set(LED.OFF)
# LED.toggle()
# LED.get() -> True/False
#
# BTN.pressed() -> True/False
#
# avr.delay(500) # Half second pause
#
# pin enumeration PORTA..F -> 0, 8, 16, 24 .. 47
# pin(pin_no, value) -> set pin = value
# pin(pin_no) -> True / False 
#
# \endcode

"""__NATIVE__
#include <avr/io.h>
#define __DELAY_BACKWARD_COMPATIBLE__
#include <util/delay.h>
"""

class Pin() :
    HIGH = 1
    LOW  = 0
    # configuration
    INPUT      = 0
    OUTPUT     = 1<<0
    START_HIGH = 1<<1
    INVERT     = 1<<2
    PULL_UP    = 1<<3
    IOC        = 1<<4

    def __init__(self, pin_no, config=Pin.INPUT):
        self.pin_no = pin_no
        if config & Pin.START_HIGH:
            _pin(pin_no, Pin.HIGH)
        _pin_config(pin_no, config)
    
    def set(self, value):
        _pin(self.pin_no, value)

    def toggle(self):
        _pin(self.pin_no, not _pin(self.pin_no))

    def get(self):
        return _pin(self.pin_no)

# define AVR-DA Curiosity specific LED pin and value
class Led(Pin) :
    ON  = 0
    OFF = 1 

    def __init__(self, pin_no):
        super().__init__(pin_no, config=Pin.OUTPUT)
            
 # Default LED present on Curiosity board
LED = Led(45)

class Button() :
    "Handle simple Push buttons"

    def __init__(self, pin_no):
        self.pin_no = pin_no

    def pressed(self):
        return not _pin(self.pin_no)

# Default button present on Curiosity board
BTN = Button(46)

# 
# Low level routines to access AVR-DA and Curiosity assets
#
# Pin is specified as an integer, 0-47 (A0=0, A1=1 .. B0=8, B1=9 ... )
#
# Value is either boolean True/False or Integer 0 or non-zero.
#
def _pin(pin, value):
    """__NATIVE__
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
    """
    pass

def _pin_config(pin, config):
    """__NATIVE__
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
    """
    pass

def delay(ms):
    """__NATIVE__
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
    """
    pass

# 
# SPI
#
class SPI():
    "Synchronous Port Interface"
    def __init__(self, instance, sck, mosi, miso, mode=0, frequency=1000000):
        self.instance = instance
        _pin_config(sck, config=Pin.OUTPUT)
        _pin_config(mosi, config=Pin.OUTPUT)
        _pin_config(miso, config=Pin.INPUT)
        _spi_config(instance, mode, frequency)

    def transfer(data):
        return _spi_transfer(self.instance, data)


# example 
#oled = SPI(0, mode=0, sck=40, mosi=41, miso=42, frequency=4000000)
#oled.transfer(bytearray(1,2,3,4))

def _spi_config(instance, mode, frequency):
    """__NATIVE__
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
    """
    pass

def _spi_transfer(instance, data):
    """__NATIVE__
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
    """
    pass
