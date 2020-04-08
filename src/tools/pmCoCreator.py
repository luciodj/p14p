#! /usr/bin/env python

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

"""
Generates a C source and header file from one or more .py source files.
The output C code is structs that define the code objects from the .py files
The output C header is types that are used in the VM and
extern declarations of some global objects.
"""


import os, sys
import pmConstantPool
from pmCoFilter import co_filter_factory


# Issue 227: Raise an error at build-time if CPython version is not supported
assert sys.version_info[0] == 2 and sys.version_info[1] == 7, \
    "P14p REQUIRES CPython 2.7.x in order to support the correct bytecodes"


PM_GENERATED_OBJS_FN = "pm_generated_objs.c"
PM_GENERATED_TYPES_FN = "pm_generated_types.h"

NATIVE_INDICATOR = "__NATIVE__"
NATIVE_INDICATOR_LENGTH = len(NATIVE_INDICATOR)

MODULE_IDENTIFIER = "<module>"

# The prefix of global C variables in the VM
GLOBAL_PREFIX = "pm_global_"

# Expose these COs with the given name for easy access in the VM
co_to_expose = {
    "Generator": GLOBAL_PREFIX + "co_generator",
    "Exception": GLOBAL_PREFIX + "co_exception",
}


none = type(None)
code = type(compile("None", "None", "exec"))
mod = ("Mod",)
native = ("__native__",)
typeval = {
    none: "OBJ_TYPE_NON",
    bool: "OBJ_TYPE_BOOL",
    int: "OBJ_TYPE_INT",
    float: "OBJ_TYPE_FLT",
    str: "OBJ_TYPE_STR",
    tuple: "OBJ_TYPE_TUP",
    code: "OBJ_TYPE_COB",
    native: "OBJ_TYPE_NOB",
}
ctype = {
    none: "PmNone%s_t",
    bool: "PmBoolean%s_t",
    int: "PmInt%s_t",
    float: "PmFloat%s_t",
    str: "PmString%s_t",
    tuple: "PmTuple%s_t",
    code: "PmCo%s_t",
    native: "PmNo%s_t",
}


cname_kpool = pmConstantPool.pmConstantPool()
crepr_kpool = {}
ordered_cnames = []
string_sizes = set()
tuple_sizes = set()


def gen_obj_name():
    """Generates object names and returns the name as a string."""
    obj_count = 0
    while True:
        yield "o%d" % obj_count
        obj_count += 1
gen_next_obj_name = gen_obj_name().next


def wrap(s, width=75):
    """Wraps a crepr string by inserting a newline after a comma.
    """
    b = bytearray(s)
    end_b = len(b) - width - 1
    i = 0
    while i < end_b:
        i = b.find(',', i + width)
        if b[i+1] == ' ':
            b[i+1] = os.linesep
        else:
            b.insert(i+1, os.linesep)
    return str(b)


def _byte_crepr(c):
    """Returns c as a printable ascii char surrounded by single quotes,
    or a decimal number as string.   Comma, apostrophe and backslash
    are excluded to avoid trouble with C char syntax.
    """
    n = ord(c)
    if n >= 32 and n < 127 and n != 39 and n != 44 and n != 92:
        return repr(c)
    else:
        return str(n)


def header(typ, nm, size=""):
    ctyp = ctype[typ] % str(size)
    return "%s PM_PLAT_PROGMEM %s = {PM_DECLARE_OD(%s, sizeof(%s))" \
           % (ctyp, nm, typeval[typ], ctyp)


def string_to_crepr(o, nm):
    len_o = len(o)
    string_sizes.add(len_o)
    chars = "%s," * len_o % tuple(map(_byte_crepr, o))
    return "%s, %d, %s, {%s'\\0'}};\n" \
           % (header(str, nm, len_o), len_o, "C_NULL", chars)


