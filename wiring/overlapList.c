#include <assert.h>

#include "wiring/overlapList.h"



static int wol_compare_starts(HWC_Wiring_OverlapList *a,
                              HWC_Wiring_OverlapList *b)
{
	if (a->start != b->start)
		return a->start - b->start;
	return a->end - b->end;
}

static int wol_compare_ends(HWC_Wiring_OverlapList *a,
                            HWC_Wiring_OverlapList *b)
{
	if (a->end != b->end)
		return a->end - b->end;
	return a->start - b->start;
}



void wiring_overlapList_insert(HWC_Wiring_OverlapList *list,
                               HWC_Wiring_OverlapList *listE,
                               HWC_Wiring_OverlapList *node)
{
	assert(list != NULL);

	assert(node->next  == node);
	assert(node->prev  == node);
	assert(node->nextE == node);
	assert(node->prevE == node);


	// search for the proper location for the 'start' list node.  All
	// lists have that - although only some lists will also have the
	// 'end' node.

	HWC_Wiring_OverlapList *cur = list;
	while (cur->next != list && wol_compare_starts(cur->next, node) > 0)
		cur = cur->next;

	// we've found the proper location for the 'start' node.  Add it
	// here.
	node->next = cur->next;
	node->prev = cur;

	node->next->prev = node;
	cur       ->next = node;


	// if the 2nd list is non-NULL, then do the exact same thing again,
	// on that list - except that we compare the *ends*
	if (listE != NULL)
	{
		cur = listE;
		while (cur->nextE != listE && wol_compare_ends(cur->nextE, node) > 0)
			cur = cur->nextE;

		node->nextE = cur->nextE;
		node->prevE = cur;

		node->nextE->prevE = node;
		cur        ->nextE = node;
	}
}


