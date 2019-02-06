#include <stdio.h>
#include <assert.h>

#include "graph/overlapTable.h"

#include "sim/notify.h"



void HWC_Sim_notify(HWC_Graph_OverlapRange *searchStart,
                    int indx,int len)
{
	HWC_Graph_OverlapRange *cur = searchStart;

	while (cur->start != -1 &&
	       cur->start < indx+len)
	{
		assert(0);

		cur++;
	}
}

