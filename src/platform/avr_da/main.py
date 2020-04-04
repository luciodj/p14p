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

import ipm
from avr import *
from sys import *
LED = Pin(45, 7)
BTN = Button(46)

def bench(fn, times=1000):
    t=time()
    i=0
    while i < times:
        fn()
        i += 1
    return time()-t - 250*times/1000 # remove the empty function call cost

ipm.ipm({"bench":bench, "LED":LED, "BTN":BTN, "Pin":Pin, "Spi":Spi, "delay":delay})
# b=bytearray(1)
# ipm.ipm()
