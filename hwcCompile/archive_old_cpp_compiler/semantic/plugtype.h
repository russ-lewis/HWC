#ifndef __SEMANTIC_PLUGTYPE_H__INCLUDED__
#define __SEMANTIC_PLUGTYPE_H__INCLUDED__


#include <stdlib.h>

#include "wiring/fileRange.h"
#include "names.h"
#include "decl.h"



// Maybe just want to reference "plug" struct instead?
typedef struct HWC_PlugType HWC_PlugType;
struct HWC_PlugType
{
	FileRange fr;

	/* this is basically the same thing as the 'sizes.bits' field in
	 * a part.  But I'm using a single int - instead of an HWC_Sizes
	 * struct - because a plugtype cannot possibly have memory,
	 * connections, or other components inside it.
	 */
	int sizeBits;

	/* these track the progress of the semantic phase.  The 'completed'
	 * field tells us which semantic phase is done for this type; calling
	 * a generator function on this type, for one of these phases, is a
	 * NOP.  The 'begun' field tells you what phases have begun, which is
	 * used to detect recursive types.
	 */
	int phases_completed;
	int phases_begun;

	// All names within a plugtype are public
	HWC_NameScope *publicNames;

	// Only stmts allowed in plugtypes are decls.
	HWC_Decl *decls;
	int       decls_len;
};

/*
 * BitType represents the "Bit" primitive in HWC
 *   Its size is 1
 *   It does not have a namescope
 */
extern HWC_PlugType BitType;


void plugtype_dump(HWC_PlugType*, int prefixLen);


#endif // __SEMANTIC_PLUGTYPE_H__INCLUDED__
