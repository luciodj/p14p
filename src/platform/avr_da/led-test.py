#
# playing with LEDs
#
from avr import *
LED0 = Pin(24,7)
LED1 = Pin(25,7)
LED2 = Pin(27,7)
LED3 = Pin(28,7)
LED4 = Pin(29,7)
LEDs = [LED0, LED1, LED2, LED3, LED4]

for led in LEDs:
    led.toggle()
    delay_ms(500)

