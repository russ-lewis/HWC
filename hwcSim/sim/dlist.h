#ifndef __SIM_DLIST_H__INCLUDED__
#define __SIM_DLIST_H__INCLUDED__


#include <stdio.h>
#include <assert.h>

#include "graph/core.h"


static inline int dlist_not_empty(HWC_Graph_Component *list)
{
	return list->next != list;
}

static inline HWC_Graph_Component *dlist_remove_head(HWC_Graph_Component *list)
{
	assert(dlist_not_empty(list));

	HWC_Graph_Component *retval = list->next;

	list->next = retval->next;
	list->next->prev = list;

	retval->next = retval->prev = retval;

	return retval;
}



#endif

