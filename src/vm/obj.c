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
#define __FILE_ID__ 0x0F


/**
 * \file
 * \brief Object Type
 *
 * Object type operations.
 */


#include "pm.h"


/* Returns true if the obj is false */
int8_t
obj_isFalse(pPmObj_t pobj)
{
    C_ASSERT(pobj != C_NULL);

    switch (OBJ_GET_TYPE(pobj))
    {
        case OBJ_TYPE_NON:
            /* None evaluates to false, so return true */
            return C_TRUE;

        case OBJ_TYPE_INT:
            /* Only the integer zero is false */
            return ((pPmInt_t)pobj)->val == 0;

#ifdef HAVE_FLOAT
        case OBJ_TYPE_FLT:
            /* The floats 0.0 and -0.0 are false */
            return (((pPmFloat_t) pobj)->val == 0.0)
                || (((pPmFloat_t) pobj)->val == -0.0);
#endif /* HAVE_FLOAT */

        case OBJ_TYPE_STR:
            /* An empty string is false */
            return ((pPmString_t)pobj)->length == 0;

        case OBJ_TYPE_TUP:
            /* An empty tuple is false */
            return ((pPmTuple_t)pobj)->length == 0;

        case OBJ_TYPE_LST:
            /* An empty list is false */
            return ((pPmList_t)pobj)->length == 0;

        case OBJ_TYPE_DIC:
            /* An empty dict is false */
            return ((pPmDict_t)pobj)->length == 0;

        case OBJ_TYPE_BOOL:
            /* C int zero means false */
            return ((pPmBoolean_t) pobj)->val == 0;

        default:
            /*
             * The following types are always not false:
             * CodeObj, Function, Module, Class, ClassInstance.
             */
            return C_FALSE;
    }
}


/* Returns true if the item is in the container object */
PmReturn_t
obj_isIn(pPmObj_t pobj, pPmObj_t pitem)
{
    PmReturn_t retval = PM_RET_NO;
    pPmObj_t ptestItem;
    int16_t i;
    uint8_t c;

    switch (OBJ_GET_TYPE(pobj))
    {
        case OBJ_TYPE_TUP:
            /* Iterate over tuple to find item */
            for (i = 0; i < ((pPmTuple_t)pobj)->length; i++)
            {
                PM_RETURN_IF_ERROR(tuple_getItem(pobj, i, &ptestItem));

                if (obj_compare(pitem, ptestItem) == C_SAME)
                {
                    retval = PM_RET_OK;
                    break;
                }
            }
            break;

        case OBJ_TYPE_STR:
            /* Raise a TypeError if item is not a string */
            if ((OBJ_GET_TYPE(pitem) != OBJ_TYPE_STR))
            {
                retval = PM_RET_EX_TYPE;
                break;
            }

            /* Empty string is alway present */
            if (((pPmString_t)pitem)->length == 0)
            {
                retval = PM_RET_OK;
                break;
            }

            /* Raise a ValueError if the string is more than 1 char */
            else if (((pPmString_t)pitem)->length != 1)
            {
                retval = PM_RET_EX_VAL;
                break;
            }

            /* Iterate over string to find char */
            c = ((pPmString_t)pitem)->val[0];
            for (i = 0; i < ((pPmString_t)pobj)->length; i++)
            {
                if (c == ((pPmString_t)pobj)->val[i])
                {
                    retval = PM_RET_OK;
                    break;
                }
            }
            break;

        case OBJ_TYPE_LST:
            /* Iterate over list to find item */
            for (i = 0; i < ((pPmList_t)pobj)->length; i++)
            {
                PM_RETURN_IF_ERROR(list_getItem(pobj, i, &ptestItem));

                if (obj_compare(pitem, ptestItem) == C_SAME)
                {
                    retval = PM_RET_OK;
                    break;
                }
            }
            break;

        case OBJ_TYPE_DIC:
            /* Check if the item is one of the keys of the dict */
            retval = dict_getItem(pobj, pitem, &ptestItem);
            if (retval == PM_RET_EX_KEY)
            {
                retval = PM_RET_NO;
            }
            break;

        default:
            retval = PM_RET_EX_TYPE;
            break;
    }

    return retval;
}


int8_t
obj_compare(pPmObj_t pobj1, pPmObj_t pobj2)
{
    PmReturn_t retval;
    pPmObj_t pobj;

    C_ASSERT(pobj1 != C_NULL);
    C_ASSERT(pobj2 != C_NULL);

    /* Check if pointers are same */
    if (pobj1 == pobj2)
    {
        return C_SAME;
    }

    /* If types are different, objs must differ */
    if (OBJ_GET_TYPE(pobj1) != OBJ_GET_TYPE(pobj2))
    {
        return C_DIFFER;
    }

    /* If object is an instance, get the thing it contains */
    if (OBJ_GET_TYPE(pobj1) == OBJ_TYPE_CLI)
    {
        retval = dict_getItem((pPmObj_t)((pPmInstance_t)pobj1)->cli_attrs,
                              PM_NONE,
                              &pobj);
        PM_RETURN_IF_ERROR(retval);
        pobj1 = pobj;
    }
    if (OBJ_GET_TYPE(pobj2) == OBJ_TYPE_CLI)
    {
        retval = dict_getItem((pPmObj_t)((pPmInstance_t)pobj2)->cli_attrs,
                              PM_NONE,
                              &pobj);
        PM_RETURN_IF_ERROR(retval);
        pobj2 = pobj;
    }

    /* If types are different, objs must differ */
    if (OBJ_GET_TYPE(pobj1) != OBJ_GET_TYPE(pobj2))
    {
        return C_DIFFER;
    }

    /* Otherwise handle types individually */
    switch (OBJ_GET_TYPE(pobj1))
    {
        case OBJ_TYPE_NON:
            return C_SAME;

        case OBJ_TYPE_INT:
            return ((pPmInt_t)pobj1)->val ==
                ((pPmInt_t)pobj2)->val ? C_SAME : C_DIFFER;

#ifdef HAVE_FLOAT
        case OBJ_TYPE_FLT:
        {
            pPmObj_t r_pobj;

            float_compare(pobj1, pobj2, &r_pobj, COMP_EQ);
            return (r_pobj == PM_TRUE) ? C_SAME : C_DIFFER;
        }
#endif /* HAVE_FLOAT */

        case OBJ_TYPE_STR:
            return string_compare((pPmString_t)pobj1, (pPmString_t)pobj2);

        case OBJ_TYPE_TUP:
        case OBJ_TYPE_LST:
        case OBJ_TYPE_BYA:
            return seq_compare(pobj1, pobj2);

        case OBJ_TYPE_DIC:
            return dict_compare(pobj1, pobj2);

        default:
            break;
    }

    /* All other types would need same pointer to be true */
    return C_DIFFER;
}


