#include <stdio.h>
#include <assert.h>

#include "sim/tick.h"

#include "sim/dlist.h"
#include "sim/bits.h"



static int dispatch_one(HWC_Sim_State*, HWC_Graph_Component*,
                        int (*callback)(HWC_Sim_State*,int,int));

static int dispatch_conn(HWC_Sim_State*, HWC_Graph_Component*,
                         int (*callback)(HWC_Sim_State*,int,int));

static int dispatch_logic(HWC_Sim_State*, HWC_Graph_Component*,
                          int (*callback)(HWC_Sim_State*,int,int));

static int dispatch_assert(HWC_Sim_State*, HWC_Graph_Component*,
                           int (*callback)(HWC_Sim_State*,int,int));



void HWC_Sim_doTick(HWC_Sim_State *sim,
                    int (*write_callback)(HWC_Sim_State*,int,int),
                    int (*mem_update_callback)(HWC_Sim_State*,HWC_Wiring_Memory*))
{
	HWC_Sim_tick_init(sim);

	while (HWC_Sim_tick_hasTODO(sim) || HWC_Sim_tick_hasDeferred(sim))
	{
		HWC_Sim_tick_dispatchSome    (sim, -1, write_callback);
		HWC_Sim_tick_dispatchDeferred(sim,     write_callback);
	}

	HWC_Sim_tick_finish(sim, mem_update_callback);

	printf("\n");
	printf("...end of tick...\n");
	printf("\n");
}



void HWC_Sim_tick_init(HWC_Sim_State *sim)
{
	int i;

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
}



int HWC_Sim_tick_hasTODO(HWC_Sim_State *sim)
{
	return dlist_not_empty(&sim->todo);
}

int HWC_Sim_tick_hasDeferred(HWC_Sim_State *sim)
{
	return dlist_not_empty(&sim->deferred);
}



int HWC_Sim_tick_dispatchSome(HWC_Sim_State *sim,
                              int count,
                              int (*callback)(HWC_Sim_State*, int pos, int len))
{
	assert(count == -1 || count > 0);

	int soFar = 0;
	while (HWC_Sim_tick_hasTODO(sim) &&
	       (count == -1 || soFar < count))
	{
		HWC_Graph_Component *cur;

		assert(dlist_not_empty(&sim->todo));
		cur = dlist_remove_head(&sim->todo);

		int retval = dispatch_one(sim, cur, callback);
		if (retval != 0)
			break;

		soFar++;
	}

	return soFar;
}



int HWC_Sim_tick_dispatchDeferred(HWC_Sim_State *sim,
                                  int (*callback)(HWC_Sim_State*, int,int))
{
	if (   HWC_Sim_tick_hasTODO(sim) ||
	     ! HWC_Sim_tick_hasDeferred(sim))
	{
		return 0;
	}

	HWC_Graph_Component *cur = dlist_remove_head(&sim->deferred);
	dispatch_one(sim, cur, callback);
	return 1;
}



int HWC_Sim_tick_finish(HWC_Sim_State *sim,
                        int (*callback)(HWC_Sim_State*, HWC_Wiring_Memory*))
{
	int i,j;

	int updates = 0;

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

				printf("mem changed: element=%d bit=%d: val=%d\n", i,j, val);

				updates++;
			}
	}

	return updates;
}



static int dispatch_one(HWC_Sim_State *sim, HWC_Graph_Component *cur,
                        int (*callback)(HWC_Sim_State*, int,int))
{
	switch(cur->type)
	{
	case HWC_GRAPH_COMP_CONN:
		return dispatch_conn(sim, cur, callback);

	case HWC_GRAPH_COMP_LOGIC:
		return dispatch_logic(sim, cur, callback);

	case HWC_GRAPH_COMP_ASSERT:
		return dispatch_assert(sim, cur, callback);

	case HWC_GRAPH_COMP_MEM:   // memory components should *NEVER* get on the TODO list!
	default:
		assert(0);
		return -1;   // never get here, but make the compiler happy
	}
}


static int dispatch_conn(HWC_Sim_State *sim, HWC_Graph_Component *graph_conn,
                         int (*callback)(HWC_Sim_State*, int,int))
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

	if (callback != NULL)
		assert(0);

	return 0;   // keep going
}


static int dispatch_logic(HWC_Sim_State *sim, HWC_Graph_Component *graph_logic,
                          int (*callback)(HWC_Sim_State*, int,int))
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

	if (callback != NULL)
		assert(0);

	return 0;   // keep going
}


static int dispatch_assert(HWC_Sim_State *sim, HWC_Graph_Component *graph_assert,
                           int (*callback)(HWC_Sim_State*, int,int))
{
	HWC_Wiring_Assert *wiring_assert = graph_assert->assertion;

	assert(0);   // TODO: implement me



	if (callback != NULL)
		assert(0);

	return 0;   // keep going
}

