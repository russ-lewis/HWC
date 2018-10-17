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

/* TODO: comments */

int semPhase2_part    (HWC_Part     *part);
int semPhase2_plugtype(HWC_PlugType *plugtype);


#endif

