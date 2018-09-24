
/* ------------------- NO ACTUAL CODE IN THIS FILE -------------------
 *
 * This file is simply a wrapper for other headers.  Include this file
 * if you plan to work on the entire parse tree (such as the parser
 * itself); if you only need to work on certain parts of it, you may
 * include only the smaller bits.
 *
 * (When headers in this directory reference other types (by pointer),
 * they will pre-declare the structs in question, so that we don't have
 * a major recursive-headers problem.)
 *
 * I'm not sure that this design is actually a good idea.  But I'm going
 * to give it a try, to encourage us to be able to work more independently.
 *              - Russ, 11 Sep 2018
 *
 * ------------------- NO ACTUAL CODE IN THIS FILE ------------------- */

#include "file.h"
#include "part.h"
#include "plugtype.h"
#include "stmt.h"
#include "type.h"
#include "expr.h"
