#ifndef __SIM_GRAPH_C__INCLUDED__
#define __SIM_GRAPH_C__INCLUDED__


#include <wiring/core.h>



typedef struct HWC_sim_graph       HWC_sim_graph;
typedef struct HWC_sim_update_list HWC_sim_update_list;

struct HWC_sim_graph
{
	/* one int for each bit in the simulation. */
	int *bits;

	/* an array of arrays; the array is marked by an element with type=0 */
	HWC_sim_update_list **updateTable;

	/* this queue holds queue (the TODO list) of update entries above.  In
	 * FIFO mode, we use both the head and tail pointers; in LIFO mode, we
	 * only use the head.  In both cases, we always remove from the head;
	 * the difference between FIFO and LIFO is how we add new elements.
	 */
	HWC_sim_update_list *queueHead;
	HWC_sim_update_list *queueTail;



	/* we need to know the length of the array of memory units, since they
	 * are the start of all computation - and also because we need to copy
	 * from the 'write' side to the 'read' side at the end of the clock
	 * cycle.
	 */
	int               memoryCount;
	HWC_WiringMemory *memory;

	/* we do *NOT* need to know the length of these arrays, since we never
	 * iterate through them - we simply access them from a 
	 */
	HWC_WiringLogic      *logic;
	HWC_WiringConnection *connections;
	HWC_WiringAssert     *asserts;
};


enum {
	SIM_UPDATE__END_OF_LIST = 0,

	SIM_UPDATE_LOGIC  = 1,
	SIM_UPDATE_CONNECTION,
	SIM_UPDATE_ASSERT,
};

struct HWC_sim_update_list
{
	int type;   /* SIM_UPDATE_* */
	int indx;

	/* this is used for building the 'TODO' list, which is a FIFO (or
	 * LIFO) queue.
	 */
	int onQueue;
	HWC_sim_update_list *next;
};


HWC_sim_graph *HWC_sim_buildGraph(HWC_Wiring*);


#endif

