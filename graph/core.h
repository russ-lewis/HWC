#ifndef __GRAPH_CORE_H__INCLUDED__
#define __GRAPH_CORE_H__INCLUDED__



#include "wiring/core.h"

#include "graph/components.h"



typedef struct HWC_Graph HWC_Graph;
struct HWC_Graph
{
	HWC_Wiring *wiring;

	// the 'graph' wrappers for the 'wiring' components
	HWC_Graph_Component *mem;

#if 0  // do we need these for anything?
	HWC_Graph_Component *logic;
	HWC_Graph_Component *conns;
	HWC_Graph_Component *asserts;
#endif
};



HWC_Graph *HWC_Graph_build(HWC_Wiring*);

#endif

