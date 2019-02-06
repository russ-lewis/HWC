#include <stdio.h>
#include <assert.h>
#include <stdlib.h>

#include "graph/core.h"



HWC_Graph *HWC_Graph_build(HWC_Wiring *wiring)
{
	HWC_Graph *retval = malloc(sizeof(HWC_Graph));
	if (retval == NULL)
		return NULL;

	retval->wiring = wiring;

	printf("FIXME: Implement more!  %s() at %s:%d\n", __func__, __FILE__,__LINE__);

	return retval;
}

