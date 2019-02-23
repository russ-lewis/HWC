#include <stdio.h>
#include <assert.h>

#include "phase20.h"


// Initialization of BitType, an extern var from plugtype.h , which is used for all "Bit" declarations
HWC_PlugType BitType = {
	.publicNames = NULL,

	.phases_completed = 40,
	.phases_begun     = 40,

	.decls     = NULL,
	.decls_len = 0,

	.size = 1
};


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


	/* maybe, when we did the call above, we completed this phase
	 * already?
	 *
	 * TODO: is this even possible?
	 */
	if (plugtype->phases_completed >= 20)
		return 0;

	HWC_Decl *currDecl;
	int i;
	for(i = 0; i < plugtype->decls_len; i++)
	{
		currDecl = &plugtype->decls[i];
		int numError = checkDeclName(currDecl, plugtype->publicNames, 1);
		if(numError != 0)
			return numError;
	}

	plugtype->phases_completed = 20;

	return 0;
}

