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


	printf("FIXME: Build the overlap table(s)  %s() at %s:%d\n", __func__, __FILE__,__LINE__);
	retval->   overlapTable = NULL;
	retval->revOverlapTable = NULL;


	int nMem = wiring->numMemRanges;
	int nLog = wiring->numLogicalOperators;
	int nCon = wiring->numConnections;
	int nAsr = wiring->numAsserts;
	int total = nMem+nLog+nCon+nAsr;

	retval->mem     = calloc(total * sizeof(HWC_Graph_Component), 1);
	retval->logic   = retval->mem + nMem;
	retval->conns   = retval->logic + nLog;
	retval->asserts = retval->conns + nCon;

	if (retval->mem == NULL)
	{
		free(retval);
		return NULL;
	}


	// there is some common initialization, which needs to happen to
	// *every* component.  Then we'll do a second pass, which is
	// type-specific (setting ranges).
	for (i=0; i<total; i++)
	{
		// leave the 'partial write' field all zeroes

		retval->mem[i].prev = retval->mem[i].next = &retval->mem[i];
	}

	for (i=0; i<nMem; i++)
	{
		HWC_Wiring_Memory *mem = &wiring->mem[i];

		// we do *NOT* post any input range for memory, because it
		// doesn't read *during* the clock tick, it only reads it
		// when the clock tick has terminated.
		retval->mem[i].in1.start = -1;
		retval->mem[i].in2.start = -1;

		retval->mem[i].out.start = mem->read;
		retval->mem[i].out.end   = mem->read + mem->size;

		retval->mem[i].type =  HWC_GRAPH_COMP_MEM;
		retval->mem[i].mem  = &wiring->mem[i];
	}

	for (i=0; i<nLog; i++)
	{
		HWC_Wiring_Logic *logic = &wiring->logic[i];

		retval->logic[i].in1.start = logic->a;
		retval->logic[i].in1.end   = logic->a + logic->size;

		// input 2: in use in all types of logic except for NOT
		switch (logic->type)
		{
		case WIRING_AND:
		case WIRING_OR:
		case WIRING_XOR:
			retval->logic[i].in2.start = logic->b;
			retval->logic[i].in2.start = logic->b + logic->size;

			retval->logic[i].out.start = logic->out;
			retval->logic[i].out.end   = logic->out + logic->size;
			break;

		case WIRING_EQ:
		case WIRING_NEQ:
			retval->logic[i].in2.start = logic->b;
			retval->logic[i].in2.start = logic->b + logic->size;

			retval->logic[i].out.start = logic->out;
			retval->logic[i].out.end   = logic->out + 1;
			break;

		case WIRING_NOT:
			retval->logic[i].in2.start = -1;

			retval->logic[i].out.start = logic->out;
			retval->logic[i].out.end   = logic->out + logic->size;
			break;

		default:
			assert(0);
		}

		retval->logic[i].type  =  HWC_GRAPH_COMP_LOGIC;
		retval->logic[i].logic = &wiring->logic[i];
	}

	for (i=0; i<nCon; i++)
	{
		HWC_Wiring_Connection *conn = &wiring->conns[i];

		retval->conns[i].in1.start = conn->from;
		retval->conns[i].in1.end   = conn->from + conn->size;

		// input 2: only in use in directed connections.
		if (conn->condition == WIRING_BIT_INVALID)
			retval->conns[i].in2.start = -1;
		else
		{
			retval->conns[i].in2.start = conn->condition;
			retval->conns[i].in2.end   = conn->condition+1;
		}

		retval->conns[i].out.start = conn->to;
		retval->conns[i].out.end   = conn->to + conn->size;

		retval->conns[i].type =  HWC_GRAPH_COMP_CONN;
		retval->conns[i].conn = &wiring->conns[i];
	}

	for (i=0; i<nAsr; i++)
	{
		HWC_Wiring_Assert *asr = &wiring->asserts[i];

		retval->asserts[i].in1.start = asr->bit;
		retval->asserts[i].in1.end   = asr->bit+1;

		retval->asserts[i].in2.start = -1;
		retval->asserts[i].out.start = -1;

		retval->asserts[i].type      =  HWC_GRAPH_COMP_ASSERT;
		retval->asserts[i].assertion = &wiring->asserts[i];
	}


	// we build the forward and reverse lists simply by iterating
	// through the components, and reading the range structs.  All of
	// the type-specific logic is above, we don't have to do anything
	// here.  Cool!

	HWC_Graph_OverlapRange *fwd = calloc((1+2*total)*sizeof(HWC_Graph_OverlapRange), 1);
	HWC_Graph_OverlapRange *rev = calloc((1 + total)*sizeof(HWC_Graph_OverlapRange), 1);
	if (fwd == NULL || rev == NULL)
	{
		free(rev);
		free(fwd);
		free(retval->mem);
		free(retval);
		return NULL;
	}

	int fwdCount = 0, revCount = 0;

	for (i=0; i<total; i++)
	{
		if (retval->mem[i].in1.start != -1)
		{
			fwd[fwdCount].start =  retval->mem[i].in1.start;
			fwd[fwdCount].end   =  retval->mem[i].in1.end;
			fwd[fwdCount].comp  = &retval->mem[i];
			fwdCount++;
		}

		if (retval->mem[i].in2.start != -1)
		{
			fwd[fwdCount].start =  retval->mem[i].in2.start;
			fwd[fwdCount].end   =  retval->mem[i].in2.end;
			fwd[fwdCount].comp  = &retval->mem[i];
			fwdCount++;
		}

		if (retval->mem[i].out.start != -1)
		{
			rev[revCount].start =  retval->mem[i].out.start;
			rev[revCount].end   =  retval->mem[i].out.end;
			rev[revCount].comp  = &retval->mem[i];
			revCount++;
		}
	}

	// put invalid-range terminators on both arrays
	fwd[fwdCount].start = -1;
	rev[revCount].start = -1;

	// shorten both, to save some space
	fwd = realloc(fwd, (fwdCount+1)*sizeof(fwd[0]));
	rev = realloc(rev, (revCount+1)*sizeof(rev[0]));
	assert(fwd != NULL && rev != NULL);

	// sort both arrays
	HWC_Graph_sortOverlapRanges(fwd, fwdCount);
	HWC_Graph_sortOverlapRanges(rev, revCount);


	/* fill out the 'notifyStart' pointers for each output range for each
	 * component; these point into the forward list.  We know that every
	 * output range, from any component, is represented by an element in
	 * the *reverse* list (not the forward one); we have the nice property
	 * that each component has at most one output range, so if we find a
	 * reference to a component in the reverse list, then it is totally
	 * unambigous what output range it refers to.  (Note that this doesn't
	 * apply for the other search, because each component can have two
	 * input ranges.)
	 *
	 * So, our algorithm is as follows:
	 *   - Iterate over the elements in the reverse list
	 *   - For each element in the reverse list, get the component pointer
	 *     from the overlap range object.  We know that we want to fill
	 *     the 'notifyStart' for the *output* range of that component.
	 *   - Keep a running pointer into the *forward* list.  This is
	 *     initialized to point to the start of the forward array.
	 *   - Compare the start of the reverse-list component to the *end* of
	 *     the forward-list component.  If they don't overlap, increment
	 *     through the forward list until they do.
	 *   - The notifyStart for the reverse-list component is equal to the
	 *     current forward-list component
	 */

	HWC_Graph_OverlapRange *curFwd = fwd;
	for (i=0; i<revCount; i++)
	{
		HWC_Graph_Component *comp = rev[i].comp;
		assert(comp->out.start == rev[i].start);
		assert(comp->out.end   == rev[i].end);

		while (curFwd->start != -1 && curFwd->end <= comp->out.start)
			curFwd++;

		comp->out.notifyStart = curFwd;
	}

printf("FIXME: we do not currently populate the 'notifyStart' fields for input ranges.  %s() : %s:%d\n", __func__, __FILE__,__LINE__);


	return retval;
}

