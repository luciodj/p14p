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
#include "pyToC.h"
#include "avr.h"
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
def _pin(pin_no, value):
    """__NATIVE__
    uint8_t pin_no;
    pPmObj_t pa;
    PmReturn_t retval = PM_RET_OK;

    if ( (NATIVE_GET_NUM_ARGS() < 1) || (NATIVE_GET_NUM_ARGS() > 2) ) {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    /* get the pin number */
    pa = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 48, &pin_no));

    /* if assigned a value */
    if (NATIVE_GET_NUM_ARGS() == 2) {
        // get the pin value 
        pa = NATIVE_GET_LOCAL(1); 
        /* If the arg is not an integer or boolean, raise TypeError */
        if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT && OBJ_GET_TYPE(pa) != OBJ_TYPE_BOOL ) { 
            PM_RAISE(retval, PM_RET_EX_TYPE);
            return retval;
        }
        avr_pin_set(pin_no, ((pPmInt_t)pa)->val);
    }
    pa = (avr_pin_get(pin_no)) ? PM_TRUE : PM_FALSE;

    NATIVE_SET_TOS(pa); // Push our result object onto the stack
    return retval;
    """
    pass

def _pin_config(pin_no, config):
    """__NATIVE__
    uint8_t pin_no;
    pPmObj_t pa;
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(2);

    /* get the pin number */
    pa = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 48, &pin_no));

    // get the config value 
    pa = NATIVE_GET_LOCAL(1); 
    /* If the arg is not an integer , raise TypeError */
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT ) { 
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    avr_pin_config(pin_no, ((pPmInt_t)pa)->val);

    NATIVE_SET_TOS(PM_NONE);
    return retval;
    """
    pass
# 
# SPI
#
class Spi(object):
    "Synchronous Port Interface"
    def __init__(self, instance, mode=0, freq=8000000,  mosi=4, miso=5, msck=6):
        self.id = instance
        self.freq = _spi_config(instance, mode, freq, mosi, miso, msck)

    def xfer(self, data):
        return _spi_xfer(self.id, data)

# example 
#oled = Spi(0) 
#oled = Spi(0, 0, 3000000) 
#oled.xfer(bytearray([1,2,3,4]))

def _spi_config(instance, mode, frequency, mosi, miso, msck):
    """__NATIVE__
    // computes best prescaler approx -> returns actual frequency 
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(6);

    uint8_t instance;
    pPmObj_t pa = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 1, &instance));

    uint8_t mode;
    pa = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 3, &mode));

    pPmObj_t pf = NATIVE_GET_LOCAL(2);
    uint32_t frequency =  ((pPmInt_t)pf)->val;
    PM_CHECK_FUNCTION( getRangedInt(pf, 0, F_CPU, (int32_t*)&frequency));
    
    uint8_t mosi;
    pa = NATIVE_GET_LOCAL(3);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 48, &mosi));
    avr_pin_config(mosi, 1); // output

    uint8_t miso;
    pa = NATIVE_GET_LOCAL(4);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 48, &miso));
    avr_pin_config(miso, 0); // input

    uint8_t msck;
    pa = NATIVE_GET_LOCAL(5);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 48, &msck));
    avr_pin_config(msck, 1); // output
    
    retval = int_new( avr_spi_config(instance, mode, frequency), &pa);

    NATIVE_SET_TOS(pa);
    return retval;
    """
    pass

def _spi_xfer(instance, data):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;
    pPmObj_t pba;

    CHECK_NUM_ARGS(2);

    uint8_t instance;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &instance));

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

    avr_spi_xfer(instance, n, pb);

    NATIVE_SET_TOS(po);
    return retval;
    '''
    pass

#
#   ADC support
#
# ADC = Adc(); # init
# ADC.get(TEMP) #-> return temp sensor reading
# ADC.get(GND)  #-> 0 reading (check)
# ADC.get(DAC)  #-> DAC internal pick
# ADC.get(0-15) #-> read analog pin 0-15

class Adc(object):
    TEMP = 0x42
    DAC  = 0x48
    GND  = 0x40
    
    def __init__(self):
        _adc_config()

    def get(self, channel):
        return _adc_get(channel)


def _adc_config(void):
    """__NATIVE__
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(0);

    //uint8_t mode;
    //pPmObj pa = NATIVE_GET_LOCAL(1);
    //PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 3, &mode));
    
    avr_adc_config();

    NATIVE_SET_TOS(PM_NONE);
    return retval;
    """
    pass

def _adc_get(channel):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;
    pPmObj_t pVal;

    CHECK_NUM_ARGS(1);

    uint8_t channel;
    pPmObj_t pc = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pc, 0, 0x48, &channel));

    retval = int_new(avr_adc_get(channel), &pVal);

    NATIVE_SET_TOS(pVal);
    return retval;
    '''
    pass

##
# TCA module
# 

class Tca(object):
    def __init__(self, period_us=20000, duty0=1000, duty1=None, duty2=None):
        self.duty = [duty0, duty1, duty2]
        # if None, channel won't be enabled
        if duty0: _tca_set(0, duty0) 
        if duty1: _tca_set(1, duty1)
        if duty2: _tca_set(2, duty2)
        _tca_init( period_us, duty0!=None, duty1!=None, duty2!=None)
        
    def set(self, id, duty_us):
        self.duty[id] = duty_us 
        _tca_set(id, duty_us)

def _tca_set(instance, duty):
    """___NATIVE___
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(2);

    uint8_t instance;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 2, &instance));

    uint32_t duty;
    pa = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedInt(pa, 0, 65535, &duty));

    avr_tca_set(instance, duty);    
    """
    pass

def _tca_init(period, b0, b1, b2):
    """___NATIVE___
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(4);

    uint8_t period;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 1, 65535, &period));

    bool b0, b1, b2;
    GET_BOOL_ARG(1, &b0);
    GET_BOOL_ARG(2, &b1);
    GET_BOOL_ARG(3, &b2);

    avr_tca_init(period, b0, b1, b2);

    """
    pass
