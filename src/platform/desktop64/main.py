# This file is Copyright 2011 Dean Hall.
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

#
# Runs the interactive interpreter
#


import ipm
class Led(object):
    def __init__(self, pin):
        self.pin = pin

    def set(self, value):
        print 'pin [', self.pin, ']=', value
        _pin(self.pin, 1)

def _pin(pin, config):
    print config
    pass

LED = Led(10)

ipm.ipm({"LED":LED, "_pin":_pin})
