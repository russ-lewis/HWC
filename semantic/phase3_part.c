#include <stdio.h>
#include <assert.h>

#include "semantic/phase2.h"
#include "semantic/phase3.h"


int semPhase3_part(HWC_Part *part)
{
	if (part->phases_completed >= 3)
		return 0;

	if (part->phases_begun >= 3)
	{
		/* report user error */
		assert(0);
	}

	if (part->phases_completed < 2)
	{
		int rc = semPhase2_part(part);
		if (rc != 0)
			return rc;
	}

	if (part->phases_completed >= 3)
		return 0;



	assert(0);   // TODO
}

