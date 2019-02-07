#include <stdio.h>
#include <assert.h>

#include "sim/tick.h"

#include "sim/dlist.h"
#include "sim/bits.h"



static void dispatch_one(HWC_Sim_State*, HWC_Graph_Component*);

static void dispatch_conn(HWC_Sim_State*, HWC_Graph_Component*);
static void dispatch_logic(HWC_Sim_State*, HWC_Graph_Component*);
static void dispatch_assert(HWC_Sim_State*, HWC_Graph_Component*);



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

		dispatch_one(sim, cur);
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

				printf("mem: i=%d j=%d: val=%d\n", i,j, val);
			}
	}

	printf("\n");
	printf("...end of tick...\n");
	printf("\n");
}



static void dispatch_one(HWC_Sim_State *sim, HWC_Graph_Component *cur)
{
	switch(cur->type)
	{
	case HWC_GRAPH_COMP_MEM:
		assert(0);    // memory components should *NEVER* get on the TODO list!

	case HWC_GRAPH_COMP_CONN:
		dispatch_conn(sim, cur);
		break;

	case HWC_GRAPH_COMP_LOGIC:
		dispatch_logic(sim, cur);
		break;

	case HWC_GRAPH_COMP_ASSERT:
		dispatch_assert(sim, cur);
		break;

	default:
		assert(0);
	}
}


static void dispatch_conn(HWC_Sim_State *sim, HWC_Graph_Component *graph_conn)
{
	HWC_Wiring_Connection *wiring_conn = graph_conn->conn;

	if (wiring_conn->condition != WIRING_BIT_INVALID)
	{
assert(0);   // TODO: implement me
	}


	// TODO: partial writes and deferred writes are not implemented yet.
	assert(HWC_Sim_bit_rangeIsValid(sim->bits, wiring_conn->from, wiring_conn->size));

	HWC_Sim_copyBitRange(sim->bits,
	                     wiring_conn->to, wiring_conn->from,
	                     wiring_conn->size,
	                     graph_conn->out.notifyStart);
}


static void dispatch_logic(HWC_Sim_State *sim, HWC_Graph_Component *graph_logic)
{
	HWC_Wiring_Logic *wiring_logic = graph_logic->logic;

	// TODO: partial writes and deferred writes are not implemented yet.
	assert(HWC_Sim_bit_rangeIsValid(sim->bits, wiring_logic->a, wiring_logic->size));
	if (graph_logic->in2.start != -1)
		assert(HWC_Sim_bit_rangeIsValid(sim->bits, wiring_logic->b, wiring_logic->size));

	// TODO: support larger logic operations
	assert(wiring_logic->size <= 8*sizeof(unsigned long));

	unsigned long a,b;
	a = HWC_Sim_readBitRange(sim->bits, wiring_logic->a, wiring_logic->size);
	if (graph_logic->in2.start != -1)
		b = HWC_Sim_readBitRange(sim->bits, wiring_logic->b, wiring_logic->size);

	unsigned long out;
	int           out_size;

	switch (wiring_logic->type)
	{
	case WIRING_AND:
		out = a & b;
		out_size = wiring_logic->size;
		break;

	case WIRING_OR:
		out = a | b;
		out_size = wiring_logic->size;
		break;

	case WIRING_XOR:
		out = a ^ b;
		out_size = wiring_logic->size;
		break;

	case WIRING_NOT:
		out = ~a & ((1<<wiring_logic->size)-1);
		out_size = wiring_logic->size;
		break;

	case WIRING_EQ:
		out = (a == b ? 1:0);
		out_size = 1;
		break;

	case WIRING_NEQ:
		out = (a != b ? 1:0);
		out_size = 1;
		break;

	default:
		assert(0);
	}

	HWC_Sim_writeBitRange(sim->bits, wiring_logic->out, out_size, out,
	                      graph_logic->out.notifyStart);
}


static void dispatch_assert(HWC_Sim_State *sim, HWC_Graph_Component *graph_assert)
{
	HWC_Wiring_Assert *wiring_assert = graph_assert->assertion;

	assert(0);   // TODO: implement me
}