def tuple_to_crepr(o, nm):
    len_o = len(o)
    tuple_sizes.add(len_o)
    objs = "(pPmObj_t)&%s," * len_o % tuple(map(obj_to_cvar, o))
    # Issue 238: Add support for compilers that don't allow zero-sized arrays
    if len_o == 0: return "%s, %d};\n" % (header(tuple, nm, len_o), len_o)
    return "%s, %d, {%s}};\n" % (header(tuple, nm, len_o), len_o, objs)


def co_to_crepr(co, cvarnm):
    fco = filter_co(co)

    # Check if the code object indicates native code
    if co.co_consts and type(co.co_consts[0]) == str \
       and co.co_consts[0][:NATIVE_INDICATOR_LENGTH] == NATIVE_INDICATOR:

        # If the module has a native header, copy it's C code
        # Put directly in the kpool so it appears before CO's field's objs
        if co.co_name == MODULE_IDENTIFIER:
            varname = "mod_" + cvarnm
            crepr_kpool[varname] = "/* Module %s:%d */\n%s\n" \
                % (co.co_filename, co.co_firstlineno,
                   co.co_consts[0][NATIVE_INDICATOR_LENGTH:])
            ordered_cnames.append(varname)

        # Otherwise it's a native function
        else:
            native_cvarnm = "n" + cvarnm
            return '/* %s:%d %s */\nPmReturn_t %s(pPmFrame_t *ppframe)\n' \
                '{\n#line %d "%s"\n%s\n}\n\n%s, %d, %s};\n' \
                % (co.co_filename, co.co_firstlineno + 1, co.co_name,
                   native_cvarnm, co.co_firstlineno + 1, co.co_filename,
                   co.co_consts[0][NATIVE_INDICATOR_LENGTH:],
                   header(native, cvarnm), co.co_argcount, native_cvarnm)

    # HACK: append co_filename and co_name to the co_consts tuple to reduce
    # the size of the code object structure by two pointers.
    # co_filename and co_name are extracted via the co API in codeobj.c
    fco['co_consts'] += (fco['co_filename'], fco['co_name'],)

    # Prep data to fill into the CO structure definition
    d = {}
    d['hdr'] = header(code, cvarnm)
    d['co_code'] = obj_to_cvar(co.co_code)
    d['co_names'] = obj_to_cvar(fco['co_names'])
    d['co_consts'] = obj_to_cvar(fco['co_consts'])
    d['co_cellvars'] = obj_to_cvar(fco['co_cellvars'])
    d['co_lnotab'] = obj_to_cvar(co.co_lnotab)

    # Format the CO structure definition
    crepr = bytearray(
        "%(hdr)s, "
        "(pPmString_t)&%(co_code)s, "
        "PM_REFERENCE_LNOTAB(%(co_lnotab)s), "
        "(pPmTuple_t)&%(co_names)s, "
        "(pPmTuple_t)&%(co_consts)s, "
        "(pPmTuple_t)&%(co_cellvars)s, "
        % d)
    crepr.extend("%d, %d, %d, %d, %d, %d};\n" %
        (co.co_firstlineno,
         co.co_argcount,
         co.co_flags & 0xFF,
         co.co_stacksize,
         co.co_nlocals,
         len(co.co_freevars)))
    return str(crepr)


# Table of functions that turn a Python obj to its C struct representation
objtype_to_crepr_func_table = {
    none: lambda o, nm: "%s};\n" % (header(none, nm)),
    bool: lambda o, nm: "%s, %d};\n" % (header(bool, nm), int(o)),
    int: lambda o, nm: "%s, %d};\n" % (header(int, nm), o),
    float: lambda o, nm: "%s, %s};\n" % (header(float, nm), repr(o)),
    str: string_to_crepr,
    tuple: tuple_to_crepr,
    code: co_to_crepr,
}


