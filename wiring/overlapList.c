#include <assert.h>

#include "wiring/overlapList.h"



int wiring_overlapList_compare(HWC_Wiring_OverlapList *a,
                               HWC_Wiring_OverlapList *b)
{
	if (a->start != b->start)
		return a->start - b->start;
	return a->end - b->end;
}



void wiring_overlapList_insert(HWC_Wiring_OverlapList *list,
                               HWC_Wiring_OverlapList *newNode)
{
	assert(newNode->next == newNode);
	assert(newNode->prev == newNode);

	HWC_Wiring_OverlapList *cur = list;
	while (cur->next != list && wol_compare(list->next, newNode) > 0)
	{
		cur = cur->next;
	}

	newNode->next = cur->next;
	newNode->prev = cur;

	newNode->next->prev = newNode;
	cur          ->next = newNode;
}


