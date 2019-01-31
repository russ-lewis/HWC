#include <stdio.h>
#include <assert.h>

#include "phase20.h"


// Initialization of BitType, an extern var from plugtype.h , which is used for all "Bit" declarations
HWC_PlugType BitType = { .publicNames = NULL, .phases_completed = -1, .phases_begun = -1, .decls = NULL, .decls_len = -1, .size = 1};

/*
Performs phase 20 on the given part.
To be specific, convert all "name"/"char *" variables into pointers to other HWC structs.

Returns how many errors were found during this function.
*/
int semPhase20_plugtype(HWC_PlugType *plugtype)
{
	/* phase 1 is executed right at the beginning, when we are doing
	 * phase 1 of the file.
	 */
	assert(plugtype->phases_begun     >= 10);
	assert(plugtype->phases_completed >= 10);


	/* is this a NOP? */
	if (plugtype->phases_completed >= 20)
		return 0;

	/* detect recursive types */
	if (plugtype->phases_begun >= 20)
	{
		/* report user error */
		assert(0);
	}

	/* do we need to do the previous phases first? */
	if (plugtype->phases_completed < 20)
	{
		int rc = semPhase20_plugtype(plugtype);
		if (rc != 0)
			return rc;
	}

	/* maybe, when we did the call above, we completed this phase
	 * already?
	 *
	 * TODO: is this even possible?
	 */
	if (plugtype->phases_completed >= 20)
		return 0;

	int retval = 0;

	HWC_Decl currDecl;
	int i;
	for(i = 0; i < plugtype->decls_len; i++)
	{
		currDecl = plugtype->decls[i];
		retval = checkDeclName(&currDecl, plugtype->publicNames, 1);
		if(retval != 0)
		{
			// TODO: Error message for when not found in namescope

		}
	}

	// TODO: Returns number of errors found. Good idea?
	return retval;
}

