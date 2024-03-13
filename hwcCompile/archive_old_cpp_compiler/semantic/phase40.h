#ifndef __SEMANTIC_PHASE40_H__INCLUDED__
#define __SEMANTIC_PHASE40_H__INCLUDED__


/* SEMANTIC PHASE 40
 *
 * Phase 40 does array index validation, and reports user errors if the indices
 * are invalid.  It also (of course) does the previous phases before phase 40
 * (as necessary), and recurses into other types when that is required.
 *
 * Since phase 40 
 */

#include "pt/all.h"

#include "semantic/part.h"
#include "semantic/plugtype.h"
#include "semantic/stmt.h"
#include "semantic/expr.h"



/* see the comments in phase20.h - these work the same way. */

int semPhase40_part    (HWC_Part     *part);
int semPhase40_plugtype(HWC_PlugType *plugtype);
int semPhase40_stmt    (HWC_Stmt     *stmt);
int semPhase40_expr    (HWC_Expr     *expr);


#endif

