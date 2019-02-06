#include <stdio.h>
#include <assert.h>

#include "sim/tick.h"
#include "sim/dlist.h"



static void dispatch_one(HWC_Graph_Component*);

void HWC_Sim_doTick(HWC_Sim_State *sim)
{
	int i;

	// copy all memory cells into their read sides
	for (i=0; i<sim->graph->wiring->numMemRanges; i++)
	{
		assert(0);
	}


	while (dlist_not_empty(&sim->todo) || dlist_not_empty(&sim->deferred))
	{
		HWC_Graph_Component *cur;

		if (dlist_not_empty(&sim->todo))
			cur = dlist_remove_head(&sim->todo);
		else
			cur = dlist_remove_head(&sim->deferred);

		dispatch_one(cur);
	}


	// copy the 'write' bits (if any) of each memory cell into the
	// memory storage.
	for (i=0; i<sim->graph->wiring->numMemRanges; i++)
	{
		assert(0);
	}
}


static void dispatch_one(HWC_Graph_Component *cur)
{
	assert(0);
}

