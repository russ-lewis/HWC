#include <stdio.h>
#include <assert.h>

#include "semantic/phase35.h"
#include "semantic/phase40.h"


int semPhase40_plugtype(HWC_PlugType *plugtype)
{
	if (plugtype->phases_completed >= 40)
		return 0;

	if (plugtype->phases_begun >= 40)
	{
		/* report user error */
		assert(0);
	}

	if (plugtype->phases_completed < 35)
	{
		int rc = semPhase35_plugtype(plugtype);
		if (rc != 0)
			return rc;
	}

	if (plugtype->phases_completed >= 40)
		return 0;

	plugtype->phases_begun = 40;


	// TODO: For now, we skip phase40, out of consideration for time
	plugtype->phases_completed = 40;
	return 0;
}

