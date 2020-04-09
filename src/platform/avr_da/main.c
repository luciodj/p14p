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

#define HEAP_SIZE 10000

#include <stdio.h>

int main(void)
{      
    uint8_t heap[HEAP_SIZE] ;
    PmReturn_t retval;

    retval = plat_init();
    PM_RETURN_IF_ERROR(retval);
    // printf("plat returned:%d", retval);
    
    while (1) {
    retval = pm_init(heap, HEAP_SIZE);
    printf("pm_init returned:%d", retval);
    PM_RETURN_IF_ERROR(retval);
    retval = pm_run((uint8_t *)"main");
    printf("pm_run returned : %d", retval);
    puts("\nRestarting...");
    }
    return (int)retval;
}
