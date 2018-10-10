#ifndef __SEMANTIC_PHASE4_H__INCLUDED__
#define __SEMANTIC_PHASE4_H__INCLUDED__


/* SEMANTIC PHASE 4
 *
 * Phase 4 does array index validation, and reports user errors if the indices
 * are invalid.  It also (of course) does the previous phases before phase 4
 * (as necessary), and recurses into other types when that is required.
 */

#include "pt/all.h"

#include "names.h"

#include "part.h"
#include "plugtype.h"



typedef struct HWC_Part     HWC_Part;
typedef struct HWC_PlugType HWC_Plugtype;

/* TODO: comments */

HWC_NameScope *semPhase4_part    (HWC_Part     *part);
HWC_NameScope *semPhase4_plugtype(HWC_PlugType *plugtype);


#endif

