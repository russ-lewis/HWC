#include <stdio.h>
#include <assert.h>

#include "semantic/phase20.h"
#include "semantic/phase30.h"

#include "semantic/plugtype.h"



int semPhase30_plugtype(HWC_PlugType *plugtype)
{
	if (plugtype->phases_completed >= 30)
		return 0;

	// Recursive definition
	if (plugtype->phases_begun >= 30)
	{
		/* report user error */
		assert(0);
	}

	if (plugtype->phases_completed < 20)
	{
		int rc = semPhase20_plugtype(plugtype);
		if (rc != 0)
			return rc;
	}

	if (plugtype->phases_completed >= 30)
		return 0;

	plugtype->phases_begun = 30;


	int retval = 0;

	int i;


	plugtype->sizeBits = 0;


	for(i = 0; i < plugtype->decls_len; i++)
	{
		// 1 as an argument because we are within a plugtype
		retval = semPhase30_decl(&plugtype->decls[i], 1);

		assert(&plugtype->decls[i].sizes.bits >= 0);
		plugtype->sizeBits += plugtype->decls[i].sizes.bits;

		assert(plugtype->decls[i].sizes.memBits    == 0);
		assert(plugtype->decls[i].sizes.conns      == 0);
		assert(plugtype->decls[i].sizes.memoryObjs == 0);
		assert(plugtype->decls[i].sizes.logicOps   == 0);
		assert(plugtype->decls[i].sizes.asserts    == 0);
	}


	plugtype->phases_completed = 30;
	return retval;
}

