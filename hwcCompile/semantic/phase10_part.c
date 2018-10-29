
#include <stdio.h>
#include <malloc.h>
#include <memory.h>

#include <assert.h>

#include "phase10.h"
#include "stmt.c" // Ask Russ about a better way to include this. Obviously through Makefile, but right now it's too complex for me to understand :(

HWC_Part *semPhase10_part(PT_part_decl *parsedPart, HWC_NameScope *fileScope)
{
	HWC_Part *retval = malloc(sizeof(HWC_Part));
	if (retval == NULL)
	{
		assert(0);   // TODO: debug message
		return NULL;
	}
	memset(retval, 0, sizeof(*retval));


	retval->phases_completed = retval->phases_begun = 10;

	retval->publicNames = nameScope_malloc(fileNames);
	if (retval->publicNames == NULL)
	{
		assert(0);   // TODO: debug message
		free(retval);
		return NULL;
	}

	// Implementation can be found in stmts.c
	retval->stmts_len = convertPTstmtIntoHWCstmt(parsedPart->stmts, retval->stmts);

	assert(0);    // TODO: fill in stmts


	return retval;
}

