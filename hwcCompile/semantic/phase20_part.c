#include <stdio.h>
#include <assert.h>

#include "phase20.h"

#include "stmt.h"

/*
Performs phase 20 on the given part.
To be specific, convert all "name"/"char *" variables into pointers to other HWC structs.

Returns how many errors were found during this function.
*/
int semPhase20_part(HWC_Part *part)
{
	/* phase 1 is executed right at the beginning, when we are doing
	 * phase 1 of the file.
	 */
	assert(part->phases_begun     >= 10);
	assert(part->phases_completed >= 10);


	/* is this a NOP? */
	if (part->phases_completed >= 20)
		return 0;

	/* detect recursive types */
	if (part->phases_begun >= 20)
	{
		/* report user error */
		assert(0);
	}


	/* maybe, when we did the call above, we completed this phase
	 * already?
	 *
	 * TODO: is this even possible?
	 */
	if (part->phases_completed >= 20)
		return 0;

	int retval = 0;

	HWC_Decl currDecl;
	int i;
	for(i = 0; i < part->decls_len; i++)
	{
		currDecl = part->decls[i];
		int numError = checkDeclName(&currDecl, part->privateNames, 0);
		if(numError != 0)
		{
			// TODO: Better error message for when not found in namescope?
			fprintf(stderr, "Phase 20, part: %d errors found with decl of %s!\n", numError, currDecl.typeName);
		}
		retval += numError;
	}

	// There's no iteration for expr-essions because they're found within stmts.
	// TODO: Can a Stmt appear in both this list and as part of another stmt? 
	HWC_Stmt currStmt;
	for(i = 0; i < part->stmts_len; i++)
	{
		currStmt = part->stmts[i];
		int numError = checkStmtName(&currStmt, part->privateNames);
		if(numError != 0)
			fprintf(stderr, "Phase 20, part: %d errors found with stmt of %s!\n", numError, currStmt.name);
		retval += numError;
	}

	part->phases_completed = 20;

	// Returns number of errors found, if something else doesn't break
	// TODO: Good idea?
	return retval;
}


