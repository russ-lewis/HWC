#include <stdio.h>
#include <assert.h>

#include "semantic/phase20.h"
#include "semantic/phase30.h"

int semPhase30_plugtype(HWC_PlugType *plugtype)
{
	if (plugtype->phases_completed >= 30)
		return 0;

	// Recursive definition
	if (plugtype->phases_begun >= 30)
	{
		/* report user error */
		assert(0);
	}

	if (plugtype->phases_completed < 20)
	{
		int rc = semPhase20_plugtype(plugtype);
		if (rc != 0)
			return rc;
	}

	if (plugtype->phases_completed >= 30)
		return 0;

	// TODO: Will bits necessarily go through the sem phases?
	// TODO: Is publicNames a good way to check if a plugtype is a bit?
	//   Note: We do explicitly state this in plugtype.h, so maybe it is.
	// This checks if our plugtype is a bit (ie, it BitType)
	if(plugtype->publicNames == NULL)
		return 0;


	int retval = 0;

	int i;
	int currIndex = 0;
	int currMemory = 0;

	HWC_Decl *currDecl;
	for(i = 0; i < plugtype->decls_len; i++)
	{
		currDecl = &plugtype->decls[i];

		// 1 as an argument because we are within a plugtype
		int size = findDeclSize(currDecl, 1, &currMemory);

		// TODO: Is a size of zero valid? No, I would think. Make it a special error value?
		if(size <= 0)
		{
			// TODO: Error message for I dunno. Recursive definitions?
			retval++;
		}
		else
		{
			currDecl->offsets.bits = currIndex;
			currIndex += size;
		}
	}

	// TODO: Is this clever, or stupid?
	// ie, the size of something is the index at which we've stopped inserting things
	plugtype->size = currIndex;


	plugtype->phases_completed = 30;
	return retval;
}

