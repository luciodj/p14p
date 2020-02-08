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
# pin enumeration PORTA..F -> 0, 8, 16, 24 .. 40
# pin(pin_no, value) -> set pin = value
# pin(pin_no) -> True / False 
#
# legacy
# avr.ddrA(0) # Set all pins as input
# a = avr.portA()
# avr.ddrA(0xFF) # Set all pins as output
# avr.portA(42)
#
#
# if avr.digitalRead('A', 3):
#   avr.digitalWrite('D', 0, True)
# \endcode


"""__NATIVE__
#include <avr/io.h>
#define __DELAY_BACKWARD_COMPATIBLE__
#include <util/delay.h>

/*
 * Common method for all port register operations
 */
PmReturn_t
_portX(volatile uint8_t *port,
       volatile uint8_t *direction,
       volatile uint8_t *pin)
{
   pPmObj_t pa;
   PmReturn_t retval = PM_RET_OK;

   switch (NATIVE_GET_NUM_ARGS())
   {
      /* If no argument is present, return PIN reg value */
      case 0:

        /* Read port and create a Python integer from its value */
        retval = int_new(*pin, &pa);

        /* Return the integer on the stack */
        NATIVE_SET_TOS(pa);
        break;

      /* If one argument is present, set port to that value */
      case 1:
         pa = NATIVE_GET_LOCAL(0);
         /* If the arg is not an integer, raise TypeError */
         if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT)
         {
           PM_RAISE(retval, PM_RET_EX_TYPE);
           break;
         }

         NATIVE_SET_TOS(PM_NONE);

         /* Set PORT to the low byte of the integer value */
         *port = ((pPmInt_t)pa)->val;
         break;

      /* If an invalid number of args are present, raise TypeError */
      default:
         PM_RAISE(retval, PM_RET_EX_TYPE);
         break;
    }

    return retval;
}


/*
 * Set a DDR register to the first Python argument
 */
PmReturn_t _ddrX(volatile uint8_t *direction)
{
   PmReturn_t retval = PM_RET_OK;
   pPmObj_t pa;
   if(NATIVE_GET_NUM_ARGS() != 1)
   {
      PM_RAISE(retval, PM_RET_EX_TYPE);
      return retval;
   }

   pa = NATIVE_GET_LOCAL(0);
   if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT)
   {
      PM_RAISE(retval, PM_RET_EX_TYPE);
      return retval;
   }

   *direction = (uint8_t) ((pPmInt_t)pa)->val;
   NATIVE_SET_TOS(PM_NONE);
   return retval;
}



/*
 * Loads the correct AVR port registers & direction address from the first
 * Python argument, and integer pin number (0-7) from second argument.
 * Port name argument is expected to be a single-character string with the port
 * letter ([a-dA-D])
 *
 * Both port_reg & port_reg arguments are optional.
 *
 * TODO: Look into putting this into a table in PROGMEM instead of a switch
 * statement
 */
PmReturn_t  _get_port_register(volatile uint8_t **pin_reg,
                               volatile uint8_t **port_reg,
                               volatile uint8_t **direction,
                               uint8_t *pin)
{
    pPmObj_t pa;
    pPmObj_t pb;
    PmReturn_t retval = PM_RET_OK;

    pa = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_STR)
    {
      PM_RAISE(retval, PM_RET_EX_TYPE);
      return retval;
    }

    pb = NATIVE_GET_LOCAL(1);
    if (OBJ_GET_TYPE(pb) != OBJ_TYPE_INT)
    {
      PM_RAISE(retval, PM_RET_EX_TYPE);
      return retval;
    }

    // Only single-character strings for the port number
    if ((((pPmString_t)pa)->length) != 1)
    {
      PM_RAISE(retval, PM_RET_EX_VAL);
      return retval;
    }

    // Find port & direction regs (TODO: Possibly make a PROGMEM lookup table)
    switch(((pPmString_t)pa)->val[0])
    {
      case 'F':
      case 'f':
        if(port_reg) *port_reg = &PORTF.OUT;
        if(pin_reg) *pin_reg = &PORTF.IN;
        *direction = &PORTF.DIR;
        break;

/*
      case 'b':
      case 'B':
        if(port_reg) *port_reg = &PORTB;
        if(pin_reg) *pin_reg = &PINB;
        *direction = &DDRB;
        break;
      case 'c':
      case 'C':
#if defined(PORTC) && defined(PINC) && defined(DDRC)
        if(port_reg) *port_reg = &PORTC;
        if(pin_reg) *pin_reg = &PINC;
        *direction = &DDRC;
#endif
        break;
      case 'd':
      case 'D':
#if defined(PORTD) && defined(PIND) && defined(DDRD)
        if(port_reg) *port_reg = &PORTD;
        if(pin_reg) *pin_reg = &PIND;
        *direction = &DDRD;
#endif
        break;
      case 'e':
      case 'E':
#if defined(PORTE) && defined(PINE) && defined(DDRE)
        if(port_reg) *port_reg = &PORTE;
        if(pin_reg) *pin_reg = &PINE;
        *direction = &DDRE;
#endif
        break;
      case 'f':
      case 'F':
#if defined(PORTF) && defined(PINF) && defined(DDRF)
        if(port_reg) *port_reg = &PORTF;
        if(pin_reg) *pin_reg = &PINF;
        *direction = &DDRF;
#endif
        break;

*/
      default:
        PM_RAISE(retval, PM_RET_EX_VAL);
        return retval;
    }

    // Check pin is in range
    if(((pPmInt_t)pb)->val < 0 || ((pPmInt_t)pb)->val > 7)
    {
        PM_RAISE(retval, PM_RET_EX_VAL);
        return retval;
    }
    *pin = ((pPmInt_t)pb)->val;

    return retval;
}

"""

