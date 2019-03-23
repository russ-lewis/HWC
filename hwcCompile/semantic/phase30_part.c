#include <stdio.h>
#include <assert.h>

#include "semantic/phase20.h"
#include "semantic/phase30.h"

#include "semantic/part.h"
#include "semantic/stmt.h"



// Return number of errors
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

	part->phases_begun = 30;


	int retval = 0;

	int i;


	sizes_set_zero(&part->sizes);


	for(i = 0; i < part->decls_len; i++)
	{
		// 0 as an argument because we are within a part
		retval = semPhase30_decl(&part->decls[i], 0);
		sizes_inc(&part->sizes, &part->decls[i].sizes);
	}


	for(i = 0; i < part->stmts_len; i++)
	{
		retval = semPhase30_stmt(&part->stmts[i]);
		sizes_inc(&part->sizes, &part->stmts[i].sizes);
	}


	part->phases_completed = 30;
	return retval;
}


