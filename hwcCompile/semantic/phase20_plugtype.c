#include <stdio.h>
#include <assert.h>

#include "phase20.h"


int semPhase20_plugtype(HWC_PlugType *plugtype)
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



	assert(0);   // TODO
}

