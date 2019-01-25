#include <stdio.h>
#include <assert.h>

#include "phase20.h"


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

	/* do we need to do the previous phases first? */
	if (part->phases_completed < 20)
	{
		int rc = semPhase20_part(part);
		if (rc != 0)
			return rc;
	}

	/* maybe, when we did the call above, we completed this phase
	 * already?
	 *
	 * TODO: is this even possible?
	 */
	if (part->phases_completed >= 20)
		return 0;

	HWC_Decl currDecl;
	int i;
	for(i = 0; i < part->decls_len; i++)
	{
		currDecl = part->decls[i];
		if(checkDeclName(&currDecl, part->publicNames, 0) != 0)
		{
			// TODO: Error message for when not found in namescope

		}
	}

	HWC_Stmt currStmt;
	for(i = 0; i < part->stmts_len; i++)
	{
		currStmt = part->stmts[i];
		if(checkStmtName(&currStmt, part->publicNames) != 0)
		{
			// TODO: Error message for when not found in namescope

		}
	}

	assert(0);   // TODO
}

