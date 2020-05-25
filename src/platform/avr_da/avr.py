## @file
#  @copybrief avr
## @package avr
#  @brief AVR MCU Access Module
#
# Provides generic access to the AVR microcontroller
#
# 
"""__NATIVE__
/* 
 * AVR MCU Access Module
 * Provides generic access to the AVR microcontroller
 */
#include <avr/io.h>
#define __DELAY_BACKWARD_COMPATIBLE__
#include <util/delay.h>
#include "pyToC.h"
#include "avr.h"
"""

##
# delay(ms) 
#   blocking loop based delay routine
#  example:
#   delay(500) # ms
#
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


##
#   Pin - Basic I/O definition 
#       pin_no is specified as an integer, 0-47 (A0=0, A1=1 .. B0=8, B1=9 ... )
#       values are either boolean True/False or Integer 0 or non-zero.
#   examples: 
#       pin12 = Pin(12, Pin.INPUT + Pin.PULL_UP) # pin 12 (aka B4) as input with pull up enabled
#       print pin12.get()
#
#       pin13 = Pin(13, Pin.OUTPUT) # configure pin 13 (aka B5) as output
#       pin13.toggle()
#
#       LED = Pin(45,  Pin.OUTPUT + Pin.START_HIGH + Pin.INVERT ) # use invert for LEDs tied to Vdd
#       LED.set(Pin.ON)
#       LED.set(Pin.OFF)
#       LED.toggle()
#       LED.get() -> True/False
#
#       Default LED present on Curiosity board
#       LED = Pin(45, 7) #Pin.OUTPUT + Pin.INVERT + Pin.START_HIGH)
#
class Pin(object) :
    HIGH = 1
    LOW  = 0
    ON   = 1
    OFF  = 0
    # configuration
    INPUT      = 0      # set pin as input
    OUTPUT     = 1<<0   # set pin as output
    START_HIGH = 1<<1   # start pin high 
    INVERT     = 1<<2   # invert pin logic 
    PULL_UP    = 1<<3   # enable weak pull ups
    #IOC        = 1<<4   # enable interrupt logic (falling edge)

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

##
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


##
#   "Handle simple Push buttons"
#   Button() example: 
#       BTN = Button(46)    # default button on the curiosity board
#       print BTN.pressed() # -> True/False (non-pressed -> pressed)
#       print BTN.state()   # -> True/False (istantaneous)
#
class Button(object) :

    def __init__(self, pin_no):
        self.pin_no = pin_no
        _pin(pin_no, Pin.INPUT + Pin.INVERT)
        self.prev = False

    def pressed(self):
        prev = self.prev
        self.prev = self.state()    # new state
        return  True if not prev and self.prev else False         

    def state(self):
        return not _pin(self.pin_no)

## 
# SPI
#   Synchronous Port Interface"
#   examples :  
#       oled = Spi(0) 
#       oled = Spi(0, 0, 3000000) 
#       oled.xfer(bytearray([1,2,3,4]))
#
class Spi(object):
    def __init__(self, inst, mode=0, freq=8000000,  mosi=4, miso=5, msck=6):
        self.id = inst
        self.freq = _spi_config(inst, mode, freq, mosi, miso, msck)

    def xfer(self, data):
        return _spi_xfer(self.id, data)


def _spi_config(inst, mode, frequency, mosi, miso, msck):
    """__NATIVE__
    // computes best prescaler approx -> returns actual frequency 
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(6);

    uint8_t inst;
    pPmObj_t pa = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 1, &inst));

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
    
    retval = int_new( avr_spi_config(inst, mode, frequency), &pa);

    NATIVE_SET_TOS(pa);
    return retval;
    """
    pass

