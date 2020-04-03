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
#
# Pin() examples:
#   pin enumeration PORTA..F -> 0, 8, 16, 24 .. 47
# 
#   pin12 = Pin(12, INPUT + PULL_UP) # pin 12 (aka B4) as input with pull up enabled
#   print pin12.get()
#
#   pin13 = Pin(13, Pin.OUTPUT) # configure pin 13 (aka B5) as output
#   pin13.toggle()

#   LED = Pin(45,  Pin.OUTPUT + Pin.START_HIGH + Pin.INVERT )
#   LED.set(Pin.ON)
#   LED.set(Pin.OFF)
#   LED.toggle()
#   LED.get() -> True/False
#
#  Button() example: (BTN is the default button on the curiosity board)
#   BTN = Button(46)
#   print BTN.pressed() # -> True/False (non-pressed -> pressed)
#   print BTN.state() # -> True/False (istantaneous)
#
# Blocking delays:
#   delay(500) # ms
#
# SPI example # sck, mosi, miso must match the selected instance default pins
#   oled = SPI(0, mode=0, sck=40, mosi=41, miso=42, frequency=4000000)
#   oled.transfer(bytearray(1,2,3,4))
# 
# \endcode

"""__NATIVE__
#include <avr/io.h>
#define __DELAY_BACKWARD_COMPATIBLE__
#include <util/delay.h>
//#include "pyToC.h"
"""

class Pin(object) :
    HIGH = 1
    LOW  = 0
    ON   = 1
    OFF  = 0
    # configuration
    INPUT      = 0
    OUTPUT     = 1<<0
    START_HIGH = 1<<1
    INVERT     = 1<<2
    PULL_UP    = 1<<3
    IOC        = 1<<4

    def __init__(self, pin_no, config):
        self.pin_no = pin_no
        if config & Pin.START_HIGH :
            _pin(pin_no, Pin.HIGH)
        self.ctrl(config)

    def ctrl(self, config):
        _pin_config(self.pin_no, config)

    def set(self, value):
        _pin(self.pin_no, value)

    def toggle(self):
        _pin(self.pin_no, not _pin(self.pin_no))

    def get(self):
        return _pin(self.pin_no)

# Default LED present on Curiosity board
# LED = Pin(45, 7) #Pin.OUTPUT + Pin.INVERT + Pin.START_HIGH)


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

# define AVR-DA Curiosity specific LED pin and value
            
class Button(object) :
    "Handle simple Push buttons"

    def __init__(self, pin_no):
        self.pin_no = pin_no
        _pin(pin_no, Pin.INPUT)
        self.prev = False

    def pressed(self):
        prev = self.prev
        self.prev = self.state()    # new state
        return  True if not prev and self.prev else False         

    def state(self):
        return not _pin(self.pin_no)

# Default button present on Curiosity board
# BTN = Button(46)

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

        // *(port+1) = 1<<pin; // Set pin DIRSET to output
        
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

def _pin_config(pin_no, config):
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
# 
# SPI
#
class Spi(object):
    "Synchronous Port Interface"
    def __init__(self, instance, mode=0, frequency=8000000,  mosi=4, miso=5, msck=6):
        self.instance = instance
        _spi_config(instance, mode, frequency, mosi, miso, msck)

    def xfer(self, data):
        return _spi_xfer(self.instance, data)

# example 
#oled = Spi(0) 
#oled = Spi(0, 0, 3000000) 
#oled.xfer(bytearray([1,2,3,4]))

def _spi_config(instance, mode, frequency, mosi, miso, msck):
    """__NATIVE__
    // computes best prescaler approx -> returns actual frequency 
    PmReturn_t retval = PM_RET_OK;

    if(NATIVE_GET_NUM_ARGS() != 6) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    pPmObj_t pa = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    uint8_t instance =  ((pPmInt_t)pa)->val & 1;

    pa = NATIVE_GET_LOCAL(1);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    uint8_t mode =  ((pPmInt_t)pa)->val;

    pPmObj_t pf = NATIVE_GET_LOCAL(2);
    if (OBJ_GET_TYPE(pf) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    uint32_t frequency =  ((pPmInt_t)pf)->val;
    
    pa = NATIVE_GET_LOCAL(3);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    uint8_t mosi =  ((pPmInt_t)pa)->val;

    pa = NATIVE_GET_LOCAL(4);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    uint8_t miso =  ((pPmInt_t)pa)->val;

    pa = NATIVE_GET_LOCAL(5);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    uint8_t msck =  ((pPmInt_t)pa)->val;
    
    /* get pointer to SPI instance registers */
    uint8_t *spi = (uint8_t *)(&SPI0+instance);

    /* get a pointer to the port struct */
    uint8_t *port = (uint8_t*) (&PORTA + (mosi>>3)); // use mosi to deduce the port
    // SPI0 has default: MOSI = 04/PA4(out), MISO = 05/PA5(in), MSCK = 06/PA6(out) 
    mosi &= 7;
    miso &= 7;
    msck &= 7;

    *(port+1) = (1<<mosi) + (1<<msck); // Set  DIRSET to output for MOSI and MSCK
    *(port+2) = (1<<miso); // Set  DIRCLR to input for MISO
    
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
    ((pPmInt_t)pf)->val = spi_clock;

    // SPI.CTRLA
    *spi = (0<<6) + (1<<5) + (prescaler<<1); // MSB, master, CLK*2|PRE, ENABLE
    // SPI.CTRLB
    *(spi+1) = (mode & 0x03) + 4; // disable slave select in master mode (single master)
    // enable spi port
    *spi |= 1;  
 
    NATIVE_SET_TOS(pf);
    return retval;
    """
    pass

def _spi_xfer(instance, data):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;
    uint8_t instance;
    pPmObj_t pba;

    if(NATIVE_GET_NUM_ARGS() != 2) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pi) != OBJ_TYPE_INT) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    instance =  ((pPmInt_t)pi)->val;

    /* get pointer to SPI instance registers */
    volatile uint8_t *spi = (uint8_t *)(&SPI0+instance);

    pPmObj_t po = NATIVE_GET_LOCAL(1);
    if (OBJ_GET_TYPE(po) != OBJ_TYPE_CLI) { // must be a class instance 
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }
    // get the actual byte array object it should contain
    retval = dict_getItem((pPmObj_t)((pPmInstance_t)po)->cli_attrs,
                        PM_NONE,
                        (pPmObj_t *)&pba);
    PM_RETURN_IF_ERROR(retval);

    if (OBJ_GET_TYPE(pba) != OBJ_TYPE_BYA) { // must contain a bytearray
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    uint8_t n = ((pPmBytearray_t)pba)->length;
    uint8_t *pb = ((pPmBytearray_t)pba)->val->val;

    // perform the transfer
    for(int i=0; i<n; i++) {
        *(spi+4) = *pb; // write data
        while( (*(spi+3) & 0x80) == 0); // wait 
        *pb++ = *(spi+4); // read back 
    }

    NATIVE_SET_TOS(po);
    return retval;
    '''
    pass