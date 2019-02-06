#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <assert.h>

#include "graph/core.h"

#include "sim/state.h"
#include "sim/bits.h"



HWC_Sim_State *HWC_Sim_buildState(HWC_Graph *graph)
{
	HWC_Sim_State *retval = malloc(sizeof(HWC_Sim_State));
	if (retval == NULL)
		return NULL;

	retval->numBits = graph->wiring->numBits;
	assert(retval->numBits > 0);

	retval->bits    = HWC_Sim_bitsAlloc(retval->numBits);
	if (retval->bits == NULL)
	{
		free(retval);
		return NULL;
	}

	retval->numMemBits = HWC_Sim_calcNumMemBits(graph->wiring);
	if (retval->numMemBits == 0)
		retval->memBits = NULL;
	else
	{
		retval->memBits = HWC_Sim_memBitsAlloc(retval->numMemBits);
		if (retval->memBits == NULL)
		{
			free(retval->bits);
			free(retval);
			return NULL;
		}
	}

	memset(&retval->todo,     0, sizeof(retval->todo));
	memset(&retval->deferred, 0, sizeof(retval->deferred));

	retval->todo    .next = retval->todo    .prev = &retval->todo;
	retval->deferred.next = retval->deferred.prev = &retval->deferred;

	retval->graph = graph;

	return retval;
}

