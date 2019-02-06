#ifndef _GRAPH_COMPONENTS_H__INCLUDED_
#define _GRAPH_COMPONENTS_H__INCLUDED_


#include "wiring/core.h"



// body declared in "graph/overlapTable.h"
typedef struct HWC_Graph_OverlapRange HWC_Graph_OverlapRange;



typedef struct HWC_Graph_Component HWC_Graph_Component;
struct HWC_Graph_Component
{
	/* common fields, used by all types.  Ranges that are not in use
	 * have start=-1.  start values are inclusive, end values are
	 * exclusive.
	 */

	struct {
		int start,end;
		HWC_Graph_OverlapRange *notifyStart;
	} in1,in2, out;


	/* doubly-linked list, used for the 'todo/pending' lists during
	 * simulation.
	 */
	HWC_Graph_Component *prev,*next;


	/* this stores partial-write information.  To look at this, always
	 * first check the integer, which can take on 2 magic values:
	 *
	 *    0 - this component has not posted *ANY* output, but might
	 *        later.  This includes components which don't produce
	 *        any bit output (such as assert) but which definitely
	 *        need to read the inputs when they become available.
	 *
	 *   -1 - this compnent will *NOT* post any output in the future,
	 *        either because it has actually written the values, or
	 *        because it's a conditional connection, and it has
	 *        decided not to write because the condition was false.
	 *
	 * If the integer is any *other* value, then it is interpreted as
	 * information about a partial write, meaning that the component has
	 * set *some* of the output bits but not all of them.  This is
	 * interpreted in two ways, based on the size of the output:
	 *
	 *    If the output size is <= the number of bits in the integer,
	 *    then the integer is used as a bitmask, with 1s indicating
	 *    which bit(s) have been written so far.
	 *
	 *    Otherwise, the pointer is used, and it is a pointer to a
	 *    malloc()ed buffer, which contains the bitmask.
	 */

	union {
		long  l;
		char *buf;
	} partialWrite;


	int type;	// see enum below
	union {
		HWC_Wiring_Memory     *mem;
		HWC_Wiring_Logic      *logic;
		HWC_Wiring_Connection *conn;
		HWC_Wiring_Assert     *assertion;
	};
};

enum HWC_Graph_ComponentType
{
	HWC_GRAPH_COMP_MEM = 1,
	HWC_GRAPH_COMP_LOGIC,
	HWC_GRAPH_COMP_CONN,
	HWC_GRAPH_COMP_ASSERT,
};



#endif
