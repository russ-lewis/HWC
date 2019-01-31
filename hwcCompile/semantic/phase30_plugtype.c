#include <stdio.h>
#include <assert.h>

#include "semantic/phase20.h"
#include "semantic/phase30.h"


int semPhase30_plugtype(HWC_PlugType *plugtype)
{
	if (part->phases_completed >= 30)
		return 0;

	// Recursive definition
	if (part->phases_begun >= 30)
	{
		/* report user error */
		assert(0);
	}

	if (part->phases_completed < 20)
	{
		int rc = semPhase20_part(part);
		if (rc != 0)
			return rc;
	}

	if (part->phases_completed >= 30)
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

	assert(0);   // TODO

	// TODO: Returns number of errors found. Good idea?
	return retval;
}

