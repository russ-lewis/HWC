#include <stdio.h>
#include <assert.h>

#include "semantic/phase20.h"
#include "semantic/phase30.h"


// Return number of errors
// MAKE SURE RETVAL OF PHASE 20 AND 30 ARE ZERO
int semPhase30_part(HWC_Part *part)
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

	int i;
	int currIndex = 0;

	// TODO: For now, I place all decls at the start of the part, and all stmts later. Is this wise?

	HWC_Decl currDecl;
	for(i = 0; i < part->decls_len; i++)
	{
		currDecl = part->decls[i];
		// 0 as an argument because we are within a part
		int size = findDeclSize(currDecl, 0);
		// TODO: Is a size of zero valid? No, I would think. Make it a special error value?
		if(size <= 0)
		{
			// TODO: Error message for I dunno. Recursive definitions?
			retval++;
		}
		else
		{
			currDecl->index = currIndex;
			currIndex += size;
		}
	}


	HWC_Stmt currStmt;
	for(i = 0; i < part->stmts_len; i++)
	{
		currStmt = part->stmts[i];
		// 0 as an argument because we are within a part
		int size = findDeclSize(currStmt, 0);
		// TODO: Is a size of zero valid? Yes, I would think, for statements. Think about this more.
		if(size < 0)
		{
			// TODO: Error message for I dunno. Recursive definitions?
			retval++;
		}
		else
		{
			currStmt->index = currIndex;
			currIndex += size;
		}
	}


	// TODO: Is this clever, or stupid?
	// ie, the size of something is the index at which we've stopped inserting things
	part->size = currIndex;

	return retval;
}

// Create helper function that returns size as int or at least sets size for given part/plugtype
// A reply to myself: Isn't that what phase30 should be doing? Why a separate function?
