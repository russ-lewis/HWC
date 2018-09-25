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



/* This takes a parse-tree at the file level as input, and returns a
 * newly-created NameScope object for that file.  Inside that NameScope are
 * pointers to the various declarations inside the file; these allow you to
 * find the HWC_Part, HWC_PlugType, etc. pointers.
 *
 * Note that this function does *NOT* create an HWC_File object; that is
 * something which you can create to *contain* this NameScope (when/if that
 * is necessary).
 */
HWC_NameScope *semPhase1_file(PT_File *parsedFile);


#endif

