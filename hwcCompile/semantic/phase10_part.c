#include <stdio.h>
#include <stdlib.h>
#include <memory.h>

#include <assert.h>

#include "phase10.h"


/*
 * Converts the given PT_part into the semantic's (HWC) version of Parts.
 * As part of this, converts all decls and stmts within the Part into their HWC versions.
 * 
 *  - parsedPart is the current PT part that will be converted into HWC form
 *  - fileScope is the name scope for the entire file
 * 
 * Returns a pointer to the created HWC_Part.
 */
HWC_Part *semPhase10_part(PT_part_decl *parsedPart, HWC_NameScope *fileScope)
{
	HWC_Part *retval = malloc(sizeof(HWC_Part));
	if (retval == NULL)
	{
		assert(0);   // TODO: debug message
		return NULL;
	}
	memset(retval, 0, sizeof(*retval));

	fr_copy   (&retval->fr, &parsedPart->fr);
	sizes_init(&retval->sizes);

	retval->phases_completed = retval->phases_begun = 10;

	// Create publicNames, and make "NULL" its parent
	// ie, 
	retval->publicNames = nameScope_malloc(NULL);
	if (retval->publicNames == NULL)
	{
		assert(0);   // TODO: debug message
		free(retval);
		return NULL;
	}

	// Create privateNames, and make "fileScope" its parent
	retval->privateNames = nameScope_malloc(fileScope);
	if (retval->privateNames == NULL)
	{
		assert(0);   // TODO: debug message
		// TODO: use namescope-specifc free-ing code:    free(retval->publicNames); // TODO: Is this right?
		free(retval);
		return NULL;
	}

	// Implementation can be found in stmts.c
	// Creates an list of decls within this part.
	retval->decls_len = extractHWCdeclsFromPTstmts(parsedPart->stmts, &retval->decls, retval->publicNames, retval->privateNames);

	// Implementation can be found in stmts.c
	// Converts the list of pt_stmts generated by the gramamr into HWC_Stmts
	retval->stmts_len = convertPTstmtIntoHWCstmt(parsedPart->stmts, &retval->stmts);

	// TODO: Perhaps check if either of these functions result in NULL, since that might be invalid

	return retval;
}

