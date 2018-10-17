#include <stdio.h>
#include <assert.h>

#include "semantic/phase3.h"
#include "semantic/phase4.h"


int semPhase4_part(HWC_Part *part)
{
	if (part->phases_completed >= 4)
		return 0;

	if (part->phases_begun >= 4)
	{
		/* report user error */
		assert(0);
	}

	if (part->phases_completed < 3)
	{
		int rc = semPhase3_part(part);
		if (rc != 0)
			return rc;
	}

	if (part->phases_completed >= 4)
		return 0;



	assert(0);   // TODO
}

