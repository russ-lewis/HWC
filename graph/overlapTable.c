#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#include "graph/overlapTable.h"



static int sort_helper(const void *a_void, const void *b_void)
{
	const HWC_Graph_OverlapRange *a = a_void;
	const HWC_Graph_OverlapRange *b = b_void;

	if (a->start != b->start)
		return a->start - b->start;
	return a->end - b->end;
}

void HWC_Graph_sortOverlapRanges(HWC_Graph_OverlapRange *arr, int count)
{
	qsort(arr, count, sizeof(arr[0]), sort_helper);
}

