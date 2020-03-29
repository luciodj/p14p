/*
# This file is Copyright 2007 Dean Hall.
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
*/

/** Sample PyMite application */


#include "pm.h"
#include "avr/pgmspace.h"

#define HEAP_SIZE 15000
  

extern unsigned char  usrlib_img[];

#include <stdio.h>

int main(void)
{      
    uint8_t heap[HEAP_SIZE] __attribute__((aligned((4))));
    PmReturn_t retval;

    while (1) {
        retval = pm_init(heap, HEAP_SIZE, MEMSPACE_PROG, usrlib_img);
        PM_RETURN_IF_ERROR(retval);
        retval = pm_run((uint8_t *)"main");
        puts("\nRestarting...");
    }
    return (int)retval;
}