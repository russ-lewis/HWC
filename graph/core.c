#include <stdio.h>
#include <assert.h>
#include <stdlib.h>

#include "wiring/core.h"

#include "graph/core.h"



HWC_Graph *HWC_Graph_build(HWC_Wiring *wiring)
{
	int i;

	HWC_Graph *retval = malloc(sizeof(HWC_Graph));
	if (retval == NULL)
		return NULL;

	retval->wiring = wiring;


	retval->mem = calloc(wiring->numMemRanges * sizeof(HWC_Graph_Component), 1);
	if (retval->mem == NULL)
	{
		free(retval);
		return NULL;
	}

	for (i=0; i<wiring->numMemRanges; i++)
	{
		HWC_Wiring_Memory *mem = &wiring->mem[i];

		retval->mem[i].in1.start = mem->write;
		retval->mem[i].in1.end   = mem->write + mem->size;
		// don't set the searchStart for 'in', unless we have a reverse overlapTable

		retval->mem[i].in2.start = -1;

		retval->mem[i].out.start = mem->read;
		retval->mem[i].out.end   = mem->read + mem->size;
printf("TODO: set the search start!  %s() at %s:%d\n", __func__, __FILE__,__LINE__);

		// leave the 'partial write' field all zeroes

		retval->mem[i].prev = retval->mem[i].next = &retval->mem[i];

		retval->mem[i].type =  HWC_GRAPH_COMP_MEM;
		retval->mem[i].mem  = &wiring->mem[i];
	}


	printf("FIXME: Implement more!  %s() at %s:%d\n", __func__, __FILE__,__LINE__);
#if 0
	retval->logic   = NULL;
	retval->conns   = NULL;
	retval->asserts = NULL;
#endif

	return retval;
}

