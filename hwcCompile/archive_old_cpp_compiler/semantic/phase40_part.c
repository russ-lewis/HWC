#include <stdio.h>
#include <assert.h>

#include "semantic/phase35.h"
#include "semantic/phase40.h"


int semPhase40_part(HWC_Part *part)
{
	if (part->phases_completed >= 40)
		return 0;

	if (part->phases_begun >= 40)
	{
		/* report user error */
		assert(0);
	}

	if (part->phases_completed < 35)
	{
		int rc = semPhase35_part(part);
		if (rc != 0)
			return rc;
	}

	if (part->phases_completed >= 40)
		return 0;

	part->phases_begun = 40;


	// TODO: For now, we skip phase40, out of consideration for time
	part->phases_completed = 40;
	return 0;
}

