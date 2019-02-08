#include <stdio.h>
#include <malloc.h>
#include <memory.h>

#include <assert.h>

#include "phase10.h"

/*
Converts the given PT_plugtype_decl into the semantic's (HWC) version of Plugtypes.
As part of this, converts all decls and stmts within the Plugtype into their HWC versions.

 - parsedPlugtype is the current PT plugtype that will be converted into HWC form
 - fileScope is the name scope for the entire file
 NOTE: *fileScope is unused in this function, but has been kept to mirror semPhase10_part

Returns a pointer to the created HWC_Plugtype.
*/
HWC_PlugType *semPhase10_plugtype(PT_plugtype_decl *parsedPlugtype,
                                 HWC_NameScope    *fileScope)
{
	HWC_PlugType *retval = malloc(sizeof(HWC_PlugType));
	if (retval == NULL)
	{
		assert(0);   // TODO: debug message
		return NULL;
	}
	memset(retval, 0, sizeof(*retval));

	retval->phases_completed = retval->phases_begun = 10;

	// Create publicNames, and make "NULL" its parent
	retval->publicNames = nameScope_malloc(NULL);
	if (retval->publicNames == NULL)
	{
		assert(0);   // TODO: debug message
		free(retval);
		return NULL;
	}
	// PlugTypes have no private fields, so only create a public nameScope


	// Implementation can be found in stmts.c
	// Creates an ordered list of decls within this plugtype.
	retval->decls_len = extractHWCdeclsFromPTstmts(parsedPlugtype->stmts, &retval->decls, retval->publicNames, NULL);

	// TODO: Same question as in phase10_part

	return retval;
}
