#ifndef __SEMANTIC_PHASE35_H__INCLUDED__
#define __SEMANTIC_PHASE35_H__INCLUDED__


/* SEMANTIC PHASE 35
 *
 * Phase 35 determines the offsets of all elements in the semantic tree.
 *
 * (See semantic/sizes.h for a long description of sizes and offsets.)
 */

#include "pt/all.h"

typedef struct HWC_Part     HWC_Part;
typedef struct HWC_PlugType HWC_PlugType;
typedef struct HWC_Stmt     HWC_Stmt;
typedef struct HWC_Expr     HWC_Expr;



/* see the comments in phase20.h - these work the same way. */

int semPhase35_part    (HWC_Part     *part);
int semPhase35_plugtype(HWC_PlugType *plugtype);
int semPhase35_stmt    (HWC_Stmt     *stmt);
int semPhase35_expr    (HWC_Expr     *expr, int isLHS);


#endif

