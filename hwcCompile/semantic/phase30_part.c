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
			currDecl->sizes.bits = size;
			currIndex += size;
		}
	}


	HWC_Stmt *currStmt;
	for(i = 0; i < part->stmts_len; i++)
	{
		currStmt = &part->stmts[i];
		// 0 as an argument because we are within a part
		int size = findStmtSize(currStmt, &currIndex, &currConn, &currLogic, &currAssert);
		// TODO: Is a size of zero valid? Yes, I would think, for statements. Think about this more.
		if(size < 0)
		{
			printf("%s:%d:%d: Stmt size was negative [%d].\n", currStmt->fr.filename, currStmt->fr.s.l, currStmt->fr.s.c, size);
			retval++;
		}
		else
		{
			currStmt->offsets.bits = currIndex;
			currStmt->sizes.bits = size;
			//currIndex += size;
		}
	}


	part->sizes.bits       = currIndex;
	part->sizes.memBits    = 0;
	part->sizes.conns      = currConn;
	part->sizes.logicOps   = currLogic;
	part->sizes.memoryObjs = currMemory;
	part->sizes.asserts    = currAssert;

	part->phases_completed = 30;
	return retval;
}

// Create helper function that returns size as int or at least sets size for given part/plugtype
// A reply to myself: Isn't that what phase30 should be doing? Why a separate function?
