#include <stdio.h>
#include <assert.h>

#include "graph/overlapTable.h"
#include "sim/state.h"
#include "sim/dlist.h"

#include "sim/notify.h"



// HACK!  Get rid of this global!
extern HWC_Sim_State *sim_global;



void HWC_Sim_notify(HWC_Graph_OverlapRange *searchStart,
                    int indx,int len)
{
	HWC_Graph_OverlapRange *cur = searchStart;

	while (cur->start != -1 &&
	       cur->start < indx+len)
	{
		HWC_Graph_Component *comp = cur->comp;

		// TODO: FIXME: global variables are evil!
		HWC_Sim_State *sim = sim_global;

		dlist_remove_if_on_a_list(comp);

		// TODO: add support for the FIFO strategy as well.  This
		//       line hard-codes the LIFO (that is, stack) stategy.
		dlist_add_head(&sim->todo, comp);

		cur++;
	}
}