# define AVR-DA Curiosity specific LED pin and value
class Led() :
  ON  = 0
  OFF = 1 
  
  def __init__(self, pin_no):
    self.pin_no = pin_no 

  def set(self, value):
    pin(self.pin_no, value)

  def toggle(self):
      pin(self.pin_no, not pin(self.pin_no))

  def get(self):
    return pin(self.pin_no)

LED = Led(45)

class Button() :

  def __init__(self, pin_no):
    self.pin_no = pin_no

  def pressed(self):
    return not pin(self.pin_no)

BTN = Button(46)
  

# Port methods are commented out by default because of the amount of RAM
# used when the module is loaded. Uncomment the ones you need...

# def portA(a):
#     """__NATIVE__
#     return _portX(&PORTA.IN, &PORTA.DIR, &PORTA.OUT);
#     """
#     pass

# def portB(a):
#     """__NATIVE__
#     return _portX(&PORTB, &DDRB, &PINB);
#     """
#     pass

# def portC(a):
#     """__NATIVE__
#     return _portX(&PORTC, &DDRC, &PINC);
#     """
#     pass

# def portD(a):
#     """__NATIVE__
#     return _portX(&PORTD, &DDRD, &PIND);
#     """
#     pass

# def portE(a):
#     """__NATIVE__
#     return _portX(&PORTE, &DDRE, &PINE);
#     """
#     pass

# def portF(a):
#     """__NATIVE__
#     return _portX(&PORTF, &DDRF, &PINF);
#     """
#     pass

# def ddrA(a):
#     """__NATIVE__
#     return _ddrX(&PORTA.DIR);
#     """
#     pass

# def ddrB(a):
#     """__NATIVE__
#     return _ddrX(&DDRB);
#     """
#     pass

# def ddrC(a):
#     """__NATIVE__
#     return _ddrX(&DDRC);
#     """
#     pass


# def ddrD(a):
#     """__NATIVE__
#     return _ddrX(&DDRD);
#     """
#     pass

# def ddrE(a):
#     """__NATIVE__
#     return _ddrX(&DDRE);
#     """
#     pass

# def ddrF(a):
#     """__NATIVE__
#     return _ddrX(&DDRF);
#     """
#     pass


