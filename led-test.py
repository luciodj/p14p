#
# playing with LEDs
#
LED0 = Pin(24,5)
LED1 = Pin(25,5)
LED2 = Pin(27,5)
LED3 = Pin(28,5)
LED4 = Pin(29,5)
LEDs = [LED1, LED2, LED3, LED4]

def display(value):
    for led in LEDs:
        led.set(value & 1)
        value >>= 1

for i in range(17):
    LED.toggle()
    display(i)
    while(not BTN.pressed()):
        pass

