#ifndef __SEMANTIC_PHASE30_H__INCLUDED__
#define __SEMANTIC_PHASE30_H__INCLUDED__


/* SEMANTIC PHASE 30
 *
 * Phase 30 determines the sizes  of all elements in the semantic tree.
 *
 * Note that we originally planned to have this also generate the
 * offsets, but we decided to move that into Phase 35.
 *
 * (See semantic/sizes.h for a long description of sizes and offsets.)
 */

#include "pt/all.h"

typedef struct HWC_Part     HWC_Part;
typedef struct HWC_PlugType HWC_PlugType;
typedef struct HWC_Decl     HWC_Decl;
typedef struct HWC_Stmt     HWC_Stmt;
typedef struct HWC_Expr     HWC_Expr;



/* see the comments in phase20.h - these work the same way. */

int semPhase30_part    (HWC_Part     *part);
int semPhase30_plugtype(HWC_PlugType *plugtype);
int semPhase30_decl    (HWC_Decl     *decl, int isInPlugtype);
int semPhase30_stmt    (HWC_Stmt     *stmt);
int semPhase30_expr    (HWC_Expr     *expr);


#endif

