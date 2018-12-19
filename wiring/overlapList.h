#ifndef __WIRING_OVERLAP_LIST_H__INCLUDED__
#define __WIRING_OVERLAP_LIST_H__INCLUDED__


#include <assert.h>


/* OVERLAP LIST
 *
 * The "overlap list" is a critical part of both the simulation, and also any
 * dead-code elimination that we implement in the future - although they will
 * use it in slightly different ways.  The purpose of the list is to have a
 * data structure which gives us information about which bits are read and
 * written by which components, at a per-bit granularity.  But it avoids the
 * obvious (and terrible) linked-list-per-bit cost of a naive implementation.
 *
 * The list itself is a doubly-linked circular list; each node stores range
 * information (indicating which bist are used), as well as metadata which
 * indicates *how* the bits are used (read/write, as well as the component
 * involved).
 *
 * The nodes of the list are always sorted; they are sorted first by the
 * *starting* bit, and later by the *ending* bit (when the starting bits are
 * identical).
 *
 * TODO: do we want another list in parallel, which swaps the key preference,
 *       to make it efficient to to *backwards* searches???
 *
 * The simulation uses this list to figure out what components need to be
 * alerted when a bit is updated.  Each component that writes to a range of
 * bits has, along with the index into the bit array, a pointer to one of the
 * nodes in the overlap list.  This is never, a pointer to its own node  in
 * the list; instead, it is always a pointer to a node that comes *earlier* in
 * the list.  This pointer is set up before the simulation begins, and never
 * changes; it is defined to point to the *FIRST* node in the list that
 * represents a *READ* of any bit in the output range we're consiering.  In
 * other words, this node gives us the first component (perhaps of many)
 * which needs to be alerted when this component writes a value to one of its
 * bits.
 *
 * When a component actually writes one or more bits (we hope, normally, that
 * a component writes to its entire range at once, but this is not always
 * true), it scans through the list, starting at the saved node.  It continues
 * scanning until it finds a node whose range starts *AFTER* the end of the
 * range that is being written; by the definition of the sorting of the list,
 * we know that none of the nodes after this in the list can overlap the range
 * being written.
 *
 * The purpose of the scan, of course, is to find all of the components which
 * might be affected by the write; to do this, we calculate the intersection
 * of the write range with the range of each node on the list.  Sometimes, we
 * may find that the intersection is null (in which case we ignore the node
 * and move on); other times, we may find that the node is affected, and so
 * we move the node onto the simulation's TODO list.
 */



typedef struct HWC_Wiring_OverlapList HWC_Wiring_OverlapList;
struct HWC_Wiring_OverlapList
{
	// all of the nodes in the list are organized into a doubly-linked
	// circular list!
	HWC_Wiring_OverlapList *prev,*next;


	// what is the range of bits covered by this access?
	int start;  // inclusive
	int end;    // exclusive

	// is this access a read or a write operation?
	int read;   // 1-read the bits;   0-write the bits

	// what is the component that performs the access?  Exactly one
	// of these bits will be non-NULL.
	HWC_Wiring_Memory     *mem;
	HWC_Wiring_Logic      *logc;
	HWC_Wiring_Connection *conn;
	HWC_Wiring_Assert     *asrt;
};



int wiring_overlapList_compare(HWC_Wiring_OverlapList *a,
                               HWC_Wiring_OverlapList *b);

void wiring_overlapList_insert(HWC_Wiring_OverlapList *list,
                               HWC_Wiring_OverlapList *newNode);


#endif

