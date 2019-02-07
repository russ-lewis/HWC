#ifndef __GRAPH_CORE_H__INCLUDED__
#define __GRAPH_CORE_H__INCLUDED__



#include "wiring/core.h"

#include "graph/components.h"
#include "graph/overlapTable.h"



typedef struct HWC_Graph HWC_Graph;
struct HWC_Graph
{
	HWC_Wiring *wiring;

	HWC_Graph_OverlapRange    *overlapTable;
	HWC_Graph_OverlapRange *revOverlapTable;


	// the 'graph' wrappers for the 'wiring' components
	HWC_Graph_Component *mem;
	HWC_Graph_Component *logic;
	HWC_Graph_Component *conns;
	HWC_Graph_Component *asserts;
};



HWC_Graph *HWC_Graph_build(HWC_Wiring*);

#endif

