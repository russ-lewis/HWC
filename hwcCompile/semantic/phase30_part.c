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



	assert(0);   // TODO
}


// Create helper function that returns size as int or at least sets size for given part/plugtype
