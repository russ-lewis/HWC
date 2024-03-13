#include <stdio.h>
#include <assert.h>

#include "semantic/phase30.h"
#include "semantic/phase35.h"

#include "semantic/part.h"
#include "semantic/stmt.h"



// Returns number of errors
int semPhase35_part(HWC_Part *part)
{
	if (part->phases_completed >= 35)
		return 0;

	// Recursive definition
	if (part->phases_begun >= 35)
	{
		/* report user error */
		assert(0);
	}

	if (part->phases_completed < 30)
	{
		int rc = semPhase30_part(part);
		if (rc != 0)
			return rc;
	}

	if (part->phases_completed >= 35)
		return 0;

	part->phases_begun = 35;


	/* this will be used by the statement array, after the decls
	 * are done.  It's the base, plus all of the decl sizes (if any).
	 */
	HWC_Sizes afterDecls;

	/* trivial case: if there are no declarations, do nothing */
	if (part->decls_len == 0)
		sizes_set_zero(&afterDecls);
	else
	{
		/* the offset of the first declaration is equal to the offset
		 * of the entire part.
		 */
		sizes_set_zero (&part->decls[0].offsets);

		/* each successive decl is the previous one, plus the size of
		 * the previous one.
		 */
		int i;
		for (i=1; i<part->decls_len; i++)
		{
			sizes_add(&part->decls[i  ].offsets,
			          &part->decls[i-1].offsets, &part->decls[i-1].sizes);
		}

		/* save the offset from the last decl as the start of the
		 * statement offsets.
		 */
		sizes_add(&afterDecls,
		          &part->decls[part->decls_len-1].offsets,
		          &part->decls[part->decls_len-1].sizes);
	}


	/* loop over the statements.  Same basic logic as the decl loop above. */
	if (part->stmts_len > 0)
	{
		sizes_copy(&part->stmts[0].offsets, &afterDecls);
		semPhase35_stmt(&part->stmts[0]);

		int i;
		for (i=1; i<part->stmts_len; i++)
		{
			sizes_add(&part->stmts[i  ].offsets,
			          &part->stmts[i-1].offsets, &part->stmts[i-1].sizes);

			semPhase35_stmt(&part->stmts[i]);
		}
	}


	part->phases_completed = 35;
	return 0;
}