def _spi_xfer(inst, data):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;
    pPmObj_t pba;

    CHECK_NUM_ARGS(2);

    uint8_t inst;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &inst));

    pPmObj_t po = NATIVE_GET_LOCAL(1);
    if (OBJ_GET_TYPE(po) != OBJ_TYPE_CLI) { // must be a class inst 
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

    avr_spi_xfer(inst, n, pb);

    NATIVE_SET_TOS(po);
    return retval;
    '''
    pass

##
#   ADC support
#
#   ADC = Adc(); # init
#   ADC.get(TEMP) #-> return temp sensor reading
#   ADC.get(GND)  #-> 0 reading (check)
#   ADC.get(DAC)  #-> DAC internal pick
#   ADC.get(0-15) #-> read analog pin 0-15
#
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
#   TCA module
#   examples:
#     select TCA0 with a 20ms period PC0 output (1ms duty)
#       tca0 = Tca(0) 
#       tca0.set(0, 2000) # change PC0 duty cycle to 2ms
#
#     select TCA0, period = 10ms, 3 outputs (1ms each)
#       tca0 = Tca(0, 10000, 1000, 1000, 1000) 
#       tca.set(0, 100) # PC0 = 100 us
#       tca.set(1, 200) # PC1 = 200 us
#       tca.set(2, 300) # PC2 = 300 us
#
class Tca(object):
    def __init__(self, inst, period_us=20000, duty0=1000, duty1=None, duty2=None):
        self.inst = inst
        self.duty = [duty0, duty1, duty2]
        # if None, channel won't be enabled
        if duty0: _tca_set(self.inst, 0, duty0) 
        if duty1: _tca_set(self.inst, 1, duty1)
        if duty2: _tca_set(self.inst, 2, duty2)
        _tca_config( inst, period_us, duty0!=None, duty1!=None, duty2!=None)
        
    def set(self, chan, duty_us):
        self.duty[chan] = duty_us 
        _tca_set(self.inst, chan, duty_us)

def _tca_set(inst, chan, duty):
    """__NATIVE__
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(3);

    uint8_t inst;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &inst));

    uint8_t chan;
    pPmObj_t pc = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pc, 0, 2, &chan));

    int32_t duty;
    pPmObj_t pa = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedInt(pa, 0, 65535L, &duty));

    avr_tca_set(inst, chan, (uint16_t) duty);    

    NATIVE_SET_TOS(PM_NONE);
    return retval;
   """
    pass

def _tca_config(inst, period, b0, b1, b2):
    """__NATIVE__
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(5);

    uint8_t inst;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &inst));

    int32_t period;
    pPmObj_t pp = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedInt(pp, 1, 65535, &period));

    bool b0, b1, b2;
    GET_BOOL_ARG(2, &b0);
    GET_BOOL_ARG(3, &b1);
    GET_BOOL_ARG(4, &b2);

    // printf("TCA0 period %ld, %d\\n", period, b0);

    avr_tca_config(inst, (uint16_t) period, b0, b1, b2);

    NATIVE_SET_TOS(PM_NONE);
    return retval;
    """
    pass

##
#   TWI - I2C interface
#     examples:
#       twi = Twi(0, 0x76) # init TWI0, address 0x76, alternate 0 pins A2/A3, standard mode)
#       written = twi.write(bytearray("Hello")) # write 5 bytes, return number of bytes written
#       read    = twi.read( bytearray(5))       # read 5 bytes, return number of bytes read
#
class Twi(object):
    def __init__(self, inst, addr, alt=0, mode=0):
        self.inst = inst
        self.addr = addr
        _twi_config(inst, mode, alt)

    def read(self, barray):
        return _twi_read(self.inst, self.addr, barray)

    def write(self, barray):
        return _twi_write(self.inst, self.addr, barray)

#
# SMB - I2 Interface
#   examples:
#       smb = Smb(0, 0xA5, 2) # init TWI0 , address 76, alternate 2 pins C2/C3
#       read = smb.read_word( 3) # read a word from register #3, return int or None
#       read = smb.read_byte( 4) # read a byte from register #4, return int or None
#       success = smb.write_word( 5, 0xAA55) # write a word to register #5, return true if successfull
#       success = smb.write_byte( 6, 0xAA55) # write a byte to register #6, return true if successfull
#
class Smb(object):
    def __init__(self, inst, addr, alt=0):
        self.inst = inst
        self.addr = addr
        _twi_config(inst, 0, alt)

    def read_word(self, reg):
        b = bytearray(2)
        if (_smb_read(self.inst, self.addr, reg, b) == 2):
            return b[0]*256+b[1] # msb first
        else: 
            return None

    def read(self, reg=0xd0):
        b = bytearray(1)
        if _smb_read(self.inst, self.addr, reg, b) == 1:
            return b[0]
        else: 
            return None

    def write_word(self, reg, value):
        b = bytearray([value & 0xff, value >> 8]) # msb first
        return _smb_write(self.inst, self.addr, reg, b) == 2
            
    def write(self, reg, value):
        b = bytearray([value & 0xff])
        return _smb_write(self.inst, self.addr, reg, b) == 1



def _twi_config(inst, mode, alt):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;

    CHECK_NUM_ARGS(3);

    uint8_t inst;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &inst));

    uint8_t mode;
    pPmObj_t pm = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedUint8(pm, 0, 1, &mode));

    uint8_t alternate;
    pPmObj_t pa = NATIVE_GET_LOCAL(2);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 2, &alternate));
    
    avr_twi_config(inst, mode, alternate);

    NATIVE_SET_TOS(PM_NONE);
    return retval;
    '''
    pass

def _twi_write(inst, addr, data):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;
    pPmObj_t pba;
    pPmObj_t pVal;

    CHECK_NUM_ARGS(3);

    uint8_t inst;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &inst));

    uint8_t addr;
    pPmObj_t pa = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 127, &addr));

    pPmObj_t po = NATIVE_GET_LOCAL(2);
    if (OBJ_GET_TYPE(po) != OBJ_TYPE_CLI) { // must be a class inst 
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

    retval = int_new(avr_twi_write(inst, addr, pb, n), &pVal);

    NATIVE_SET_TOS(pVal);  // return number of bytes written
    return retval;
    '''
    pass

def _twi_read(inst, addr, data):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;
    pPmObj_t pba;
    pPmObj_t pVal;

    CHECK_NUM_ARGS(3);

    uint8_t inst;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &inst));

    uint8_t addr;
    pPmObj_t pa = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 127, &addr));

    pPmObj_t po = NATIVE_GET_LOCAL(2);
    if (OBJ_GET_TYPE(po) != OBJ_TYPE_CLI) { // must be a class inst 
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

    retval = int_new(avr_twi_read(inst, addr, pb, n), &pVal);

    NATIVE_SET_TOS(pVal);  // return number of bytes read
    return retval;
    '''
    pass

def _smb_write(inst, addr, reg, data):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;
    pPmObj_t pba;
    pPmObj_t pVal;

    CHECK_NUM_ARGS(4);

    uint8_t inst;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &inst));

    uint8_t addr;
    pPmObj_t pa = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 127, &addr));

    uint8_t reg;
    pPmObj_t pr = NATIVE_GET_LOCAL(2);
    PM_CHECK_FUNCTION( getRangedUint8(pr, 0, 255, &reg));

    pPmObj_t po = NATIVE_GET_LOCAL(3);
    if (OBJ_GET_TYPE(po) != OBJ_TYPE_CLI) { // must be a class inst 
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

    retval = int_new(avr_smb_write(inst, addr, reg, pb, n), &pVal);

    NATIVE_SET_TOS(pVal);  // return number of bytes written
    return retval;
    '''
    pass

def _smb_read(inst, addr, reg, data):
    '''__NATIVE__
    PmReturn_t retval = PM_RET_OK;
    pPmObj_t pba;
    pPmObj_t pVal;

    CHECK_NUM_ARGS(4);

    uint8_t inst;
    pPmObj_t pi = NATIVE_GET_LOCAL(0);
    PM_CHECK_FUNCTION( getRangedUint8(pi, 0, 1, &inst));

    uint8_t addr;
    pPmObj_t pa = NATIVE_GET_LOCAL(1);
    PM_CHECK_FUNCTION( getRangedUint8(pa, 0, 127, &addr));

    uint8_t reg;
    pPmObj_t pr = NATIVE_GET_LOCAL(2);
    PM_CHECK_FUNCTION( getRangedUint8(pr, 0, 255, &reg));

    pPmObj_t po = NATIVE_GET_LOCAL(3);
    if (OBJ_GET_TYPE(po) != OBJ_TYPE_CLI) { // must be a class inst 
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

    retval = int_new(avr_smb_read(inst, addr, reg, pb, n), &pVal);

    NATIVE_SET_TOS(pVal);  // return number of bytes read
    return retval;
    '''
    pass
