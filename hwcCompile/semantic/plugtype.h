#ifndef __SEMANTIC_PLUGTYPE_H__INCLUDED__
#define __SEMANTIC_PLUGTYPE_H__INCLUDED__


#include <malloc.h>

#include "names.h"
#include "decl.h"

// Maybe just want to reference "plug" struct instead?
typedef struct HWC_PlugType HWC_PlugType;
struct HWC_PlugType
{
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

	// TODO: Field for sizeof Part
};

// Presumably put primitive "bit" here

/*
HWC_PlugType *BitType = malloc(sizeof(HWC_PlugType));
BitType->phases_completed = 40;
BitType->publicNames = NULL;
BitType->decls = NULL; // TODO: What kind of decl should be here?
BitType->decls_len = 1;
*/

#endif // __SEMANTIC_PLUGTYPE_H__INCLUDEDED__
