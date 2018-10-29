#include <stdio.h>
#include <assert.h>

#include "core.h"
#include "write.h"


int wiring_write(HWC_Wiring *core)
{
	int i;

	printf("TODO: %s: Add parameters to allow the user to control the output filename.\n",
	       __func__);

	FILE *fp = fopen("out.wire", "w");
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
		char *name;
		int binary = 1; // default value; changed by NOT

		// why use this switch instead of a lookup table?  For
		// better sanity-checking that the values line up.  Maybe
		// we'll optimize for performance later???
		switch(core->logic[i].type)
		{
		default:
			assert(0);   // TODO: unsupported type

		case WIRING_AND: name = "AND"; break;
		case WIRING_OR : name = "OR "; break;
		case WIRING_XOR: name = "XOR"; break;
		case WIRING_NOT: name = "NOT"; binary = 0; break;
		case WIRING_EQ : name = "EQ "; break;
		case WIRING_NEQ: name = "NEQ"; break;
		}

		fprintf(fp, "  logic %s size %d a %d",
		            name,
		            core->logic[i].size,
		            core->logic[i].a);

		if (binary)
			fprintf(fp, " b %d", core->logic[i].b);

		fprintf(fp, " out %d\n", core->logic[i].out);
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

