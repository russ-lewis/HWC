#include <stdio.h>
#include <assert.h>

#include "core.h"
#include "write.h"


int wiring_write(HWC_Wiring *core)
{
	int i;

	printf("TODO: %s: Add parameters to allow the user to control the output filename.\n",
	       __func__);

	FILE *fp = fopen("compile.wire", "w");
	if (fp == NULL)
	{
		perror("Could not open the file to write the wiring diagram");
		return 1;
	}

	/* we use a goto-to-leave strategy, so we need a variable to hold
	 * the value that we plan to return.
	 */
	int retval = 0;


	/* a little header, to make things obvious for a user.  It also
	 * supposes that we might, in the future, be well-known enough to
	 * be supported by 'file.'  Is that arrogant?
	 */
	fprintf(fp, "# HWC Wiring Diagram\n");

	/* support for future versions, just in case */
	fprintf(fp, "version: 1.0\n");
	fprintf(fp, "\n");

	/* TODO: put the file name here */
	fprintf(fp, "debug=\"\"\n");
	fprintf(fp, "\n");

	fprintf(fp, "bits %d\n", core->numBits);
	fprintf(fp, "\n");

	fprintf(fp, "memory count %d\n", core->numMemRanges);
	for (i=0; i<core->numMemRanges; i++)
	{
		fprintf(fp, "  memory size %d read %d write %d\n",
		            core->mem[i].size,
		            core->mem[i].read, core->mem[i].write);
	}
	fprintf(fp, "\n");

	fprintf(fp, "logic count %d\n", core->numLogicalOperators);
	for (i=0; i<core->numLogicalOperators; i++)
	{
assert(0); // TODO
		fprintf(fp, "  logic AND size %d a %d b %d out %d\n",
		            1,2,3,4);
	}
	fprintf(fp, "\n");

	
	fprintf(fp, "connection count %d\n", core->numConnections);
	for (i=0; i<core->numConnections; i++)
	{
		fprintf(fp, "  connection ");

		// if(conditional)
		//	fprintf(fp , "(condition %d) ");

		// if(undirected)
		//	fprintf(fp , "(undirected) ");

		fprintf(fp, "size %d to %d from %d\n",
		            core->conns[i].size,
		            core->conns[i].to, core->conns[i].from);
	}
	fprintf(fp, "\n");


OUT:
	fclose(fp);
	return retval;
}

