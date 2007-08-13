/*
 * PyMite - A flyweight Python interpreter for 8-bit microcontrollers and more.
 * Copyright 2002 Dean Hall
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

/**
 * VM feature configuration
 *
 * Compile time switches to include features or save space.
 *
 * Log
 * ---
 *
 * 2007/07/04   Introduce RPP and RPM
 * 2007/01/09   #75: First (P.Adelt)
 */


#ifndef FEATURES_H_
#define FEATURES_H_

/**
 * When defined, bytecodes PRINT_ITEM and PRINT_NEWLINE are supported. Along
 * with these, helper routines in the object type are compiled in that allow
 * printing of the object.
 */
#define HAVE_PRINT

/**
 * Remote PyMite Management (HAVE_RPM) implicitly needs Remote PyMite Protocol
 * (HAVE_RPP). It alters the behaviour of PRINT_ITEM/PRINT_EXPR in interp.c to
 * emit RPP per-thread messages instead of the raw data. This way, the receiver
 * can distinguish output of different threads.
 */
#define HAVE_RPM

#ifdef HAVE_RPM
  #define HAVE_RPP
#endif

#endif /*FEATURES_H_ */
