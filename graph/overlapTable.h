#ifndef __GRAPH_OVERLAP_TABLE_H__INCLUDED__
#define __GRAPH_OVERLAP_TABLE_H__INCLUDED__



/* OVERLAP TABLES
 *
 * The overlap tables are used to find which output ranges overlap which
 * input ranges.  The simulator only uses the "forward" table, which lists
 * all of the input ranges; this is useful for determining which component(s)
 * need to be alerted when we write to an output range.  Static analysis
 * tools will (in the future) also make use of a "backward" table, which
 * lists all of the output ranges.
 *
 * Each element in the table has three fields:
 *   start of range
 *   end of range
 *   pointer to the component that uses this range
 *
 * The tables are always sorted first by the start of range, and second by the
 * end of range.  If two entries have identical ranges, their ordering is
 * undefined.
 */


#include "graph/components.h"



typedef struct HWC_Graph_OverlapRange HWC_Graph_OverlapRange;
struct HWC_Graph_OverlapRange
{
	int start;  // inclusive
	int end;    // exclusive

	HWC_Graph_Component *comp;
};



void HWC_Graph_sortOverlapRanges(HWC_Graph_OverlapRange*, int count);

#endif

