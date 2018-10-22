#ifndef __SEMANTIC_PHASE1_H__INCLUDED__
#define __SEMANTIC_PHASE1_H__INCLUDED__


/* SEMANTIC PHASE 1
 *
 * This declares the functions that are used to perform "phase 1" of the
 * semantic work for HWC: this converts the parse tree into a set of
 * internal HWC objects; this phase focuses on name resolution.
 */

#include "pt/all.h"

#include "names.h"

#include "part.h"
#include "plugtype.h"



/* This takes a parse-tree at the file level as input, and returns a
 * newly-created NameScope object for that file.  Inside that NameScope are
 * pointers to the various declarations inside the file; these allow you to
 * find the HWC_Part, HWC_PlugType, etc. pointers.
 *
 * Note that this function does *NOT* create an HWC_File object; that is
 * something which you can create to *contain* this NameScope (when/if that
 * is necessary).
 *
 * Also, note that you will be passed an object with a single refCount; if
 * you discard this NameScope, then you must decrement the refcount on it.
 */
HWC_NameScope *semPhase10_file(PT_file *parsedFile);



typedef struct HWC_Part     HWC_Part;
typedef struct HWC_PlugType HWC_Plugtype;

HWC_Part     *semPhase10_part    (PT_part_decl     *parsedPart,     HWC_NameScope *fileScope);
HWC_Plugtype *semPhase10_plugtype(PT_plugtype_decl *parsedPlugtype, HWC_NameScope *fileScope);


#endif

