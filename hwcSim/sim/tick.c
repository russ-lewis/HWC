#include <stdio.h>
#include <assert.h>

#include "sim/tick.h"

#include "sim/dlist.h"
#include "sim/bits.h"



static void dispatch_one(HWC_Graph_Component*);

void HWC_Sim_doTick(HWC_Sim_State *sim)
{
	int i,j;

	// wipe the memory in the bit space.  We do not wipe it at the *end*
	// of a cycle, since the caller might want to inspect it, maybe.
	HWC_Sim_bitsWipe(sim->bits, sim->numBits);


	// copy all memory cells into their read sides
	for (i=0; i<sim->graph->wiring->numMemRanges; i++)
	{
		int read = sim->graph->wiring->mem[i].read;
		int size = sim->graph->wiring->mem[i].size;
		int save_pos = sim->memOffsets[i];

		HWC_Graph_OverlapRange *notify = sim->graph->mem[i].out.notifyStart;

		HWC_Sim_copyRawToBitSpace(sim->bits,   // dest buffer
		                          read, size,  // dest pos, size

		                          sim->memBits,  // src buffer
		                          save_pos,      // src offset

		                          notify);   // notify?  Yes, please!
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
		int write_base = sim->graph->wiring->mem[i].write;
		int size       = sim->graph->wiring->mem[i].size;
		int save_pos   = sim->memOffsets[i];

		for (j=0; j<size; j++)
			if (HWC_Sim_bit_isValid(sim->bits, write_base+j))
			{
				int val = HWC_Sim_readBit(sim->bits, write_base+j);
				HWC_Sim_writeRawBit(sim->memBits,
				                    save_pos+j,
				                    val);
			}
	}
}


static void dispatch_one(HWC_Graph_Component *cur)
{
	assert(0);
}

