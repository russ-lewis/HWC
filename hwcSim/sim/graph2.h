#ifndef __SIM_GRAPH2_H__INCLUDED__
#define __SIM_GRAPH2_H__INCLUDED__


#include <wiring/core.h>



typedef struct HWC_Sim_Graph     HWC_Sim_Graph;
typedef struct HWC_Sim_Component HWC_Sim_Component;


struct HWC_Sim_Component
{
	// these are for the todo/pending lists, see the Graph struct
	// below.
	HWC_Sim_Component *next, *prev;


	// TODO: more fields!
};


struct HWC_Sim_Graph
{
	/* how many bits in the total simulation?  This is useful because we
	 * want to remap the 'bits' array below, after each clock cycle.
	 */
	int  numBits;

	/* two bits for each bit in the simulation. */
	char *bits_audit_to_make_sure_you_alloc_2x;



	/* this is the current queue of components which are pending
	 * notification.  It is a doubly-linked, circular list, so the node
	 * below is a dummy node.
	 *
	 * When dispatching nodes from this list, we always pull from the head.
	 * In LIFO mode, we also add at the head, and thus this functions as
	 * a stack.  In FIFO mode, we always add at the tail, so it functions
	 * as a queue.
	 *
	 * Note, however, that any "touch" of a node will cause the node to
	 * be moved in the list; since there are two different places where
	 * the node might be (and we're not sure, at any given moment, which
	 * list a node is in), our strategy is always to *remove* a node from
	 * its current position, and place it into its new position.
	 *
	 * DEFERRED NODES
	 *
	 * There are actually *two* lists; a TODO list, and a "deferred" list.
	 * Nodes in the TODO list represent nodes that have recently had one
	 * of their inputs updated, and we haven't yet had time to look at
	 * them; when we finally look at them, we will decide whether or not
	 * it is now possible to write to the output.
	 *
	 * If a component is able to write to its *entire* output, then it
	 * will definitely do so.  However, if it is only able to write to
	 * *part* of the output, (or, if the value that it is writing is
	 * FLOATING), then it will "defer" itself; it makes no changes to the
	 * bits, but will add itself to the (tail) of the deferred list.
	 *
	 * If such a component later has one of its inputs updated, it will
	 * be removed from where it currently is, and placed on the TODO
	 * list; then it will be considered again later.  It might post its
	 * results, or it might be deferred again.
	 *
	 * Nodes may stay on the "deferred" list for a long time; this happens
	 * when they defer themselves once, and then their inputs are not
	 * updated again.  They will not be reconsidered again, until they are
	 * moved back to the TODO list (because their inputs were update) -
	 * or, until the TODO list becomes empty.
	 *
	 * When the TODO list becomes empty, we start dispatching from the
	 * deferred list.  In this mode, components will always write out
	 * *everything* that they are able to write.  Nodes which have written
	 * out partial output might still write again (for instance, maybe the
	 * partial write they performed allows us to determine the value of
	 * some other inputs to the same component - or maybe this component
	 * was only delayed because of *another* deferred component).
	 *
	 * WHY DEFER?
	 *
	 * Think about situations where you have a single connection, which
	 * moves many, many bits all at once, but where the various bits are
	 * calculated by a large number of individual pieces of logic - such
	 * as reading the bits of output from an ALU.
	 *
	 * In such a situation, it may occasionally be useful and necessary
	 * to treat each bit individually - but more often, we want to
	 * "collect" all of the bits before we move the entire output to a
	 * new location.  Thus, while the individual bits are completing
	 * their work, the big copy operation will continually defer itself -
	 * until the *ENTIRE* move happens, all at once.
	 */
	HWC_Sim_Component todo;
	HWC_Sim_Component deferred;



	/* we need to know the length of the array of memory units, since they
	 * are the start of all computation - and also because we need to copy
	 * from the 'write' side to the 'read' side at the end of the clock
	 * cycle.
	 */
	int               memoryCount;
	HWC_Wiring_Memory *memory;

	/* we do *NOT* need to know the length of these arrays, since we never
	 * iterate through them - we simply access them from a 
	 */
	HWC_Wiring_Logic      *logic;
	HWC_Wiring_Connection *connections;
	HWC_Wiring_Assert     *asserts;
};


HWC_Sim_Graph *HWC_Sim_buildGraph(HWC_Wiring*);



#endif

