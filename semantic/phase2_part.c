#include <stdio.h>
#include <assert.h>

#include "semantic/phase2.h"


int semPhase2_part(HWC_Part *part)
{
	/* phase 1 is executed right at the beginning, when we are doing
	 * phase 1 of the file.
	 */
	assert(part->phases_begun     >= 1);
	assert(part->phases_completed >= 1);


	/* is this a NOP? */
	if (part->phases_completed >= 2)
		return 0;

	/* detect recursive types */
	if (part->phases_begun >= 2)
	{
		/* report user error */
		assert(0);
	}

	/* do we need to do the previous phases first? */
	if (part->phases_completed < 2)
	{
		int rc = semPhase2_part(part);
		if (rc != 0)
			return rc;
	}

	/* maybe, when we did the call above, we completed this phase
	 * already?
	 *
	 * TODO: is this even possible?
	 */
	if (part->phases_completed >= 2)
		return 0;



	assert(0);   // TODO
}