# Reads a single pin of a particular AVR port
#
# Port is specified as a single-character string, A-F.
# Pin is specified as an integer, 0-7
#
# Return value is boolean True/False, can be treated as 1/0
def digitalRead(port, pin):
    """__NATIVE__
    volatile uint8_t *port;
    volatile uint8_t *direction;
    uint8_t pin;
    PmReturn_t retval = PM_RET_OK;

    if(NATIVE_GET_NUM_ARGS() != 2)
    {
      PM_RAISE(retval, PM_RET_EX_TYPE);
      return retval;
    }

    retval = _get_port_register(&port, C_NULL, &direction, &pin);
    if(retval != PM_RET_OK)
      return retval;

    *direction &= ~(1<<pin); // Set pin to input
    pPmObj_t pa = (*port & (1<<pin)) ? PM_TRUE : PM_FALSE;
    NATIVE_SET_TOS(pa); // Push our result object onto the stack
    return retval;
    """
    pass


# Writes a single pin of a particular AVR port
#
# Port is specified as a single-character string, A-F.
# Pin is specified as an integer, 0-7
# Value is either boolean True/False or Integer 0 or non-zero.
#
def _pin(pin, value):
    """__NATIVE__
    uint8_t *port;
    uint8_t pin;
    pPmObj_t pa;
    PmReturn_t retval = PM_RET_OK;

    if ( (NATIVE_GET_NUM_ARGS() < 1) || (NATIVE_GET_NUM_ARGS() > 2) )
    {
      PM_RAISE(retval, PM_RET_EX_TYPE);
      return retval;
    }

    /* get the pin number */
    pa = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT)
    {
      PM_RAISE(retval, PM_RET_EX_TYPE);
      return retval;
    }

    // Check pin is in range 0-48 (A-F)
    if(((pPmInt_t)pa)->val < 0 || ((pPmInt_t)pa)->val > 48)
    {
        PM_RAISE(retval, PM_RET_EX_VAL);
        return retval;
    }
    pin = ((pPmInt_t)pa)->val;

    /* split in port and pin */
    port = (uint8_t*) (&PORTA + (pin >> 3)); 
    pin &= 0x7;

    /* if assigned a value */
    if  (NATIVE_GET_NUM_ARGS() == 2) {

      // get the pin value 
      pa = NATIVE_GET_LOCAL(1); 
      /* If the arg is not an integer, raise TypeError */
      if (OBJ_GET_TYPE(pa) != OBJ_TYPE_INT && OBJ_GET_TYPE(pa) != OBJ_TYPE_BOOL)
      {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
      }

      *(port+1) = 1<<pin; // Set pin DIRSET to output
      
      if ( ( (pPmInt_t)pa)->val)
        *(port+5) = 1<<pin;     // OUT set
      else
        *(port+6) = 1<<pin;     // OUT clear
    }

    pa = ( *(port+8) & (1<<pin)) ? PM_TRUE : PM_FALSE;
    NATIVE_SET_TOS(pa); // Push our result object onto the stack

    return retval;
    """
    pass


def delay(ms):
    """__NATIVE__
    PmReturn_t retval = PM_RET_OK;

    if(NATIVE_GET_NUM_ARGS() != 1)
    {
      PM_RAISE(retval, PM_RET_EX_TYPE);
      return retval;
    }

    pPmObj_t pa = NATIVE_GET_LOCAL(0);
    if (OBJ_GET_TYPE(pa) == OBJ_TYPE_INT)
    {
      _delay_ms((double) ((pPmInt_t)pa)->val);
    }
    else if (OBJ_GET_TYPE(pa) == OBJ_TYPE_FLT)
    {
      _delay_ms((double) ((pPmFloat_t)pa)->val);
    }
    else
    {
      PM_RAISE(retval, PM_RET_EX_TYPE);
    }

    NATIVE_SET_TOS(PM_NONE);
    return retval;
    """
    pass



# :mode=c:
