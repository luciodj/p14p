/*
# This file is Copyright 2003, 2006, 2007, 2009, 2010 Dean Hall.
#
# This file is part of the PyMite VM.
# The PyMite VM is free software: you can redistribute it and/or modify
# it under the terms of the GNU GENERAL PUBLIC LICENSE Version 2.
#
# The PyMite VM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# A copy of the GNU GENERAL PUBLIC LICENSE Version 2
# is seen in the file COPYING in this directory.
*/


#undef __FILE_ID__
#define __FILE_ID__ 0x0E


/**
 * \file
 * \brief Module Object Type
 *
 * Module object type operations.
 */


#include "pm.h"


static Mod_platLoadCodeObject_t mod_platLoadCodeObjectFunctionPointer = C_NULL;


PmReturn_t
mod_new(pPmObj_t pco, pPmObj_t *pmod)
{
    PmReturn_t retval;
    uint8_t *pchunk;
    pPmObj_t pobj;
    uint8_t objid;

    /* If it's not a code obj, raise TypeError */
    if (OBJ_GET_TYPE(pco) != OBJ_TYPE_COB)
    {
        PM_RAISE(retval, PM_RET_EX_TYPE);
        return retval;
    }

    /* Alloc and init func obj */
    retval = heap_getChunk(sizeof(PmFunc_t), &pchunk);
    PM_RETURN_IF_ERROR(retval);
    *pmod = (pPmObj_t)pchunk;
    OBJ_SET_TYPE(*pmod, OBJ_TYPE_MOD);
    ((pPmFunc_t)*pmod)->f_co = (pPmCo_t)pco;
    ((pPmFunc_t)*pmod)->f_attrs = C_NULL;
    ((pPmFunc_t)*pmod)->f_globals = C_NULL;
    ((pPmFunc_t)*pmod)->f_defaultargs = C_NULL;
    ((pPmFunc_t)*pmod)->f_closure = C_NULL;

    /* Alloc and init attrs dict */
    heap_gcPushTempRoot(*pmod, &objid);
    retval = dict_new(&pobj);
    heap_gcPopTempRoot(objid);
    ((pPmFunc_t)*pmod)->f_attrs = (pPmDict_t)pobj;

    /* A module's globals is the same as its attrs */
    ((pPmFunc_t)*pmod)->f_globals = (pPmDict_t)pobj;

    return retval;
}


PmReturn_t
mod_import(pPmObj_t pstr, pPmObj_t *pmod)
{
    pPmCo_t pco = C_NULL;
    PmReturn_t retval = PM_RET_NO;
    uint8_t i;

    /* If it's not a string obj, raise SyntaxError */
    if (OBJ_GET_TYPE(pstr) != OBJ_TYPE_STR)
    {
    printf("wrong type in module returns %x\n", OBJ_GET_TYPE(pstr));
        PM_RAISE(retval, PM_RET_EX_SYNTAX);
        return retval;
    }

    /* #234: Support platform-specific module loading */
    if (mod_platLoadCodeObjectFunctionPointer != C_NULL)
    {
        retval = mod_platLoadCodeObjectFunctionPointer(pstr, (pPmObj_t *)&pco);

        /* Return now if an exception occured */
        if ((retval != PM_RET_NO) && (retval != PM_RET_OK))
        {
            return retval;
        }
    }

    /* If the platform-callback didn't run or didn't find the code object */
    if (retval != PM_RET_OK)
    {
        /* Try to find the module in the table */
        for (i = 0; i < pm_global_module_table_len_ptr->val; i++)
        {
            if (string_compare(pm_global_module_table[i].pnm, (pPmString_t)pstr) == C_SAME)
            {
                pco = pm_global_module_table[i].pco;
                break;
            }
        }
    }

    /* If code obj was not found, raise ImportError */
    if (pco == C_NULL)
    {
        PM_RAISE(retval, PM_RET_EX_IMPRT);
        return retval;
    }

    retval = mod_new((pPmObj_t)pco, pmod);

    return retval;
}


PmReturn_t
mod_setPlatLoadCodeObjectFunctionPointer(Mod_platLoadCodeObject_t pfunc)
{
    mod_platLoadCodeObjectFunctionPointer = pfunc;
    return PM_RET_OK;
}
