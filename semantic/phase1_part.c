
#include <stdio.h>
#include <malloc.h>
#include <memory.h>

#include <assert.h>

#include "phase1.h"


HWC_Part *semPhase1_part(PT_part_decl *parsedPart, HWC_NameScope *fileNames)
{
	HWC_Part *retval = malloc(sizeof(HWC_Part));
	if (retval == NULL)
	{
		assert(0);   // TODO: debug message
		return NULL;
	}
	memset(retval, 0, sizeof(*retval));


	retval->phases_completed = retval->phases_begun = 1;

	retval->publicNames = nameScope_malloc(fileNames);
	if (retval->publicNames == NULL)
	{
		assert(0);   // TODO: debug message
		free(retval);
		return NULL;
	}


	assert(0);    // TODO: fill in stmts


	return retval;
}