def obj_to_cvar(o, name=None, typ=None):
    """Returns varname of o; either fetched from the constant pool or created.
    Puts the C variable name in the constant pool and the C representation
    in a table (keyed by C variable name).
    """

    if o in cname_kpool:
        return cname_kpool[o]

    # If object is a code-object that needs to be exposed, use its special name
    vartype = typ or type(o)
    if vartype == code and o.co_name in co_to_expose:
        name = co_to_expose[o.co_name]

    # Otherwise use the given name or generate one
    varname = name or gen_next_obj_name()
    cname_kpool[o] = varname

    # Create the C representation of the object and store it
    _obj_to_crepr = objtype_to_crepr_func_table[vartype]
    crepr_kpool[varname] = _obj_to_crepr(o, varname)
    ordered_cnames.append(varname)

    return varname


def process_globals():
    """Adds VM globals and useful constants to the constant pool.
    """
    cobjs = (None, -1,0,1,2,3,4,5,6,7,8,9,True,False,
             "__bi","__md","code","__init__","next",(),"",
             "Generator", "Exception", "bytearray",
             "None", "False", "True", "__code__")
    cnames = map(lambda x: GLOBAL_PREFIX + x,
                 ("none", "negone", "zero", "one", "two", "three", "four",
                  "five", "six", "seven", "eight", "nine", "true", "false",
                  "string_bi", "string_md", "string_code", "string_init",
                  "string_next", "empty_tuple", "empty_string",
                  "string_generator", "string_exception", "string_bytearray",
                  "string_none", "string_false", "string_true", "string_code_attr",))
    map(obj_to_cvar, cobjs, cnames)


def process_modules(filenames):
    table_lines = ["\n/* Module table */\n"
                   "PmInt_t PM_PLAT_PROGMEM * const %smodule_table_len_ptr = &%s;\n"
                   "PmModuleEntry_t PM_PLAT_PROGMEM %smodule_table[] =\n{\n"
                   % (GLOBAL_PREFIX, obj_to_cvar(len(filenames)),
                      GLOBAL_PREFIX)]

    splitext = os.path.splitext
    basename = os.path.basename
    for fn in filenames:
        modulename = splitext(basename(fn))[0]
        co = compile(open(fn).read(), fn, 'exec')
        nm = obj_to_cvar(co)
        table_lines.append("    {(pPmString_t)&%s, (pPmCo_t)&%s}, /* %s */\n" %
                                  (obj_to_cvar(modulename), nm, fn))
    table_lines.append("};\n")
    return table_lines


def process_and_print(filenames, output_path):
    # Order of process_* is important
    process_globals()
    module_table_lines = process_modules(filenames)

    # Now put all the lines of output into order
    cfile_lines = ['#include <stdint.h>\n#include "pm.h"\n\n'
                   '#define __FILE_ID__ 0x0A\n\n'
                   '/* Code object constant pool */\n']
    for cname in ordered_cnames:
        cfile_lines.extend(crepr_kpool[cname])
    cfile_lines.extend(module_table_lines)

    # Write the generated objects
    f = open(os.path.join(output_path, PM_GENERATED_OBJS_FN), 'w')
    f.writelines(cfile_lines)
    f.close()

    # Write the generated types files
    f = open(os.path.join(output_path, PM_GENERATED_TYPES_FN), 'w')
    for size in string_sizes:
        f.write("PM_DECLARE_STRING_TYPE(%d);\n" % size)
    # Issue 238: Add support for compilers that don't allow zero-sized arrays
    tuple_sizes.remove(0)
    f.write("typedef struct PmTuple0_s { PmObjDesc_t od; int16_t length; } PmTuple0_t;\n")
    
    for size in tuple_sizes:
        f.write("PM_DECLARE_TUPLE_TYPE(%d);\n" % size)
    f.close()


if __name__ == "__main__":
    filter_co = co_filter_factory()
    output_path = sys.argv[1]
    assert os.path.isdir(output_path), "Expect an output path directory"
    filenames = sys.argv[2:]
    assert len(filenames) > 0, "Expect list of .py files as args"
    process_and_print(filenames, output_path)

