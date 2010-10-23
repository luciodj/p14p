/*
 * PyMite - A flyweight Python interpreter for 8-bit and larger microcontrollers.
 * Copyright 2002 Dean Hall.  All rights reserved.
 * PyMite is offered through one of two licenses: commercial or open-source.
 * See the LICENSE file at the root of this package for licensing details.
 */

/**
 * Test for Issue #90
 * Create new lib function to return system time
 */


#include "pm.h"

extern unsigned char usrlib_img[];


int main(void)
{
    PmReturn_t retval;
    
    retval = pm_init(MEMSPACE_PROG, usrlib_img);
    PM_RETURN_IF_ERROR(retval);

    retval = pm_run((uint8_t *)"t090");
    return (int)retval;
}
