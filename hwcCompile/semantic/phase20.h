#ifndef __SEMANTIC_PHASE2_H__INCLUDED__
#define __SEMANTIC_PHASE2_H__INCLUDED__


/* SEMANTIC PHASE 20
 *
 * Phase 20 recurses through all of the declarations, and maps identifier
 * expressions to their underlying entities (which might be part types,
 * plugtypes, subparts, or plugs).
 *
 * If any name is not recognized, we will print out an error message and
 * terminate compilation.
 */

#include "pt/all.h"

#include "semantic/names.h"

#include "semantic/part.h"
#include "semantic/plugtype.h"
#include "semantic/stmt.h"
#include "semantic/expr.h"



/* all of these functions return 0 on success, nonzero on error.  The called
 * function is responsible for printing out an error message for the user
 * before returning nonzero; the caller is not expected to print *anything*
 * before terminating.
 */

int semPhase20_part    (HWC_Part     *part);
int semPhase20_plugtype(HWC_PlugType *plugtype);
int semPhase20_stmt    (HWC_Stmt     *stmt);
int semPhase20_expr    (HWC_Expr     *expr, HWC_NameScope *scope);


#endif

