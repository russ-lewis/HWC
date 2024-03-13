#include <stdio.h>
#include <assert.h>

#include "semantic/phase30.h"
#include "semantic/phase35.h"

#include "semantic/plugtype.h"



int semPhase35_plugtype(HWC_PlugType *plugtype)
{
	if (plugtype->phases_completed >= 35)
		return 0;

	// Recursive definition
	if (plugtype->phases_begun >= 35)
	{
		/* report user error */
		assert(0);
	}

	if (plugtype->phases_completed < 30)
	{
		int rc = semPhase30_plugtype(plugtype);
		if (rc != 0)
			return rc;
	}

	if (plugtype->phases_completed >= 35)
		return 0;

	plugtype->phases_begun = 35;


	/* see comments in phase35_part() */
	if (plugtype->decls_len > 0)
	{
		sizes_set_zero(&plugtype->decls[0].offsets);

		int i;
		for (i=1; i<plugtype->decls_len; i++)
		{
			sizes_add(&plugtype->decls[i  ].offsets,
			          &plugtype->decls[i-1].offsets, &plugtype->decls[i-1].sizes);
		}
	}


	plugtype->phases_completed = 35;
	return 0;
}

