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

	retval->bits = HWC_Sim_bitsAlloc(retval->numBits);
	if (retval->bits == NULL)
	{
		free(retval);
		return NULL;
	}

	if (graph->wiring->numMemRanges == 0)
	{
		retval->memOffsets = NULL;
		retval->memBits    = NULL;
	}
	else
	{
		retval->memOffsets = HWC_Sim_buildMemOffsets(graph->wiring);
		if (retval->memOffsets == NULL)
		{
			free(retval->bits);
			free(retval);
			return NULL;
		}

		retval->memBits = HWC_Sim_memBitsAlloc(retval->memOffsets[graph->wiring->numMemRanges]);
		if (retval->memBits == NULL)
		{
			free(retval->memOffsets);
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

