#include <stdio.h>
#include <assert.h>

#include "semantic/phase20.h"
#include "semantic/phase30.h"
#include "part.h"
#include "stmt.h"

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
	int currConn = 0;
	int currLogic = 0;
	int currMemory = 0;
	int currAssert = 0;

	// TODO: For now, I place all decls at the start of the part, and all stmts later. Is this wise?

	HWC_Decl *currDecl;
	for(i = 0; i < part->decls_len; i++)
	{
		currDecl = &part->decls[i];

		// 0 as an argument because we are within a part
		int size = findDeclSize(currDecl, 0, &currMemory);
		  assert(size >= 0);     // -1 is a compiler logical error!

		// TODO: Is a size of zero valid? No, I would think. Make it a special error value?
		if(size < 0)
		{
			printf("TODO: %s(): Add an error message (marker 1)\n", __func__);
			retval++;
		}
		else
		{
			currDecl->offsets.bits = currIndex;
			currIndex += size;
		}
	}


	HWC_Stmt currStmt;
	for(i = 0; i < part->stmts_len; i++)
	{
		currStmt = part->stmts[i];
		// 0 as an argument because we are within a part
		int size = findStmtSize(&currStmt, &currConn, &currMemory, &currAssert);
		// TODO: Is a size of zero valid? Yes, I would think, for statements. Think about this more.
		if(size < 0)
		{
			printf("TODO: %s(): Add an error message (marker 2)\n", __func__);
			retval++;
		}
		else
		{
			currStmt.offsets.bits = currIndex;
			currIndex += size;
		}
	}


	// TODO: Is this clever, or stupid?
	// ie, the size of something is the index at which we've stopped inserting things
	part->size = currIndex;
	part->numConn = currConn;
	part->numLogic = currLogic;
	part->numMemory = currMemory;
	part->numAssert = currAssert;

	part->phases_completed = 30;
	return retval;
}

// Create helper function that returns size as int or at least sets size for given part/plugtype
// A reply to myself: Isn't that what phase30 should be doing? Why a separate function?
