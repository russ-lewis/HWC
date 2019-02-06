#ifndef __GRAPH_CORE_H__INCLUDED__
#define __GRAPH_CORE_H__INCLUDED__



#include "wiring/core.h"

#include "graph/components.h"



typedef struct HWC_Graph HWC_Graph;
struct HWC_Graph
{
	HWC_Wiring *wiring;
};



HWC_Graph *HWC_Graph_build(HWC_Wiring*);

#endif

