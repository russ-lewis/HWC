#include <stdio.h>
#include <assert.h>

#include "core.h"
#include "write.h"


int wiring_write(HWC_Wiring *core)
{
	printf("TODO: %s: Add parameters to allow the user to control the output filename.\n",
	       __func__);

	FILE *fp = fopen("compile.wire", "w");
	if (fp == NULL)
	{
		perror("Could not open the file to write the wiring diagram");
		return 1;
	}

assert(0); // TODO


	return 0;
}

