#ifndef __SEMANTIC_PHASE2_H__INCLUDED__
#define __SEMANTIC_PHASE2_H__INCLUDED__


/* SEMANTIC PHASE 2
 *
 * Phase 2 does ...TODO...
 */

#include "pt/all.h"

#include "names.h"

#include "part.h"
#include "plugtype.h"



typedef struct HWC_Part     HWC_Part;
typedef struct HWC_PlugType HWC_Plugtype;
typedef struct HWC_Expr     HWC_Expr;

int semPhase20_part    (HWC_Part     *part);
int semPhase20_plugtype(HWC_PlugType *plugtype);
int semPhase20_expr    (HWC_Expr     *expr);


#endif