PmReturn_t
obj_print(pPmObj_t pobj, uint8_t is_expr_repr, uint8_t is_nested)
{
    PmReturn_t retval = PM_RET_OK;

    C_ASSERT(pobj != C_NULL);

    /* Something gets printed unless it's None in an unnested expression */
    if (!((OBJ_GET_TYPE(pobj) == OBJ_TYPE_NON) && is_expr_repr && !is_nested))
    {
        gVmGlobal.somethingPrinted = C_TRUE;
    }

    switch (OBJ_GET_TYPE(pobj))
    {
        case OBJ_TYPE_NON:
            if (!is_expr_repr || is_nested)
            {
                sli_puts((uint8_t *)"None");
            }
            break;
        case OBJ_TYPE_INT:
            retval = int_print(pobj);
            break;
#ifdef HAVE_FLOAT
        case OBJ_TYPE_FLT:
            retval = float_print(pobj);
            break;
#endif /* HAVE_FLOAT */
        case OBJ_TYPE_STR:
            retval = string_print(pobj, (is_expr_repr || is_nested));
            break;
        case OBJ_TYPE_TUP:
            retval = tuple_print(pobj);
            break;
        case OBJ_TYPE_LST:
            retval = list_print(pobj);
            break;
        case OBJ_TYPE_DIC:
            retval = dict_print(pobj);
            break;
        case OBJ_TYPE_BOOL:
            sli_puts(
                (((pPmBoolean_t)pobj)->val == C_TRUE)
                ? (uint8_t *)"True"
                : (uint8_t *)"False");
            break;

        case OBJ_TYPE_CLI:
            {
                pPmObj_t pobj2;

                retval = dict_getItem((pPmObj_t)((pPmInstance_t)pobj)->cli_attrs,
                                      PM_NONE,
                                      (pPmObj_t *)&pobj2);
                if ((retval == PM_RET_OK)
                    && (OBJ_GET_TYPE(pobj2) == OBJ_TYPE_BYA))
                {
                    retval = bytearray_print(pobj2);
                    break;
                }
            }

        case OBJ_TYPE_COB:
        case OBJ_TYPE_MOD:
        case OBJ_TYPE_CLO:
        case OBJ_TYPE_FXN:
        case OBJ_TYPE_CIM:
        case OBJ_TYPE_NIM:
        case OBJ_TYPE_NOB:
        case OBJ_TYPE_THR:
        case OBJ_TYPE_CIO:
        case OBJ_TYPE_MTH:
        case OBJ_TYPE_SQI:
        {
            uint8_t buf[17];
            sli_puts((uint8_t *)"<obj type 0x");
            sli_btoa16(OBJ_GET_TYPE(pobj), buf, sizeof(buf), C_TRUE);
            sli_puts(buf);
            sli_puts((uint8_t *)" @ 0x");
            sli_ptoa16((intptr_t)pobj, buf, sizeof(buf), C_TRUE);
            sli_puts(buf);
            retval = plat_putByte('>');
            break;
        }

        default:
            /* Otherwise raise a TypeError */
            PM_RAISE(retval, PM_RET_EX_TYPE);
            break;
    }
    return retval;
}


PmReturn_t
obj_repr(pPmObj_t pobj, pPmObj_t *r_pstr)
{
    uint8_t tBuffer[32];
    PmReturn_t retval = PM_RET_OK;
    uint8_t const *pcstr = (uint8_t *)tBuffer;;

    C_ASSERT(pobj != C_NULL);

    switch (OBJ_GET_TYPE(pobj))
    {
        case OBJ_TYPE_INT:
            sli_ltoa10(((pPmInt_t)pobj)->val, tBuffer, sizeof(tBuffer));
            retval = string_new(&pcstr, r_pstr);
            break;

#ifdef HAVE_FLOAT
        case OBJ_TYPE_FLT:
            /* #212: Use homebrew float formatter */
            retval = sli_ftoa(((pPmFloat_t)pobj)->val, tBuffer, sizeof(tBuffer));
            PM_RETURN_IF_ERROR(retval);
            retval = string_new(&pcstr, r_pstr);
            break;
#endif /* HAVE_FLOAT */

        default:
            /* Otherwise raise a TypeError */
            PM_RAISE(retval, PM_RET_EX_TYPE);
            break;
    }

    return retval;
}
