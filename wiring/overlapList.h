#ifndef __WIRING_OVERLAP_LIST_H__INCLUDED__
#define __WIRING_OVERLAP_LIST_H__INCLUDED__


/* OVERLAP LIST
 *
 * The "overlap list" is a representation of the edges in the graph.
 *
 * Generally, the graph is made up of nodes, which represent components in
 * the wiring diagram, and edges, which represent the dependencies between
 * them.  More specifically, the edge includes an edge from X to Y if the
 * component X writes to a range of bits which overlaps at last one bit from
 * at least one of the inputs of Y.
 *
 * There are (conceptually) two edge lists for each wiring diagram - although
 * the simulator only uses one of them.  One edge list represents all of the
 * input ranges, and is useful for traversing *forward* through edges (from
 * components that write, to components that read).  The other, which
 * represents all of the output ranges, is useful for traversing *backward*
 * through edges (from components that read, to the writers that connect to
 * them).  Each list can also be used to perform global searches of the
 * bit space (such as looking for any "dead" bits - meaning bits that are
 * either not read, not written, or both).
 *
 * Both lists are always sorted by the *start* of each range, with the end of
 * each range being a secondary key.  (Sometimes, ranges will be identical -
 * in that case, the ordering between the identical ranges is undefined.)
 *
 * While components with similar ranges tend to have similar edges, it is
 * not as simple as just saying, "all ranges starting at this point in the
 * list represent edges from X in the graph."  Instead, you must perform a
 * linear search through the list, finding the subset of ranges in the list
 * which overlap with the bits you are interested in.  While this is a
 * linear search, it should be fairly quick in most cases, since the search
 * can skip over large sections of the list.
 *
 * To facilitate this, each component has pointers into the list, which it
 * maintains throughout the analysis or simulation; each pointer represents,
 * for an input or output range, the *first* element in the appropriate list
 * which overlaps this range.  (Output ranges point to elements in the
 * input list; input ranges point to elements in the output list.  But
 * remember that the simulator doesn't use the output list, so these pointers
 * are NULL in that case.)
 *
 * To search through the list, we specify the starting node (as in the
 * previous paragraph), and the actual range we want to inspect.  We iterate
 * through the list until the *start* of the current node (inclusive) is
 * >= the end (exclusive) of the range we're searching.  (The search can end
 * there because we know, by the ordering guarantees, that none of the
 * components listed in the rest of the list can start any earlier.)
 */



#include "wiring/core.h"



typedef struct HWC_Wiring_OverlapList HWC_Wiring_OverlapList;

struct HWC_Wiring_OverlapList
{
	// the overlap list(s) are doubly-linked, circular lists.
	//
	// each struct can actually be part of *2* lists, which is why
	// we have duplicates of the next/prev links.  The E links are
	// used for the "end of range" list; the unadorned links are
	// used for the primary (start of range) list.
	HWC_Wiring_OverlapList *prev, *next;
	HWC_Wiring_OverlapList *prevE,*nextE;

	// what is the range of bits covered by this access?
	int start;  // inclusive
	int end;    // exclusive

	// what is the component that performs the access?  Exactly one
	// of these bits will be non-NULL.
	HWC_Wiring_Memory     *mem;
	HWC_Wiring_Logic      *logc;
	HWC_Wiring_Connection *conn;
	HWC_Wiring_Assert     *asrt;
};



void wiring_overlapList_insert(HWC_Wiring_OverlapList *list,
                               HWC_Wiring_OverlapList *listE,    // can be NULL
                               HWC_Wiring_OverlapList *newNode);


#endif

