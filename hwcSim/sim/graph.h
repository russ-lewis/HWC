#ifndef __SIM_GRAPH_C__INCLUDED__
#define __SIM_GRAPH_C__INCLUDED__


#include <wiring/core.h>



/* THE GRAPH DATA STRUCTURE
 *
 * The graph is really made up of *two* different but interlocked data
 * structures: the bit storage, and the graph of interrelated components
 * which are reading and writing the various bits.
 *
 * BIT STORAGE
 *
 * For the bits, we want to store complex state (more than just 0/1), but we
 * don't want to pay the runtime cost of having large, heavyweight types for
 * each of them (especially since we expect large blocks of bits to be
 * treated as busses, and thus have the same state at all times).
 *
 * For that reason, we will have a multi-layered bit storage.  The base
 * storage is a simple array, which will have exactly one bit of physical
 * storage for every bit of simulated storage.  We will initialize this to
 * all zeroes (except for the 'read' side of memory units) at the beginning of
 * every clock cycle.
 *
 * Above that, we will have a doubly-linked list of structures, which tell us
 * how to *intepret* the bits below.  Each entry in the list will cover a
 * contiguous range of bits in the space; they will be adjoining but not
 * overlapping, and cover the entire space at all times.  As bits change
 * state, we will split, join, and update these various objects.
 *
 * We will *NOT* have a tree which allows us to search this list; instead, we
 * will assume that the graph nodes have pointers *into* this data structure,
 * which point to individual nodes; we will search laterally when necessary,
 * but will not ever have to search far - so we don't need to worry about the
 * theoretical O(n) cost of searching, the practical cost will be O(1) or
 * close to it.
 *
 * BIT STORAGE - AVAILABLE STATES
 *
 * Bits can be in the following states:
 *
 *     SET - this range of bits has their final state.  (This is the only
 *           state where it's legal to read the actual bits from the lower
 *           level.)
 *
 *     FLOATING - init state of all bits except the 'read' side of memory.
 *                The value of this bit is unclear.
 *
 *     UNDEFINED - the bit has taken a specific value, but its value is
 *                 undetermined.  This state is only used at the *END* of
 *                 a clock cycle, for error checking.  UNDEFINED bits are
 *                 legal in isolation, but may lead to bugs due to potential
 *                 short circuits or undefined behavior.
 *
 *                 UNDEFINED is set, at the end of the clock cycle, when:
 *                   - A logical component cannot determine the value of the
 *                     output bit; the output bit is set to UNDEFINED
 *                   - A conditional connection cannot decide whether or not
 *                     to make the connection; the left side of the connection
 *                     is set to UNDEFINED
 *                   - A connection is made, and the right side is UNDEFINED
 *
 *     MERGED - this is not a bit state, it's a transient state of the data
 *              structure, indicating that this node is no longer on the list.
 *              See below for details.
 *
 * END-OF-CYCLE ERROR CHECKING
 *
 * TODO: what do we set to UNDEFINED first?  Remember that flags are actually
 *       *hoping* to be in the FLOATING state (which would trigger a value of
 *       0 being written to the read side).  Should we count how many incoming
 *       connections to a flag are still pending - and drive the 0 as soon as
 *       the last one arrives?  Should we turn any 'flag' into a giant OR gate
 *       inside the compiler, so that it doesn't have to be here?
 *
 * BIT STATE REFCOUNTING
 *
 * The list of bit states includes a refcount on every element of the list.
 * This is important because we want to be able to merge nodes together, but
 * we have lots of internal pointers into the list - and we don't want to have
 * to manage backpointers.  Thus, when we split a list node, we will always
 * keep the old node intact, and simply *insert* a new node after it in the
 * list; we will update the stated range of a node, but will not try to alter
 * any pointers into it (except for the one that we have for ourselves).
 *
 * Likewise, if we change the state of a node and we would have the chance to
 * merge the node with another, we will *NOT* simply delete one of the nodes
 * (unless the refcount says that it has no references).  Instead, we will
 * remove the node from the list, but keep it around; we will change its
 * state to MERGED, and zero out all other fields, except for the 'prev' link,
 * which will point to the new, merged node.  Thus, when we try to read a
 * node, we will first check to see if it is MERGED; if it is, then we will
 * update our pointer to point to the other node, decrement the refcount, and
 * (if the refcount goes to 0) free the old node.  Note that this
 * MERGED-cleanup could be chained arbitrarily deep!  Also note that the note
 * that we eventually find might not contain the range we want; it is possible
 * that we merged two ranges, and later had to split them when their states
 * diverged again!
 *
 *      NOTE: A node in the MERGED state must count as a reference to the
 *            new node - entirely independent of any graph node which might
 *            or might not (yet) know about the new node!
 *
 * Of course, since we are splitting list nodes without updating all of the
 * graph nodes which point to them, which means that often, when we try to use
 * a pointer, it will not point to the correct node anymore.  This might be
 * because the node is now in the MERGED state; or it may be because the node
 * has been split.  Thus, the first step of any "use" of the pointer is to
 * update it; we'll provide a helper function for that.  The helper function
 * will traverse from the starting node to the current node for a given bit
 * index, updating refcounts as we go.
 *
 * HOW THE GRAPH WORKS
 *
 * Each node in the graph represents a component in the wiring diagram; most
 * of them have input (max, two ranges) and output (max, a single range).
 * We represent each of these in two ways: pointers to the current list node
 * for the bits (see above), and pointers to other graph nodes (for expressing
 * dependencies).
 *
 * The pointers to the bit list nodes are pretty easy; our data structure has
 * three different pointers, two for input, one for output.  We can use the
 * list-traversal code we've described above to keep these pointers pointing
 * at the correct list node for each of the three fields, and we can then use
 * those nodes to determine the state of the inputs and outputs.
 *
 *     TODO: we need a set of 'done' flags (one per bit) to indicate whether
 *           we've already used a given component to set a given bit.  Or
 *           can we find a better solution, which is less space-heavy???
 *           (Without this, how could we tell the difference between short
 *           circuits and simply having multiple looks at the same component?)
 *           (One solution would be a per-component 'done' flag, but then it
 *           would be impossible to set only certain bits.  Maybe a bitmask???)
 *
 * However, the pointers between the nodes are harder, because the relationship
 * is many-to-many.  A single bit, written by a component, may have multiple
 * readers; and a bit field, viewed by a component as a large range, may be
 * written to (in small pieces) by many different smaller components; finally,
 * a bit may be the write-side of a plurality of conditional connections, any
 * of which *might* write the value (even if only one of them writes it per
 * clock cycle).
 *
 * Moreover, even though the input range(s) for each component are continugous
 * ranges (though not necessarily contiguous with each other), the fact that
 * some readers (or writers) may access a subset of the range makes things hard.
 *
 * One option, of course, would be to have a linked list, rooted at each
 * component, indicating what other components might be affected by a write by
 * the current component.  However, this is undesirable because it requires a
 * lot of memory allocation; it also would be tricky to build this list of
 * "attention" objects without having an array of these lists, as large as the
 * bit space, to start with.
 *
 * Our solution is to have another linked list.  Unlike the bit-state linked
 * list, this is a *static* list, and thus is singly-linked.  Each node in
 * this list contains a 'next' field, range information, and a pointer to an
 * affected component.  The list is sorted by the range information: first, by
 * the *start* of a range, and second, by its length (both ascending).
 *
 * We build the notification list at runtime, by scanning through all
 * components and adding an entry for each input range.  (If a component has
 * two inputs but they are adjacent, then a single list node, covering both,
 * is sufficient.)  Then, we perform a second pass, and we look up the proper
 * node for each output; the component gets a pointer to the *first* entry
 * which overlaps with the output range.
 *
 * During the clock cycle, when a component updates the state of any bit in
 * its range, it calls a helper function to notify other components that might
 * read that bit, passing the helper function both the range of bits modified,
 * and the pointer to the proper node in the notification list.  The helper
 * will scan through the list, notifying each component that is affected; it
 * stops when the 'start' field of the current node is beyond the end of the
 * modified range.  We don't have to worry about there being some very-huge
 * range, starting far back in the list, because of how we built the list in
 * the first place; we know that no nodes earlier in the list are interesting.
 *
 * To "notify" a component of a change, we add it to a list of pending
 * updates; this requires that every component have a 'next' pointer in the
 * data structure.  If the simulator is configured for LIFO operation, then it
 * adds the newly-notified component at the head of the list; if FIFO, then it
 * adds it at the tail.  (It always removes nodes from the head.)
 *
 * To prevent double-insertion into the list, each component has an 'onList'
 * flag; if this is set, it will not be added to the notify list.  Likewise,
 * each component has a 'done' flag; if set, it will not be added every again
 * (during this clock cycle).
 *
 * COMPONENT TYPES
 *
 * We use a single data structure, HWC_Sim_Component, to represent all
 * components, since most components have a set of very common features.  We
 * use an emum to distinguish the type; this only affects how the component
 * responds to updated inputs.
 */



