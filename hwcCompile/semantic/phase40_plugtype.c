#include <stdio.h>
#include <assert.h>

#include "semantic/phase40.h"


int semPhase40_plugtype(HWC_PlugType *plugType)
{
	if (plugType->phases_completed >= 40)
		return 0;

	if (plugType->phases_begun >= 40)
	{
		/* report user error */
		assert(0);
	}

	if (plugType->phases_completed < 30)
	{
		int rc = semPhase30_plugtype(plugType);
		if (rc != 0)
			return rc;
	}

	if (plugType->phases_completed >= 40)
		return 0;

	// TODO: For now, we skip phase40, out of consideration for time
	plugType->phases_completed = 40;
	return 0;
}

