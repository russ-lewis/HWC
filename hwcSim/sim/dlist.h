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



static inline void dlist_remove_if_on_a_list(HWC_Graph_Component *node)
{
	assert((node->next == node) == (node->prev == node));

	if (node->next == node)
		return;   // NOP

	node->prev->next = node->next;
	node->next->prev = node->prev;

	node->next = node->prev = node;
}



static inline void dlist_add_head(HWC_Graph_Component *list,
                                  HWC_Graph_Component *node)
{
	assert(node->next == node && node->prev == node);

	node->prev = list;
	node->next = list->next;

	node->prev->next = node;
	node->next->prev = node;
}



#endif