typedef struct HWC_Sim_Graph        HWC_Sim_Graph;
typedef struct HWC_Sim_BitStateNode HWC_Sim_BitStateNode;
typedef struct HWC_Sim_Component    HWC_Sim_Component;
typedef struct HWC_Sim_NotifyNode   HWC_Sim_NotifyNode;

struct HWC_Sim_Graph
{
	/* how many bits in the total simulation?  This is useful because we
	 * want to remap the 'bits' array below, after each clock cycle.
	 */
	int  numBits;

	/* one bit for each bit in the simulation. */
	char *bits;

	/* doubly linked list, length grows and shrinks as the clock cycle
	 * progresses.  This is the node which represents the range which
	 * begins at bit 0.  It is *NOT* a dummy node!
	 */
	HWC_Sim_BitStateNode bitStateList;



	/* this is the current queue of components which are pending
	 * notification.  We always pull from the head.  In LIFO mode, we
	 * always add at the head, and ignore the tail pointer.  In FIFO
	 * mode, we add at the tail.
	 *
	 * In LIFO mode, tail is always NULL.  In either mode, the head
	 * is NULL iff the list is empty.
	 */
	HWC_Sim_Component *notifyList_head;
	HWC_Sim_Component *notifyList_tail;



	/* a linked list of notification structs; each maps a range to a
	 * component that reads it.  The various components have pointers
	 * into the middle of this list, indicating where they should start
	 * the 'notification search'.
	 *
	 * This list is static once built.
	 */
	HWC_Sim_NotifyNode *notifyTable;



	/* all of the various components are stored in arrays - although, for
	 * almost all code, we will access them through a network of pointers
	 * to individual elements.
	 *
	 * However, the arrays are useful in that they make it possible to
	 * iterate through the components of a given type.
	 */
TODO: do we store the pointers to the wiring objects, poitners to the HWC_Sim_Component, or something else???



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


HWC_Sim_Graph *HWC_Sim_buildGraph(HWC_Wiring*);


#endif

